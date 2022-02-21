from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Iterable, List, Union, no_type_check


class QuestionClass(Enum):
    QUESTION = auto()
    NOT_QUESTION = auto()


@dataclass
class QuestionClassification:
    classification: QuestionClass
    confidence: float


class QuestionClassifier(ABC):
    @abstractmethod
    def classify(
        self, questions: Union[str, Iterable[str]], k: int = 1
    ) -> List[List[QuestionClassification]]:
        raise NotImplementedError

    @no_type_check
    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> "QuestionClassifier":
        raise NotImplementedError
