import click

from autoguru.cli import __version__, delegate


@click.group(help="AutoGuru CLI Application")
@click.version_option(version=__version__)
def autoguru() -> None:
    pass


@delegate(
    group=autoguru,
    module_name="autoguru.questionanswering.__main__",
    subgroup_name="question_answering",
    help="Question Answering",
)
def qa() -> None:
    pass


@delegate(
    group=autoguru,
    module_name="autoguru.webservices.__main__",
    subgroup_name="web_services",
    help="Web Services",
)
def ws() -> None:
    pass


@delegate(
    group=autoguru,
    module_name="autoguru.discord.__main__",
    help="Discord Bot",
)
def discord() -> None:
    pass


if __name__ == "__main__":
    autoguru(prog_name="autoguru")
