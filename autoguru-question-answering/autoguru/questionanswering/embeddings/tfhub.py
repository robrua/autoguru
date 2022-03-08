from typing import Callable, Dict, Iterable, List, NamedTuple, Union

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

from autoguru.questionanswering.embeddings.model import Embedder
from autoguru.questionanswering.nearestneighbors import Metric


class ModelDetails(NamedTuple):
    url: str
    suggested_metrics: List[Metric]


class TfHubEmbedder(Embedder):
    DEFAULT_SIGNATURE: str = "serving_default"
    COMMON_MODELS: Dict[str, ModelDetails] = {
        "USE_D": ModelDetails(
            url="https://tfhub.dev/google/universal-sentence-encoder/4",
            suggested_metrics=[Metric.ANGULAR_DISTANCE, Metric.COSINE],
        ),
        "USE_T": ModelDetails(
            url="https://tfhub.dev/google/universal-sentence-encoder-large/5",
            suggested_metrics=[Metric.ANGULAR_DISTANCE, Metric.COSINE],
        ),
    }

    def __init__(
        self,
        model: Callable[[Iterable[str]], tf.Tensor],
        embedding_size: int,
        suggested_metrics: List[Metric] = None,
    ) -> None:
        self._model: Callable[[Iterable[str]], tf.Tensor] = model
        self._embedding_size: int = embedding_size
        self._suggested_metrics: List[Metric] = (
            suggested_metrics if suggested_metrics is not None else []
        )

    def embed(self, text: Union[str, Iterable[str]]) -> np.ndarray:
        if isinstance(text, str):
            return self._model([text])[0].numpy()
        else:
            return self._model(text).numpy()

    @property
    def embedding_size(self) -> int:
        return self._embedding_size

    @property
    def suggested_metrics(self) -> List[Metric]:
        return self._suggested_metrics

    @classmethod
    def create(
        cls,
        url: str,
        signature: str = DEFAULT_SIGNATURE,
        suggested_metrics: List[Metric] = None,
    ) -> "Embedder":
        model = hub.load(url)
        embedding_size = model.signatures[signature].output_shapes["outputs"][1]
        return cls(
            model=model,
            embedding_size=embedding_size,
            suggested_metrics=suggested_metrics,
        )
