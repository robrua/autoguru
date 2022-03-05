from enum import Enum, auto
from typing import Callable, Dict

import numpy as np


class Metric(Enum):
    ANGULAR_DISTANCE = auto()
    COSINE = auto()

    @property
    def similarity(self) -> Callable[[np.ndarray], np.ndarray]:
        return _SIMILARITY_FUNCTIONS[self]


def angular_similarity(distances: np.ndarray) -> np.ndarray:
    return 1.0 - distances


def cosine_similarity(distances: np.ndarray) -> np.ndarray:
    return 1.0 - distances


_SIMILARITY_FUNCTIONS: Dict[Metric, Callable[[np.ndarray], np.ndarray]] = {
    Metric.ANGULAR_DISTANCE: angular_similarity,
    Metric.COSINE: cosine_similarity
}
