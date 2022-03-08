from fastapi import Depends
from fastapi_admin.app import app as admin_app
from fastapi_admin.depends import get_resources
from fastapi_admin.template import templates
from starlette.requests import Request
from starlette.responses import RedirectResponse

from autoguru.webservices.models import Admin


@admin_app.get("/")
async def home(
    request: Request,
    resources=Depends(get_resources),
):
    admin = request.state.admin
    if not admin:
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Dashboard",
            "page_pre_title": "overview",
            "page_title": "Dashboard",
        },
    )


@admin_app.get("/dbinit")
async def index():
    if not await Admin.all().exists():
        await Admin.get_or_create(
            username="admin", password="123456", email="admin@autoguru.dev"
        )
    return RedirectResponse(url="/admin")
