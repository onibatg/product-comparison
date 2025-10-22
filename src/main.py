"""
Main application entry point.

This module initializes and configures the FastAPI application,
including routers, middleware, exception handlers, and startup/shutdown events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import EXCEPTION_HANDLERS, router
from src.config.settings import settings

# Configure logging
settings.configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    This is the recommended way to manage application lifecycle in FastAPI.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting Item Comparison API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Settings: {settings.get_summary()}")

    yield

    # Shutdown
    logger.info("Shutting down Item Comparison API")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function sets up the FastAPI application with all necessary
    middleware, routers, and exception handlers. It follows the
    factory pattern for testability and flexibility.

    Returns:
        Configured FastAPI application instance
    """
    # Create FastAPI app with metadata
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        **Item Comparison API** - A production-ready RESTful API for comparing products.

        ## Features

        * **Get All Products**: Retrieve the complete product catalog
        * **Get Product by ID**: Fetch detailed information for a specific product
        * **Batch Comparison**: Retrieve multiple products at once for comparison
        * **Health Check**: Monitor API status and product catalog size

        ## Architecture

        This API is built using **Hexagonal Architecture** (Ports & Adapters pattern),
        ensuring clean separation of concerns and maintainability:

        * **Domain Layer**: Core business logic and entities
        * **Application Layer**: Use cases and services
        * **Infrastructure Layer**: Data access and external services
        * **API Layer**: HTTP endpoints and request/response handling

        ## Technology Stack

        * **FastAPI**: Modern, fast web framework for building APIs
        * **Pydantic**: Data validation and settings management
        * **Python 3.11+**: Latest Python features and performance

        ## Getting Started

        1. Browse the available endpoints below
        2. Try the interactive documentation at `/docs`
        3. View alternative documentation at `/redoc`
        """,
        lifespan=lifespan,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    for exception_class, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, handler)
        logger.debug(f"Registered exception handler for {exception_class.__name__}")

    # Include routers
    app.include_router(router, prefix=settings.api_prefix)
    logger.debug(f"Registered router with prefix {settings.api_prefix}")

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """
        Root endpoint providing API information.

        Returns basic information about the API and links to documentation.
        """
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "api_version": settings.api_version,
            "environment": settings.environment,
            "documentation": {
                "interactive": f"{settings.api_prefix}/docs",
                "redoc": f"{settings.api_prefix}/redoc",
                "openapi": f"{settings.api_prefix}/openapi.json"
            },
            "endpoints": {
                "get_all_products": f"{settings.api_prefix}/products",
                "get_product_by_id": f"{settings.api_prefix}/products/{{id}}",
                "compare_products": f"{settings.api_prefix}/products/compare/batch",
                "health_check": f"{settings.api_prefix}/products/health/count"
            }
        }

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """
        Health check endpoint.

        Returns the health status of the API.
        """
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version
        }

    logger.info("FastAPI application created and configured")
    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.host}:{settings.port}")

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
