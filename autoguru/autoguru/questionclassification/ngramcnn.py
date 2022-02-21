from typing import Any, Iterable, List, Union

import tensorflow as tf
from tensorflow.python.keras import Model
from tensorflow.python.keras.layers import (
    Concatenate,
    Conv1D,
    Dense,
    Dropout,
    GlobalMaxPool1D,
    Softmax,
)

from autoguru.questionclassification.model import (
    QuestionClass,
    QuestionClassification,
    QuestionClassifier,
)


class ConvolutionalNGrams(QuestionClassifier):
    def classify(
        self, questions: Union[str, Iterable[str]], k: int = 1
    ) -> List[List[QuestionClassification]]:
        raise NotImplementedError

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> "QuestionClassifier":
        raise NotImplementedError


# Based on https://arxiv.org/pdf/2001.00571.pdf
class NGramCnn(Model):
    DEFAULT_KERNEL_SIZES: List[int] = [3, 4, 5]
    DEFAULT_FILTERS: int = 100
    DEFAULT_DROPOUT_RATE: float = 0.5
    DEFAULT_DENSE_LAYERS: int = 1
    DEFAULT_ACTIVATION: str = "relu"
    DEFAULT_CLASSES: int = len(QuestionClass)

    def __init__(
        self,
        kernel_sizes: List[int] = None,
        filters: int = DEFAULT_FILTERS,
        dropout_rate: float = DEFAULT_DROPOUT_RATE,
        dense_layers: int = DEFAULT_DENSE_LAYERS,
        activation: str = DEFAULT_ACTIVATION,
        classes: int = DEFAULT_CLASSES,
    ) -> None:
        if kernel_sizes is None:
            kernel_sizes = NGramCnn.DEFAULT_KERNEL_SIZES

        super(NGramCnn, self).__init__()
        self._convolutions: List[Conv1D] = [
            Conv1D(filters=filters, kernel_size=kernel_size, activation=activation)
            for kernel_size in kernel_sizes
        ]
        self._pools: List[GlobalMaxPool1D] = [
            GlobalMaxPool1D() for _ in range(len(self._convolutions))
        ]
        self._stack: Concatenate = Concatenate(axis=1)
        self._dropout: Dropout = Dropout(rate=dropout_rate)
        self._dense: List[Dense] = (
            [
                Dense(units=(filters * len(kernel_sizes)) // (2**layer))
                for layer in range(1, dense_layers)
            ]
            if dense_layers > 1
            else []
        )
        self._classification: Dense = Dense(units=classes, activation=activation)
        self._softmax: Softmax = Softmax(axis=1)

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        # BATCH x WORDS x EMBEDDING SIZE

        x = [convolution(inputs) for convolution in self._convolutions]
        # [BATCH x WORDS - (KERNEL_SIZE + 1) x FILTERS]

        x = [pool(y) for pool, y in zip(self._pools, x)]
        # [BATCH x FILTERS]

        x = self._stack(x)
        # BATCH x FILTERS * len(KERNEL_SIZES)

        x = self._dropout(x)
        # BATCH x FILTERS * len(KERNEL_SIZES)

        for dense in self._dense:
            x = dense(x)
            # BATCH x FILTERS * len(KERNEL_SIZES) // 2 ** DENSE_LAYER

        x = self._classification(x)
        # BATCH x CLASSES

        x = self._softmax(x)
        # BATCH x CLASSES

        return x
