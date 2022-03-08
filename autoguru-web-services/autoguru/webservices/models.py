from fastapi_admin.models import AbstractAdmin
from tortoise import Model, fields
from tortoise.signals import pre_save


class Admin(AbstractAdmin):
    email = fields.CharField(max_length=200, default="")
    last_login = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} ({self.username})"


class Answer(Model):
    id = fields.UUIDField(pk=True)
    text = fields.TextField(default="")
    formatted_text = fields.TextField(default="")

    questions: fields.ReverseRelation["Question"]

    def __str__(self) -> str:
        return f"{self.id} ({self.formatted_text[:120]}{'...' if len(self.formatted_text) > 120 else ''})"


@pre_save(Answer)
async def answer_pre_save(sender, instance: Answer, using_db, update_fields) -> None:
    if not instance.formatted_text:
        instance.formatted_text = instance.text


class Question(Model):
    id = fields.UUIDField(pk=True)
    text = fields.TextField(default="")
    formatted_text = fields.TextField(default="")
    answer: fields.ForeignKeyRelation[Answer] = fields.ForeignKeyField(
        "models.Answer", related_name="questions"
    )

    def __str__(self) -> str:
        return f"{self.id} ({self.formatted_text[:120]}{'...' if len(self.formatted_text) > 120 else ''})"


@pre_save(Question)
async def question_pre_save(sender, instance: Question, using_db, update_fields) -> None:
    if not instance.formatted_text:
        instance.formatted_text = instance.text
