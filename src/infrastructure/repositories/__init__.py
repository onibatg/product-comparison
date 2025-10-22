"""
Infrastructure repositories package.

This package contains concrete implementations of repository ports,
providing adapters for various data sources (JSON files, databases, etc.).
"""

from src.infrastructure.repositories.json_product_repository import (
    JsonProductRepository,
)

__all__ = [
    "JsonProductRepository",
]
