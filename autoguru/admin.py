
from fastapi_admin.app import app
from fastapi_admin.resources import Field, Model, Link, ComputeField
from fastapi_admin.widgets import displays, filters, inputs

from .models import Admin, Answer, Question


@app.register
class Dashboard(Link):
    label = "Dashboard"
    icon = "fas fa-home"
    url = "/admin"


@app.register
class AdminResource(Model):
    label = "Admins"
    model = Admin
    icon = "fas fa-user"
    page_pre_title = "admin list"
    page_title = "admin model"
    filters = [
        filters.Search(
            name="username", label="Name", search_mode="contains", placeholder="Search for username"
        ),
        filters.Date(name="created_at", label="CreatedAt"),
    ]
    fields = [
        "id",
        "username",
        Field(
            name="password",
            label="Password",
            display=displays.InputOnly(),
            input_=inputs.Password(),
        ),
        Field(name="email", label="Email", input_=inputs.Email()),
        "created_at",
    ]


@app.register
class AnswerResource(Model):
    label = "Answers"
    model = Answer
    icon = "fas fa-voicemail"
    page_pre_title = "answer list"
    page_title = "answer model"
    filters = [
        filters.Search(
            name="formatted_text", label="Content", search_mode="contains", placeholder="Search for content"
        ),
    ]
    fields = [
        "id",
        "text",
        "formatted_text",
    ]


@app.register
class QuestionResource(Model):
    label = "Questions"
    model = Question
    icon = "fas fa-question"
    page_pre_title = "question list"
    page_title = "question model"
    filters = [
        filters.Search(
            name="formatted_text", label="Content", search_mode="contains", placeholder="Search for content"
        ),
    ]
    fields = [
        "id",
        "text",
        "formatted_text",
        "answer"
    ]
