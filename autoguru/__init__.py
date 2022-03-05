import pkg_resources

from . import (
    admin,
    events,
    models,
    routes,
)

__version__ = (
    pkg_resources.resource_string("autoguru", "VERSION.txt")
    .decode("UTF-8")
    .strip()
)

__all__ = ["__version__", "admin", "events", "models", "routes"]
