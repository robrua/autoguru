from uuid import UUID, uuid4

from pony.orm import PrimaryKey, Required, Set

from autoguru.persistence.model import Entity


class Answer(Entity):
    id = PrimaryKey(UUID, default=uuid4)
    text = Required(str)
    formatted_text = Required(str)
    questions = Set("Question")
