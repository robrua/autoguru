from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence, Union, no_type_check

import numpy as np


@dataclass
class Neighbor:
    __slots__ = ["index", "similarity"]

    index: int
    similarity: float


class NearestNeighbors(ABC):
    @abstractmethod
    def nearest_neighbors(
        self, vectors: np.ndarray, k: int = 1
    ) -> Sequence[Sequence[Neighbor]]:
        raise NotImplementedError

    @abstractmethod
    def save(self, index_file: Union[str, Path]) -> None:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def load(cls, index_file: Union[str, Path]) -> "NearestNeighbors":
        raise NotImplementedError

    @no_type_check
    @classmethod
    @abstractmethod
    def create(
        cls, index_vectors: np.ndarray, *args: Any, **kwargs: Any
    ) -> "NearestNeighbors":
        raise NotImplementedError
