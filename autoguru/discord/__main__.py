from typing import Optional, Callable, Any
import threading

import rpyc
import click
import logging
import discord as discord_py

from .bot import DiscordBot


@click.group(help="Administrate the AutoGuru Discord Bot")
def discord() -> None:
    pass


_DEFAULT_STATUS = "online"
_DEFAULT_LOG_LEVEL = "info"
_DEFAULT_PORT = 60120
_LOG_LEVELS = ["critical", "error", "warning", "info", "debug", "notset"]
_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class _BotService(rpyc.Service):
    def __init__(self, bot: DiscordBot) -> None:
        self._bot = bot

    def exposed_stop(self) -> None:
        self._bot.stop()


def _then_call(after: Callable, call: Callable) -> Callable:
    def wrapped() -> Any:
        result = after()
        call()
        return result

    return wrapped


@discord.command(help="Runs the AutoGuru Discord Bot")
@click.option(
    "-t",
    "--token",
    default=None,
    type=str,
    help="the token for the Discord bot to log into",
)
@click.option(
    "-s",
    "--status",
    type=click.Choice([status.value for status in discord_py.Status]),
    default=_DEFAULT_STATUS,
    help="the discord status to set on login",
    show_default=True,
)
@click.option(
    "-a",
    "--activity",
    default=None,
    type=str,
    help="the discord activity to set on login",
)
@click.option(
    "-d/-f",
    "--daemon/--foreground",
    default=False,
    help="start the bot as a daemon service which can be connected to to run further commands",
)
@click.option(
    "-p",
    "--port",
    default=_DEFAULT_PORT,
    help="the port to run the daemon service on if running as daemon",
    show_default=True,
)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(_LOG_LEVELS),
    default=_DEFAULT_LOG_LEVEL,
    help="the severity level to show logs for in console",
    show_default=True,
)
def run(
    token: Optional[str] = None,
    status: str = _DEFAULT_STATUS,
    activity: Optional[str] = None,
    daemon: bool = False,
    port: int = _DEFAULT_PORT,
    log_level: str = _DEFAULT_LOG_LEVEL,
) -> None:
    logging.basicConfig(level=getattr(logging, log_level.upper()), format=_LOG_FORMAT)
    bot = DiscordBot(autoguru=None, token=token, status=status, activity=activity)
    if daemon:
        service = _BotService(bot=bot)
        server = rpyc.utils.server.ThreadPoolServer(
            service=service, hostname="localhost", port=port, nbThreads=1
        )
        service.exposed_stop = _then_call(service.exposed_stop, server.close)
        threading.Thread(server.start()).start()

    bot.run()


@discord.command(help="Stop the AutoGuru Discord Bot daemon")
def stop(port: int = _DEFAULT_PORT) -> None:
    with rpyc.connect("localhost", port) as connection:
        bot = connection.root
        bot.stop()


if __name__ == "__main__":
    discord(prog_name="python -m autoguru.discord")
