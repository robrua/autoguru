from copy import copy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Type, Union

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import (
    Concatenate,
    Conv1D,
    Dense,
    Dropout,
    GlobalMaxPool1D,
    Softmax,
)
from tensorflow.keras.losses import CategoricalCrossentropy, Loss
from tensorflow.keras.metrics import CategoricalAccuracy
from tensorflow.keras.metrics import (
    CategoricalCrossentropy as CategoricalCrossentropyMetric,
)
from tensorflow.keras.metrics import (
    FalseNegatives,
    FalsePositives,
    Metric,
    TrueNegatives,
    TruePositives,
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adadelta, Optimizer

from autoguru.embeddings import Embedder
from autoguru.questionclassification.model import (
    QuestionClass,
    QuestionClassification,
    QuestionClassifier,
)
from autoguru.utilities.tokenization import tokenize_sentences, tokenize_words


# Based on https://arxiv.org/pdf/2001.00571.pdf
class ConvolutionalNGramsModel(Model):
    DEFAULT_KERNEL_SIZES: List[int] = [3, 4, 5]
    DEFAULT_FILTERS: int = 100
    DEFAULT_DROPOUT_RATE: float = 0.5
    DEFAULT_DENSE_LAYERS: int = 1
    DEFAULT_ACTIVATION: str = "relu"
    DEFAULT_CLASSES: int = len(QuestionClass)

    DEFAULT_OPTIMIZER: Type[Optimizer] = Adadelta
    DEFAULT_LOSS: Type[Loss] = CategoricalCrossentropy
    DEFAULT_METRICS: List[Type[Metric]] = [
        CategoricalAccuracy,
        CategoricalCrossentropyMetric,
        TruePositives,
        FalsePositives,
        TrueNegatives,
        FalseNegatives,
    ]

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
            kernel_sizes = copy(ConvolutionalNGramsModel.DEFAULT_KERNEL_SIZES)

        super(ConvolutionalNGramsModel, self).__init__()
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

    @tf.function
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


class ConvolutionalNGrams:
    DEFAULT_DTYPE: tf.DType = tf.float32

    def __init__(
        self,
        embedding_size: int,
        kernel_sizes: List[int] = None,
        filters: int = ConvolutionalNGramsModel.DEFAULT_FILTERS,
        dropout_rate: float = ConvolutionalNGramsModel.DEFAULT_DROPOUT_RATE,
        dense_layers: int = ConvolutionalNGramsModel.DEFAULT_DENSE_LAYERS,
        activation: str = ConvolutionalNGramsModel.DEFAULT_ACTIVATION,
        optimizer: Optimizer = None,
        loss: Loss = None,
        metrics: List[Metric] = None,
        dtype: tf.DType = DEFAULT_DTYPE,
    ) -> None:
        if kernel_sizes is None:
            kernel_sizes = copy(ConvolutionalNGramsModel.DEFAULT_KERNEL_SIZES)
        if optimizer is None:
            optimizer = ConvolutionalNGramsModel.DEFAULT_OPTIMIZER()
        if loss is None:
            loss = ConvolutionalNGramsModel.DEFAULT_LOSS()
        if metrics is None:
            metrics = [metric() for metric in ConvolutionalNGramsModel.DEFAULT_METRICS]

        self._model: ConvolutionalNGramsModel = ConvolutionalNGramsModel(
            kernel_sizes=kernel_sizes,
            filters=filters,
            dropout_rate=dropout_rate,
            dense_layers=dense_layers,
            activation=activation,
            classes=len(QuestionClass),
        )

        self._model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        self._model(
            tf.random.uniform(shape=(1, max(kernel_sizes), embedding_size), dtype=dtype)
        )  # Model.build is broken :(

        self._embedding_size: int = embedding_size
        self._dtype: tf.Dtype = dtype
        self._classes: List[QuestionClass] = list(
            QuestionClass
        )  # Iteration order is guaranteed

    def classify(
        self, token_embeddings: np.ndarray, k: int = 1
    ) -> List[List[QuestionClassification]]:
        predictions = self._model(token_embeddings)
        top_k = tf.math.top_k(predictions, k=k)
        return [
            [
                QuestionClassification(
                    classification=self._classes[index],
                    confidence=probability.numpy().item(),
                )
                for probability, index in zip(probabilities, indexes)
            ]
            for probabilities, indexes in zip(top_k.values, top_k.indices)
        ]

    def train(
        self,
        instances: np.ndarray,
        labels: np.ndarray,
        batch_size: int = 32,
        epochs: int = 1,
        shuffle: bool = True,
        verbose: bool = False,
    ) -> None:
        self._model.fit(
            x=instances,
            y=labels,
            batch_size=batch_size,
            epochs=epochs,
            shuffle=shuffle,
            verbose=verbose,
        )

    def save(self, saved_model_path: Union[str, Path]) -> None:
        if isinstance(saved_model_path, Path):
            saved_model_path = str(saved_model_path.resolve())

        @tf.function
        def attributes():
            return {
                "classes": tf.convert_to_tensor(
                    [clazz.name for clazz in self._classes]
                ),
                "embedding_size": self._embedding_size,
                "dtype": self._dtype.name,
            }

        self._model.attributes = attributes
        tf.saved_model.save(
            self._model,
            saved_model_path,
            {
                "call": self._model.call.get_concrete_function(
                    tf.TensorSpec(
                        shape=(None, None, self._embedding_size), dtype=self._dtype
                    )
                ),
                "attributes": self._model.attributes.get_concrete_function(),
            },
        )

    @classmethod
    def load(cls, saved_model_path: Union[str, Path]) -> "ConvolutionalNGrams":
        if isinstance(saved_model_path, Path):
            saved_model_path = str(saved_model_path.resolve())

        classifier = object.__new__(cls)
        classifier._model = tf.saved_model.load(saved_model_path)

        attributes = classifier._model.attributes()
        classifier._classes = [
            QuestionClass[clazz.numpy().decode("UTF-8")]
            for clazz in attributes["classes"]
        ]
        classifier._dtype = tf.dtypes.as_dtype(
            attributes["dtype"].numpy().decode("UTF-8")
        )
        classifier._embedding_size = attributes["embedding_size"].numpy().item()

        return classifier

    @classmethod
    def create(cls, model_path: Union[str, Path]) -> "ConvolutionalNGrams":
        return cls.load(model_path)


class ConvolutionalNGramClassifier(QuestionClassifier):
    def __init__(self, embedder: Embedder, classifier: ConvolutionalNGrams) -> None:
        self._embedder: Embedder = embedder
        self._classifier: ConvolutionalNGrams = classifier

    def classify(
        self, questions: Union[str, Iterable[str]], k: int = 1
    ) -> List[List[QuestionClassification]]:
        if isinstance(questions, str):
            questions = [questions]

        # Per https://arxiv.org/pdf/1408.5882.pdf we append word and sentence features.
        # We're flattening as we go along so we can batch embed & keep count so we can
        # recover the boundaries between question tokens
        tokens: List[str] = []
        token_counts: List[int] = [0]
        max_tokens: int = 0
        for question in questions:
            question_tokens = tokenize_words(question) + tokenize_sentences(question)
            token_count = len(question_tokens)
            if token_count > max_tokens:
                max_tokens = token_count
            token_counts.append(token_counts[-1] + token_count)
            tokens.extend(question_tokens)

        token_embeddings = self._embedder.embed(tokens)
        padded_embeddings = np.zeros(
            shape=(len(token_counts) - 1, max_tokens, token_embeddings.shape[-1]),
            dtype=token_embeddings.dtype,
        )
        for i in range(len(token_counts) - 1):
            token_count = token_counts[i + 1] - token_counts[i]
            padded_embeddings[i][0:token_count] = token_embeddings[
                token_counts[i] : token_counts[i + 1]
            ]

        return self._classifier.classify(padded_embeddings, k=k)

    @classmethod
    def create(
        cls, embedder: Embedder, classifier: ConvolutionalNGrams
    ) -> "ConvolutionalNGramClassifier":
        return cls(embedder=embedder, classifier=classifier)
