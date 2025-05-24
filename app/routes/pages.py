from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import status

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "pages/home.html",
        {"request": request, "title": "Home"}
    )

@router.get("/about", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def about(request: Request):
    """Render the about page."""
    return templates.TemplateResponse(
        "pages/about.html",
        {"request": request, "title": "About"}
    )

@router.get("/docs/api", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def api_docs(request: Request):
    """Render the API documentation page."""
    return templates.TemplateResponse(
        "docs/api.html",
        {"request": request, "title": "API Documentation"}
    )
