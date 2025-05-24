from fastapi import APIRouter

# Initialize the routes package
from . import pages, api, health

# Create a router that includes all other routers
router = APIRouter()
router.include_router(pages.router)
router.include_router(api.router, prefix="/api")
router.include_router(health.router, prefix="/health")

# Import all routes to make them discoverable
# This must be after the router is created to avoid circular imports
from .pages import *  # noqa: F401, F403
from .api import *  # noqa: F401, F403
from .health import *  # noqa: F401, F403

__all__ = [
    'router',
    'pages',
    'api',
    'health'
]
