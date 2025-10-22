"""
API dependency injection.

This module defines FastAPI dependencies that provide instances of
repositories and services to route handlers. This implements dependency
injection, a key aspect of clean architecture and SOLID principles.
"""

import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.config.settings import settings
from src.domain.services.product_service import ProductService
from src.infrastructure.repositories.json_product_repository import (
    JsonProductRepository,
)

logger = logging.getLogger(__name__)


@lru_cache()
def get_product_repository() -> JsonProductRepository:
    """
    Get product repository instance (singleton).

    This dependency provides a singleton instance of the product repository.
    The repository is cached to avoid reloading the JSON file on every request.

    Returns:
        JsonProductRepository instance

    Note:
        Uses lru_cache to create a singleton pattern. In production with
        a real database, you would use connection pooling instead.
    """
    logger.debug("Creating product repository instance")
    return JsonProductRepository(str(settings.data_file_absolute_path))


def get_product_service(
    repository: Annotated[JsonProductRepository, Depends(get_product_repository)]
) -> ProductService:
    """
    Get product service instance with injected repository.

    This dependency creates a ProductService instance with the repository
    injected. Each request gets its own service instance, but they share
    the same repository singleton.

    Args:
        repository: Injected product repository

    Returns:
        ProductService instance
    """
    return ProductService(repository)


# Type aliases for cleaner route handler signatures
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
