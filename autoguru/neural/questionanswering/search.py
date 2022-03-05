from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Type
from uuid import UUID

from autoguru.embeddings import Embedder
from autoguru.nearestneighbors import NearestNeighbors
from autoguru.persistence import Question, session


@dataclass
class SimilarQuestion:
    __slots__ = ["question", "similarity"]

    question: Question
    similarity: float


class QuestionSearchService:
    def __init__(
        self,
        embedder: Embedder,
        nearest_neighbors: Type[NearestNeighbors],
        *nearest_neighbor_args: Any,
        **nearest_neighbor_kwargs: Any,
    ) -> None:
        self._embedder: Embedder = embedder

        self._nearest_neighbors_type: Type[NearestNeighbors] = nearest_neighbors
        self._nearest_neighbor_args: Tuple[Any, ...] = nearest_neighbor_args
        self._nearest_neighbor_kwargs: Dict[str, Any] = nearest_neighbor_kwargs

        self._nearest_neighbors: NearestNeighbors
        self._question_ids: List[UUID]
        self.create_index()

    def create_index(self) -> None:
        questions = []
        self._question_ids = []

        with session():
            for question in Question.select(
                lambda question: question.answer is not None
            ):
                questions.append(question.text)
                self._question_ids.append(question.id)

        embeddings = self._embedder.embed(questions)
        self._nearest_neighbors = self._nearest_neighbors_type.create(
            embeddings, *self._nearest_neighbor_args, **self._nearest_neighbor_kwargs
        )

    def search(self, question: Question, k: int = 1) -> List[SimilarQuestion]:
        embedding = self._embedder.embed(question.text)
        neighbors = self._nearest_neighbors.nearest_neighbors(embedding, k=k)[0]

        with session():
            return [
                SimilarQuestion(
                    question=Question.get(id=self._question_ids[neighbor.index]),
                    similarity=neighbor.similarity,
                )
                for neighbor in neighbors
            ]
