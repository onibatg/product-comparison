"""
API package.

This package contains the HTTP adapter layer of the application,
including FastAPI routes, dependencies, and exception handlers.
"""

from src.api.exception_handlers import EXCEPTION_HANDLERS
from src.api.routes import router

__all__ = [
    "router",
    "EXCEPTION_HANDLERS",
]
