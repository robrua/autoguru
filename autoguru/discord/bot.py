from typing import Optional, Union, List
import threading
import datetime
import logging
import os

import discord

from ..autoguru import AutoGuru


_LOGGER = logging.getLogger(__name__)


class _BotClient(discord.Client):
    def __init__(self, autoguru: AutoGuru, *args, **kwargs) -> None:
        super(_BotClient, self).__init__(*args, **kwargs)
        self._autoguru = autoguru

    async def on_connect(self) -> None:
        _LOGGER.debug("{} has connected to Discord".format(self.user.name))

    async def on_disconnect(self) -> None:
        _LOGGER.debug("{} has disconnected from Discord".format(self.user.name))

    async def on_ready(self) -> None:
        _LOGGER.info("{} is ready".format(self.user.name))

    async def on_shard_ready(self, shard_id: int) -> None:
        _LOGGER.debug("{} is ready on shard #{}".format(self.user.name, shard_id))

    async def on_resumed(self) -> None:
        _LOGGER.debug("{} has resumed operation".format(self.user.name))

    async def on_error(self, event: str, *args, **kwargs) -> None:
        _LOGGER.error("{} encountered an error:".format(self.user.name), exc_info=True)

    async def on_typing(
        self,
        channel: discord.abc.Messageable,
        user: Union[discord.User, discord.Member],
        when: datetime.datetime,
    ) -> None:
        pass

    async def on_message(self, message: discord.Message) -> None:
        pass

    async def on_message_bulk_delete(self, messages: List[discord.Message]) -> None:
        pass

    async def on_message_delete(self, message: discord.Message) -> None:
        pass

    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        pass

    async def on_reaction_add(
        self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]
    ) -> None:
        pass

    async def on_reaction_remove(
        self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]
    ) -> None:
        pass

    async def on_reaction_clear(
        self, message: discord.Message, reactions: List[discord.Reaction]
    ) -> None:
        pass

    async def on_reaction_clear_emoji(self, reaction: discord.Reaction) -> None:
        pass


_TOKEN_ENVIRONMENT_VARIABLE = "DISCORD_BOT_TOKEN"


class DiscordBot(object):
    def __init__(
        self,
        autoguru: AutoGuru,
        token: Optional[str] = None,
        status: Union[str, discord.Status] = discord.Status.online,
        activity: Optional[Union[str, discord.Activity]] = None,
    ) -> None:
        if token is None:
            token = os.environ.get(_TOKEN_ENVIRONMENT_VARIABLE, None)
        if token is None:
            raise ValueError(
                "Token was not provided and {} environment variable was not set!".format(
                    _TOKEN_ENVIRONMENT_VARIABLE
                )
            )
        self._token = token

        if isinstance(status, str):
            status = discord.Status(status)
        if isinstance(activity, str):
            activity = discord.CustomActivity(activity)

        self._client = _BotClient(
            autoguru=autoguru, max_messages=None, status=status, activity=activity
        )

    def run(self) -> None:
        self._client.run(self._token)

    def start(self) -> None:
        threading.Thread(self.run).start()

    def stop(self) -> None:
        self._client.loop.stop()

    def scrape(self, server: str, channel: str) -> None:
        async def action():
            async for guild in self._client.fetch_guilds():
                print(guild.name)

        self._client.loop.call_soon_threadsafe(action)
