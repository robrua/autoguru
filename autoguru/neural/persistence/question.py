from uuid import UUID, uuid4

from pony.orm import Optional, PrimaryKey, Required

from autoguru.persistence.model import Entity


class Question(Entity):
    id = PrimaryKey(UUID, default=uuid4)
    text = Required(str)
    formatted_text = Required(str)
    answer = Optional("Answer")
