from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from autoguru.persistence import Answer, Question
from autoguru.questionanswering.search import QuestionSearchService


@dataclass
class QuestionAnswer:
    __slots__ = ["answer", "confidence"]

    answer: Answer
    confidence: float


class ConfidencePoolingStrategy(Enum):
    MAXIMUM = auto()
    MINIMUM = auto()
    ARITHMETIC_MEAN = auto()
    GEOMETRIC_MEAN = auto()
    MEDIAN = auto()


class QuestionAnsweringService:
    def __init__(
        self,
        search: QuestionSearchService,
        confidence_pooling_strategy: ConfidencePoolingStrategy = ConfidencePoolingStrategy.MAXIMUM,
    ) -> None:
        self._search: QuestionSearchService = search
        self._pooling: ConfidencePoolingStrategy = confidence_pooling_strategy

    def answer(self, question: Question, k: int = 1) -> List[QuestionAnswer]:
        # TODO: THIS
        pass
