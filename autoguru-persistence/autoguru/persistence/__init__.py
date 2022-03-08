import pkg_resources

from autoguru.persistence.model import Answer, Question

__version__ = (
    pkg_resources.resource_string("autoguru.persistence", "VERSION.txt")
    .decode("UTF-8")
    .strip()
)


__all__ = ["__version__", "Question", "Answer"]
