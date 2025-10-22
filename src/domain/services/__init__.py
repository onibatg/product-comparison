"""
Domain services package.

This package contains domain services that encapsulate business logic
and orchestrate operations across multiple domain entities.
"""

from src.domain.services.product_service import ProductService

__all__ = [
    "ProductService",
]
