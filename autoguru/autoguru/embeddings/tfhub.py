from typing import Callable, Dict, Iterable, Union

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

from autoguru.embeddings.model import Embedder


class TfHubEmbedder(Embedder):
    DEFAULT_SIGNATURE: str = "serving_default"
    COMMON_MODELS: Dict[str, str] = {
        "USE": "https://tfhub.dev/google/universal-sentence-encoder/4"
    }

    def __init__(
        self, model: Callable[[Iterable[str]], np.ndarray], embedding_size: int
    ) -> None:
        self._model: Callable[[Iterable[str]], np.ndarray] = model
        self._embedding_size: int = embedding_size

    def embed(self, text: Union[str, Iterable[str]]) -> np.ndarray:
        if isinstance(text, str):
            return tf.nn.l2_normalize(self._model([text]), axis=1)[0].numpy()
        else:
            return tf.nn.l2_normalize(self._model(text), axis=1).numpy()

    @property
    def embedding_size(self) -> int:
        return self._embedding_size

    @classmethod
    def create(cls, url: str, signature: str = DEFAULT_SIGNATURE) -> "Embedder":
        model = hub.load(url)
        embedding_size = model.signatures[signature].output_shapes["outputs"][1]
        return cls(model=model, embedding_size=embedding_size)
