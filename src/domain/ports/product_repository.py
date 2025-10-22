"""
Product repository port (interface).

This module defines the abstract interface for product repositories.
Following the Dependency Inversion Principle, the domain layer defines
what it needs from the infrastructure layer through this port.

Concrete implementations (adapters) will be provided by the infrastructure layer.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.product import Product


class ProductRepositoryPort(ABC):
    """
    Abstract interface for product data access.

    This port defines the contract that any product repository implementation
    must fulfill. By depending on this abstraction rather than concrete
    implementations, we achieve loose coupling between domain and infrastructure.

    The repository pattern encapsulates data access logic and provides a
    collection-like interface for accessing domain objects.
    """

    @abstractmethod
    def find_by_id(self, product_id: UUID) -> Optional[Product]:
        """
        Retrieve a product by its unique identifier.

        Args:
            product_id: UUID of the product to retrieve

        Returns:
            Product instance if found, None otherwise

        Raises:
            RepositoryException: If data access fails
        """
        pass

    @abstractmethod
    def find_by_ids(self, product_ids: List[UUID]) -> List[Product]:
        """
        Retrieve multiple products by their identifiers.

        This method supports batch retrieval for efficient comparison operations.
        Products that are not found are silently omitted from the result.

        Args:
            product_ids: List of product UUIDs to retrieve

        Returns:
            List of found Product instances (may be empty)

        Raises:
            RepositoryException: If data access fails
        """
        pass

    @abstractmethod
    def find_all(self) -> List[Product]:
        """
        Retrieve all available products.

        Returns:
            List of all Product instances (may be empty)

        Raises:
            RepositoryException: If data access fails
        """
        pass

    @abstractmethod
    def exists(self, product_id: UUID) -> bool:
        """
        Check if a product exists by its identifier.

        Args:
            product_id: UUID of the product to check

        Returns:
            True if product exists, False otherwise

        Raises:
            RepositoryException: If data access fails
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get the total number of products.

        Returns:
            Total count of products

        Raises:
            RepositoryException: If data access fails
        """
        pass
