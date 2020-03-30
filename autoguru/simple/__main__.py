import tabulate
import click

from ..nearestneighbors import DistanceMetric, HierarchicalNavigableSmallWorld
from ..embeddings import UniversalSentenceEncoder
from .. import AutoGuru
from .model import InMemoryQAStore


@click.group(help="Test question answering with a JSON database")
def simple() -> None:
    pass


_DEFAULT_DISTANCE_METRIC = "cosine"


@simple.command(help="Get answers for a question")
@click.argument("question", type=str)
@click.option(
    "-d",
    "--db",
    required=True,
    type=str,
    help="the path to the JSON file containing the question answering database",
)
@click.option(
    "-n",
    "--answers",
    default=1,
    help="the number of answers to return",
    show_default=True,
)
@click.option(
    "-m",
    "--metric",
    type=click.Choice([metric.value for metric in DistanceMetric]),
    default=_DEFAULT_DISTANCE_METRIC,
    help="the distance metric to use to get nearest neighbors for finding similar questions",
    show_default=True,
)
@click.option(
    "-e",
    "--encoding",
    default="UTF-8",
    help="the text encoding of the JSON database",
    show_default=True,
)
def answer(
    question: str,
    db: str,
    answers: int = 1,
    metric: str = _DEFAULT_DISTANCE_METRIC,
    encoding: str = "UTF-8",
) -> None:
    db = InMemoryQAStore.load_from_json(source=db, encoding=encoding)
    embedder = UniversalSentenceEncoder()
    metric = DistanceMetric(metric)
    nearest_neighbors = HierarchicalNavigableSmallWorld(
        vector_size=embedder.embedding_size, distance_metric=metric
    )

    ids, questions = zip(*db.get_questions())
    embeddings = embedder.embed(questions)
    nearest_neighbors.add(ids, embeddings)

    try:
        confidence = metric.distance_to_confidence
    except AttributeError:
        confidence = None

    autoguru = AutoGuru(
        qa_store=db,
        embedder=embedder,
        nearest_neighbors=nearest_neighbors,
        distance_to_confidence=confidence,
    )

    table = []
    if answers == 1:
        answer, confidence = autoguru.answer(question, answers=1)
        table.append((answer, confidence))
    else:
        for answer, confidence in autoguru.answer(question, answers=answers):
            table.append((answer, confidence))

    headers = ("Answer", "Confidence" if confidence is not None else "Distance")
    print(tabulate.tabulate(tabular_data=table, headers=headers, tablefmt="fancy_grid"))


if __name__ == "__main__":
    simple(prog_name="python -m autoguru.simple")
