"""
Product domain service.

This module contains the business logic for product-related operations.
Domain services orchestrate operations that don't naturally belong to a
single entity and encapsulate domain rules and workflows.
"""

import logging
from typing import List
from uuid import UUID

from src.domain.models.exceptions import ProductNotFoundException
from src.domain.models.product import Product
from src.domain.ports.product_repository import ProductRepositoryPort

logger = logging.getLogger(__name__)


class ProductService:
    """
    Service for product-related business operations.

    This service encapsulates the business logic for product retrieval and
    comparison. It depends on the ProductRepositoryPort abstraction rather
    than concrete implementations, following the Dependency Inversion Principle.

    The service layer acts as the application's use case implementation,
    coordinating between domain entities and repositories.
    """

    def __init__(self, product_repository: ProductRepositoryPort) -> None:
        """
        Initialize the product service.

        Args:
            product_repository: Repository implementation for product data access
        """
        self._repository = product_repository
        logger.info("ProductService initialized")

    def get_product_by_id(self, product_id: UUID) -> Product:
        """
        Retrieve a single product by its identifier.

        Args:
            product_id: UUID of the product to retrieve

        Returns:
            Product instance

        Raises:
            ProductNotFoundException: If product is not found
            RepositoryException: If data access fails
        """
        logger.debug(f"Retrieving product with ID: {product_id}")

        product = self._repository.find_by_id(product_id)

        if product is None:
            logger.warning(f"Product not found: {product_id}")
            raise ProductNotFoundException(str(product_id))

        logger.debug(f"Successfully retrieved product: {product.name}")
        return product

    def get_products_for_comparison(self, product_ids: List[UUID]) -> List[Product]:
        """
        Retrieve multiple products for comparison.

        This method supports batch retrieval of products, which is essential
        for the comparison feature. It validates that all requested products
        exist and returns them in a consistent order.

        Args:
            product_ids: List of product UUIDs to retrieve

        Returns:
            List of Product instances

        Raises:
            ProductNotFoundException: If any requested product is not found
            RepositoryException: If data access fails
            ValueError: If product_ids list is empty or contains duplicates
        """
        if not product_ids:
            logger.warning("Empty product_ids list provided")
            raise ValueError("At least one product ID must be provided")

        # Check for duplicates
        if len(product_ids) != len(set(product_ids)):
            logger.warning("Duplicate product IDs detected")
            raise ValueError("Product IDs must be unique")

        logger.info(f"Retrieving {len(product_ids)} products for comparison")

        products = self._repository.find_by_ids(product_ids)

        # Verify all requested products were found
        found_ids = {product.id for product in products}
        missing_ids = set(product_ids) - found_ids

        if missing_ids:
            missing_ids_str = ", ".join(str(pid) for pid in missing_ids)
            logger.error(f"Products not found: {missing_ids_str}")
            raise ProductNotFoundException(
                f"Products not found: {missing_ids_str}"
            )

        # Return products in the same order as requested
        id_to_product = {product.id: product for product in products}
        ordered_products = [id_to_product[pid] for pid in product_ids]

        logger.info(f"Successfully retrieved {len(ordered_products)} products")
        return ordered_products

    def get_all_products(self) -> List[Product]:
        """
        Retrieve all available products.

        This method returns the complete catalog of products. It's useful
        for listing all available items that can be compared.

        Returns:
            List of all Product instances (may be empty)

        Raises:
            RepositoryException: If data access fails
        """
        logger.info("Retrieving all products")
        products = self._repository.find_all()
        logger.info(f"Retrieved {len(products)} products")
        return products

    def product_exists(self, product_id: UUID) -> bool:
        """
        Check if a product exists.

        Args:
            product_id: UUID of the product to check

        Returns:
            True if product exists, False otherwise

        Raises:
            RepositoryException: If data access fails
        """
        exists = self._repository.exists(product_id)
        logger.debug(f"Product {product_id} exists: {exists}")
        return exists

    def get_product_count(self) -> int:
        """
        Get the total number of available products.

        Returns:
            Total count of products

        Raises:
            RepositoryException: If data access fails
        """
        count = self._repository.count()
        logger.debug(f"Total product count: {count}")
        return count
