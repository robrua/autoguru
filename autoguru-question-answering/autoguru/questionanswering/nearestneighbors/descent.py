import pickle
from pathlib import Path
from typing import Callable, Dict, List, Union

import numpy as np
from pynndescent import NNDescent

from autoguru.questionanswering.nearestneighbors.metrics import Metric
from autoguru.questionanswering.nearestneighbors.model import NearestNeighbors, Neighbor

_METRIC_NAMES: Dict[Metric, str] = {Metric.COSINE: "cosine"}


class Descent(NearestNeighbors):
    DEFAULT_METRIC: Metric = Metric.COSINE
    DEFAULT_EPSILON: float = 0.1
    DEFAULT_NEIGHBORS: int = 30
    DEFAULT_DIVERSIFY_PROBABILITY: float = 1.0
    DEFAULT_PRUNING_DEGREE_MULTIPLIER: float = 1.5

    def __init__(
        self,
        index: NNDescent,
        metric: Metric = DEFAULT_METRIC,
        epsilon: float = DEFAULT_EPSILON,
    ) -> None:
        self._index: NNDescent = index
        self._similarity: Callable[[np.ndarray], np.ndarray] = metric.similarity
        self._epsilon: float = epsilon

    def nearest_neighbors(
        self, vectors: np.ndarray, k: int = 1
    ) -> List[List[Neighbor]]:
        if vectors.ndim != 2:
            vectors = vectors.reshape((-1, self._index.dim))

        query_indexes, query_distances = self._index.query(
            query_data=vectors, k=k, epsilon=self._epsilon
        )
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
    def load(cls, index_file: Union[str, Path]) -> "Descent":
        if isinstance(index_file, str):
            index_file = Path(index_file)

        with index_file.open("rb") as in_file:
            return pickle.load(in_file)

    @classmethod
    def create(
        cls,
        index_vectors: np.ndarray,
        metric: Metric = DEFAULT_METRIC,
        epsilon: float = DEFAULT_EPSILON,
        neighbors: int = DEFAULT_NEIGHBORS,
        diversify_probability: float = DEFAULT_DIVERSIFY_PROBABILITY,
        pruning_degree_multiplier: float = DEFAULT_PRUNING_DEGREE_MULTIPLIER,
    ) -> "Descent":
        index = NNDescent(
            data=index_vectors,
            metric=_METRIC_NAMES[metric],
            n_neighbors=neighbors,
            diversify_prob=diversify_probability,
            pruning_degree_multiplier=pruning_degree_multiplier,
        )
        index.prepare()
        return Descent(
            index=index,
            epsilon=epsilon,
        )
