from tortoise import Model
from tortoise.fields import (
    ForeignKeyField,
    ForeignKeyNullableRelation,
    ReverseRelation,
    TextField,
    UUIDField,
)


class Question(Model):
    id: UUIDField = UUIDField(pk=True)
    text: TextField = TextField()
    formatted_text: TextField = TextField()
    answer: ForeignKeyNullableRelation["Answer"] = ForeignKeyField(
        model_name="models.Answer", related_name="questions"
    )

    def __str__(self) -> str:
        return f"{self.id} ({self.text[:120]}{'...' if len(self.text) > 120 else ''})"


class Answer(Model):
    id: UUIDField = UUIDField(pk=True)
    text: TextField = TextField()
    formatted_text: TextField = TextField()
    questions: ReverseRelation["Question"]

    def __str__(self) -> str:
        return f"{self.id} ({self.text[:120]}{'...' if len(self.text) > 120 else ''})"
