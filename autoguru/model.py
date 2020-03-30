from typing import Optional, Iterable, Union, Tuple
from abc import ABC, abstractmethod

import numpy as np


class QuestionAnswerStore(ABC):
    @abstractmethod
    def get_answer(self, id_: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def get_answers(self, ids: Iterable[str]) -> Iterable[Optional[str]]:
        raise NotImplementedError

    @abstractmethod
    def add_answer(self, question: str, answer: str) -> str:
        raise NotImplementedError


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: Union[str, Iterable[str]]) -> np.ndarray:
        raise NotImplementedError

    @property
    @abstractmethod
    def embedding_size(self) -> int:
        raise NotImplementedError


class NearestNeighbors(ABC):
    @abstractmethod
    def add(self, ids: Union[str, Iterable[str]], vectors: np.ndarray) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_neighbors(
        self, vectors: np.ndarray, neighbors: int = 1
    ) -> Tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError
