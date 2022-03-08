import os

from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.exceptions import (
    forbidden_error_exception,
    not_found_error_exception,
    server_error_exception,
    unauthorized_error_exception,
)
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from tortoise.contrib.fastapi import register_tortoise

from .settings import BASE_DIR

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)

app.add_exception_handler(HTTP_404_NOT_FOUND, not_found_error_exception)
admin_app.add_exception_handler(HTTP_500_INTERNAL_SERVER_ERROR, server_error_exception)
admin_app.add_exception_handler(HTTP_404_NOT_FOUND, not_found_error_exception)
admin_app.add_exception_handler(HTTP_403_FORBIDDEN, forbidden_error_exception)
admin_app.add_exception_handler(HTTP_401_UNAUTHORIZED, unauthorized_error_exception)


app.mount("/admin", admin_app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

register_tortoise(
    app,
    config={
        "connections": {"default": "sqlite://db.sqlite3"},
        "apps": {
            "models": {
                "models": ["autoguru.persistence", "autoguru.webservices.models"],
                "default_connection": "default",
            }
        },
    },
    generate_schemas=True,
)
