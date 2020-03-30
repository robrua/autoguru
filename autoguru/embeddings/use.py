from typing import Iterable, Union

import tensorflow_hub as hub
import numpy as np

from ..model import Embedder


_DEFAULT_MODEL = "https://tfhub.dev/google/universal-sentence-encoder/4"


class UniversalSentenceEncoder(Embedder):
    def __init__(self, tf_hub_url: str = _DEFAULT_MODEL) -> None:
        self._use = hub.KerasLayer(handle=tf_hub_url)

    def embed(self, text: Union[str, Iterable[str]]) -> np.ndarray:
        if isinstance(text, str):
            text = [text]
            return self._use(inputs=text)[0].numpy()
        else:
            return self._use(inputs=text).numpy()

    @property
    def embedding_size(self) -> int:
        return 512  # TODO: This is true for most USE models. Replace with dynamic check when https://github.com/tensorflow/hub/blob/4c170e7fa5f0c6c8d0c43fa170413718b16a6ace/tensorflow_hub/keras_layer.py#L244 is resolved.
