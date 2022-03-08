import click
import uvicorn

from autoguru.webservices import __version__


@click.group(help="AutoGuru Web Services CLI Application")
@click.version_option(version=__version__)
def web_services() -> None:
    pass


@web_services.command(name="run", help="Runs the web services")
def run() -> None:
    uvicorn.run("autoguru.webservices.main:app", debug=True, reload=True)


if __name__ == "__main__":
    web_services(prog_name="autoguru-ws")
