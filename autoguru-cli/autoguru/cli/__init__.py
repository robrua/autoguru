import importlib
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional

import click
import pkg_resources

__version__ = (
    pkg_resources.resource_string("autoguru.cli", "VERSION.txt").decode("UTF-8").strip()
)


class DynamicGroup(click.Group):
    """
    Used to dynamically load submodule __main__.py files from to allow access from CLI tools without forcing all submodules to be imported on initialization

    Args:
        module_name (str): the name of the module that should be dynamically loaded to get the command implementation
        group_name (Optional[str]): the name of the command implementation to delegate to. If None, the command with the same name as the decorated function will be used.
        preload_hook (Optional[Callable[[], None]]): an optional function to run before loading the subgroup. This can be used for messing with logging or other things that might be triggered on load of a module.
        name (Optional[str]): the name of the command group
        commands (Optional[Dict[str, click.Command]]): commands to initialize the group with
    """

    def __init__(
        self,
        module_name: str,
        group_name: str,
        preload_hook: Optional[Callable[[], None]] = None,
        name: Optional[str] = None,
        commands: Optional[Dict[str, click.Command]] = None,
        **attrs
    ) -> None:
        super(DynamicGroup, self).__init__(name=name, commands=commands, **attrs)
        self._module_name: str = module_name
        self._group_name: str = group_name
        self._preload_hook: Optional[Callable] = preload_hook

    @property
    def module(self) -> ModuleType:
        try:
            return self._module
        except AttributeError:
            if self._preload_hook is not None:
                self._preload_hook()
            self._module: ModuleType = importlib.import_module(self._module_name)
            return self._module

    @property
    def click_group(self) -> click.Group:
        try:
            return self._group
        except AttributeError:
            self._group: click.Group = getattr(self.module, self._group_name)
            return self._group

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        return self.click_group.get_command(ctx, cmd_name)

    def list_commands(self, ctx: click.Context) -> List[str]:
        return self.click_group.list_commands(ctx)

    def invoke(self, ctx: click.Context) -> Any:
        return self.click_group.invoke(ctx)

    def get_usage(self, ctx: click.Context) -> str:
        return self.click_group.get_usage(ctx)

    def get_params(self, ctx: click.Context) -> List[click.Parameter]:
        return self.click_group.get_params(ctx)

    def get_help(self, ctx: click.Context) -> str:
        return self.click_group.get_help(ctx)


def delegate(
    group: click.Group,
    module_name: str,
    subgroup_name: Optional[str] = None,
    preload_hook: Optional[Callable] = None,
    help: Optional[str] = None,
) -> Callable:
    """
    Delegates a click command to a command implemented in another __main__.py file. The other module will be dynamically imported to avoid slow startup times or unnecessary imports.
    You can just use `pass` as the implementation of the delegating command.

    This should be used as a decorator. For example:

    @delegate(
        parent_command,
        "othermodule.__main__",
        help="Since the module is dynamically loaded we have to replicate a help message",
    )
    def child_command() -> None:
        pass

    Args:
        group (click.Group): the parent command group this command should be a part of
        module_name (str): the name of the module that should be dynamically loaded to get the command implementation
        subgroup_name (Optional[str]): the name of the command implementation to delegate to. If None, the command with the same name as the decorated function will be used.
        preload_hook (Optional[str]): an optional function to run before loading the subgroup. This can be used for messing with logging or other things that might be triggered on load of a module.
        help (Optional[str]): the help message to show in the parent command group's help menu. This unfortunately can't be taken from the delegate command while dynamically loading.

    Returns:
        The delegating decorator that wraps a command for dynamic dispatch
    """

    def decorator(
        function: Callable[[], None],
    ) -> Callable[[], None]:
        return group.group(
            cls=DynamicGroup,
            module_name=module_name,
            group_name=subgroup_name
            if subgroup_name is not None
            else function.__name__,
            preload_hook=preload_hook,
            help=help,
        )(function)

    return decorator


__all__ = ["__version__", "delegate"]
