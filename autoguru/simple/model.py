from typing import Optional, Iterable, Generator, Union, Mapping, Tuple
from threading import Lock
from pathlib import Path
import json

from ..model import QuestionAnswerStore


class _Counter(object):
    def __init__(self) -> None:
        self._value = -1
        self._lock = Lock()

    def next(self) -> int:
        with self._lock:
            self._value += 1
            return self._value


class InMemoryQAStore(QuestionAnswerStore):
    def __init__(self, answers: Mapping[str, str] = None) -> None:
        self._ids = _Counter()
        self._questions = {}
        self._answers = {}

        if answers is not None:
            for question, answer in answers.items():
                self.add_answer(question=question, answer=answer)

    def get_answer(self, id_: str) -> Optional[str]:
        try:
            return self._answers[self._questions[id_]][1]
        except KeyError:
            return None

    def get_answers(self, ids: Iterable[str]) -> Generator[Optional[str], None, None]:
        for id_ in ids:
            yield self.get_answer(id_=id_)

    def add_answer(self, question: str, answer: str) -> str:
        try:
            id_, _ = self._answers[question]
        except KeyError:
            id_ = self._ids.next()

        self._questions[id_] = question
        self._answers[question] = (id_, answer)

    def get_questions(self) -> Generator[Tuple[str, str], None, None]:
        for question, answer in self._answers.items():
            yield answer[0], question

    def save_to_json(self, target: Union[str, Path], encoding: str = "UTF-8") -> None:
        if isinstance(target, str):
            target = Path(target)

        with target.open(mode="w", encoding=encoding) as out_file:
            json.dump(
                {question: answer[1] for question, answer in self._answers.items()},
                out_file,
                indent=2,
            )

    @classmethod
    def load_from_json(
        cls, source: Union[str, Path], encoding: str = "UTF-8"
    ) -> "InMemoryQAStore":
        if isinstance(source, str):
            source = Path(source)

        with source.open(mode="r", encoding=encoding) as in_file:
            answers = json.load(in_file)

        return cls(answers=answers)
