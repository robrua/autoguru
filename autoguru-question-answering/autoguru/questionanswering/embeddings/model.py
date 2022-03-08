from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Union, no_type_check

import numpy as np

from autoguru.questionanswering.nearestneighbors import Metric


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: Union[str, Iterable[str]]) -> np.ndarray:
        raise NotImplementedError

    @property
    @abstractmethod
    def embedding_size(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def suggested_metrics(self) -> List[Metric]:
        raise NotImplementedError

    @no_type_check
    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> "Embedder":
        raise NotImplementedError
