import pkg_resources

from .autoguru import AutoGuru
from .model import QuestionAnswerStore, Embedder, NearestNeighbors


__version__ = (
    pkg_resources.resource_string("autoguru", "VERSION.txt").decode("UTF-8").strip()
)


# TODO: Cleanup
# TODO: Add run discord bot
# TODO: Make daemon
# TODO: Bot Implementation
# TODO: Mongo Database for Discord Bot
# TODO: Scraping Discord
# TODO: Fine-tune Model
# TODO: Save/Load full system
# TODO: PyPi package


__all__ = [
    "__version__",
    "AutoGuru",
    "QuestionAnswerStore",
    "Embedder",
    "NearestNeighbors",
]
