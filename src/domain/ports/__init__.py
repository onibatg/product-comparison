"""
Domain ports package.

This package defines the interfaces (ports) that the domain layer requires
from external adapters. This is a key part of hexagonal architecture,
where the domain defines its needs and the infrastructure provides implementations.
"""

from src.domain.ports.product_repository import ProductRepositoryPort

__all__ = [
    "ProductRepositoryPort",
]
