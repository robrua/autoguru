from typing import Optional, Dict, List, Any, Callable
from types import ModuleType
import importlib

import click

from .autoguru import AutoGuruServer, AutoGuruClient, control_service
from . import __version__


class DynamicGroup(click.Group):
    def __init__(
        self,
        module_name: str,
        group_name: str,
        preload_hook: Optional[Callable] = None,
        name: Optional[str] = None,
        commands: Optional[Dict[str, click.Command]] = None,
        **attrs
    ) -> None:
        super(DynamicGroup, self).__init__(name=name, commands=commands, **attrs)
        self._module_name = module_name
        self._group_name = group_name
        self._preload_hook = preload_hook

    @property
    def module(self) -> ModuleType:
        try:
            return self._module
        except AttributeError:
            if self._preload_hook is not None:
                self._preload_hook()
            self._module = importlib.import_module(self._module_name)
            return self._module

    @property
    def group(self) -> click.Group:
        try:
            return self._group
        except AttributeError:
            self._group = getattr(self.module, self._group_name)
            return self._group

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command:
        return self.group.get_command(ctx, cmd_name)

    def list_commands(self, ctx: click.Context) -> List[click.Command]:
        return self.group.list_commands(ctx)

    def invoke(self, ctx: click.Context) -> Any:
        return self.group.invoke(ctx)

    def get_usage(self, ctx: click.Context) -> str:
        return self.group.get_usage(ctx)

    def get_params(self, ctx: click.Context) -> List[click.Parameter]:
        return self.group.get_params(ctx)


def _surpress_tensorflow_logging() -> None:
    import os

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    import tensorflow as tf

    tf.get_logger().setLevel("ERROR")
    tf.autograph.set_verbosity(0)


@click.group(help="Administrate AutoGuru or run related utilities")
@click.version_option(version=__version__)
def autoguru() -> None:
    pass


@autoguru.group(
    cls=DynamicGroup,
    module_name="autoguru.simple.__main__",
    group_name="simple",
    preload_hook=_surpress_tensorflow_logging,
    help="Test question answering with a JSON database",
)
def simple() -> None:
    pass


@autoguru.group(
    cls=DynamicGroup,
    module_name="autoguru.discord.__main__",
    group_name="discord",
    help="Administrate the AutoGuru Discord Bot or run related utilities",
)
def discord(context) -> None:
    pass


@autoguru.command(help="Launch the AutoGuru server")
@click.option(
    "-h",
    "--host",
    default=AutoGuruServer.DEFAULT_HOST,
    help="the hostname to bind the server to",
    show_default=True,
)
@click.option(
    "-p",
    "--port",
    default=AutoGuruServer.DEFAULT_PORT,
    help="the port to bind the server to",
    show_default=True,
)
def start(
    host: str = AutoGuruServer.DEFAULT_HOST, port: int = AutoGuruServer.DEFAULT_PORT,
) -> None:
    server = AutoGuruServer(autoguru=None, services=[control_service])
    server.run()


@autoguru.command(help="Stop the AutoGuru server")
@click.option(
    "-h",
    "--host",
    default=AutoGuruServer.DEFAULT_HOST,
    help="the hostname to bind the server to",
    show_default=True,
)
@click.option(
    "-p",
    "--port",
    default=AutoGuruServer.DEFAULT_PORT,
    help="the port to bind the server to",
    show_default=True,
)
@click.option(
    "-c",
    "--context-root",
    default="",
    help="the context root for the AutoGuruServer application",
)
def stop(
    host: str = AutoGuruServer.DEFAULT_HOST,
    port: int = AutoGuruServer.DEFAULT_PORT,
    context_root: str = "",
) -> None:
    client = AutoGuruClient(host=host, port=port, context_root=context_root)
    client.stop()


if __name__ == "__main__":
    autoguru(prog_name="autoguru")
