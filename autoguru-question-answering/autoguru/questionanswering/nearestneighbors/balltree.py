import pickle
from pathlib import Path
from typing import Callable, Dict, List, Union

import numpy as np
from scipy.spatial.distance import cosine
from sklearn.neighbors import BallTree as SkBallTree

from autoguru.questionanswering.nearestneighbors.metrics import Metric
from autoguru.questionanswering.nearestneighbors.model import NearestNeighbors, Neighbor

_METRICS: Dict[Metric, Callable[[np.ndarray, np.ndarray], np.floating]] = {
    Metric.COSINE: cosine
}


class BallTree(NearestNeighbors):
    DEFAULT_METRIC: Metric = Metric.COSINE
    DEFAULT_LEAF_SIZE: int = 40

    def __init__(
        self,
        index: SkBallTree,
        metric: Metric = DEFAULT_METRIC,
    ) -> None:
        self._index: SkBallTree = index
        self._similarity: Callable[[np.ndarray], np.ndarray] = metric.similarity

    def nearest_neighbors(
        self, vectors: np.ndarray, k: int = 1
    ) -> List[List[Neighbor]]:
        if vectors.ndim != 2:
            vectors = vectors.reshape((-1, self._index.data.shape[1]))

        query_distances, query_indexes = self._index.query(X=vectors, k=k)
        query_similarities = self._similarity(query_distances)
        return [
            [
                Neighbor(index=index.item(), similarity=similarity.item())
                for index, similarity in zip(indexes, similarities)
            ]
            for indexes, similarities in zip(query_indexes, query_similarities)
        ]

    def save(self, index_file: Union[str, Path]) -> None:
        if isinstance(index_file, str):
            index_file = Path(index_file)

        with index_file.open("wb") as out_file:
            pickle.dump(self, out_file)

    @classmethod
    def load(cls, index_file: Union[str, Path]) -> "BallTree":
        if isinstance(index_file, str):
            index_file = Path(index_file)

        with index_file.open("rb") as in_file:
            return pickle.load(in_file)

    @classmethod
    def create(
        cls,
        index_vectors: np.ndarray,
        metric: Metric = DEFAULT_METRIC,
        leaf_size: int = DEFAULT_LEAF_SIZE,
    ) -> "BallTree":
        return BallTree(
            index=SkBallTree(
                index_vectors, leaf_size=leaf_size, metric=_METRICS[metric]
            ),
            metric=metric,
        )
