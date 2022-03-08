import os

import aioredis
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider

from autoguru.webservices.main import app
from autoguru.webservices.models import Admin
from autoguru.webservices.settings import BASE_DIR


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(
        "redis://localhost:6379/7",
        decode_responses=True,
        encoding="utf8",
    )
    await admin_app.configure(
        logo_url="/static/logo.png",
        template_folders=[os.path.join(BASE_DIR, "templates")],
        providers=[
            UsernamePasswordProvider(
                admin_model=Admin,
                login_logo_url="https://preview.tabler.io/static/logo.svg",
            )
        ],
        redis=redis,
    )
