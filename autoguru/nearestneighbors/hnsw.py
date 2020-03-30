from typing import Union, Iterable, Tuple, Callable
from pathlib import Path
from enum import Enum

import numpy as np
import hnswlib

from ..model import NearestNeighbors


class DistanceMetric(Enum):
    COSINE = "cosine"
    INNER_PRODUCT = "inner_product"
    EUCLIDEAN = "euclidean"

    @property
    def distance_to_confidence(self) -> Callable[[np.ndarray], np.ndarray]:
        try:
            return _DISTANCE_TO_CONFIDENCE[self]
        except KeyError:
            raise AttributeError(
                "No default confidence normalizer for {}".format(str(self))
            )


_DISTANCE_TO_CONFIDENCE = {DistanceMetric.COSINE: lambda distance: 1.0 - distance}


_DEFAULT_DISTANCE_METRIC = DistanceMetric.COSINE
_DEFAULT_MAX_SIZE = 10000
_DEFAULT_LINKS_PER_VECTOR = 100
_DEFAULT_INDEX_QUALITY = 200
_DEFAULT_SEARCH_LIST_SIZE = 200

_HNSWLIB_NAMES = {
    DistanceMetric.COSINE: "cosine",
    DistanceMetric.INNER_PRODUCT: "ip",
    DistanceMetric.EUCLIDEAN: "l2",
}


class HierarchicalNavigableSmallWorld(NearestNeighbors):
    def __init__(
        self,
        vector_size: int,
        distance_metric: Union[str, DistanceMetric] = _DEFAULT_DISTANCE_METRIC,
        max_size: int = _DEFAULT_MAX_SIZE,
        links_per_vector: int = _DEFAULT_LINKS_PER_VECTOR,
        index_quality: int = _DEFAULT_INDEX_QUALITY,
        search_list_size: int = _DEFAULT_SEARCH_LIST_SIZE,
    ) -> None:
        if not isinstance(distance_metric, DistanceMetric):
            distance_metric = DistanceMetric(distance_metric)

        self._index = hnswlib.Index(
            space=_HNSWLIB_NAMES[distance_metric], dim=vector_size
        )
        self._index.init_index(
            max_elements=max_size, ef_construction=index_quality, M=links_per_vector
        )
        self._index.set_ef(ef=search_list_size)

    def add(self, ids: Union[str, Iterable[str]], vectors: np.ndarray) -> None:
        if isinstance(ids, str):
            ids = [ids]
        if len(vectors.shape) == 1:
            vectors = np.reshape(a=vectors, newshape=(1,) + vectors.shape)

        # Resize to fit if needed
        if (
            self._index.get_current_count() + vectors.shape[0]
            >= self._index.get_max_elements()
        ):
            multiplier = 2
            while (
                self._index.get_max_elements() * multiplier
                < self._index.get_current_count() + vectors.shape[0]
            ):
                multiplier *= 2
            self._index.resize_index(
                new_size=self._index.get_max_elements() * multiplier
            )

        self._index.add_items(data=vectors, ids=[int(id_) for id_ in ids])

    def get_neighbors(
        self, vectors: np.ndarray, neighbors: int = 1
    ) -> Tuple[np.ndarray, np.ndarray]:
        if len(vectors.shape) == 1:
            vectors = np.reshape(a=vectors, newshape=(1,) + vectors.shape)
        return self._index.knn_query(data=vectors, k=neighbors)

    def save(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            path = Path(path)
        self._index.save_index(path_to_index=str(path.resolve()))

    @classmethod
    def load(
        cls,
        path: Union[str, Path],
        vector_size: int,
        distance_metric: Union[str, DistanceMetric] = _DEFAULT_DISTANCE_METRIC,
        search_list_size: int = _DEFAULT_SEARCH_LIST_SIZE,
    ) -> "NearestNeighbors":
        if isinstance(path, str):
            path = Path(path)

        nearest_neighbors = NearestNeighbors.__new__()
        nearest_neighbors._index = hnswlib.Index(
            space=_HNSWLIB_NAMES[distance_metric], dim=vector_size
        )
        nearest_neighbors._index.load_index(path_to_index=str(path.resolve()))
        nearest_neighbors._index.set_ef(ef=search_list_size)
