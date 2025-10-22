"""
JSON-based product repository implementation.

This module provides a concrete implementation of the ProductRepositoryPort
using JSON files as the data source. This is an adapter in hexagonal
architecture terms, implementing the port defined by the domain layer.
"""

import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import ValidationError

from src.domain.models.exceptions import (
    InvalidProductDataException,
    RepositoryException,
)
from src.domain.models.product import Product
from src.domain.ports.product_repository import ProductRepositoryPort

logger = logging.getLogger(__name__)


class JsonProductRepository(ProductRepositoryPort):
    """
    JSON file-based implementation of ProductRepositoryPort.

    This repository reads product data from a JSON file and provides
    access through the repository interface. It handles data loading,
    validation, and caching for efficient access.

    Attributes:
        _data_file_path: Path to the JSON data file
        _products: In-memory cache of loaded products
    """

    def __init__(self, data_file_path: str) -> None:
        """
        Initialize the JSON product repository.

        Args:
            data_file_path: Path to the JSON file containing product data

        Raises:
            RepositoryException: If the data file cannot be loaded
        """
        self._data_file_path = Path(data_file_path)
        self._products: Dict[UUID, Product] = {}
        self._load_products()
        logger.info(
            f"JsonProductRepository initialized with {len(self._products)} products"
        )

    def _load_products(self) -> None:
        """
        Load products from the JSON file into memory.

        This method reads the JSON file, validates each product using
        Pydantic models, and stores them in the internal cache.

        Raises:
            RepositoryException: If file cannot be read or data is invalid
        """
        try:
            if not self._data_file_path.exists():
                error_msg = f"Data file not found: {self._data_file_path}"
                logger.error(error_msg)
                raise RepositoryException(error_msg)

            logger.info(f"Loading products from {self._data_file_path}")

            with open(self._data_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict) or "products" not in data:
                raise InvalidProductDataException(
                    "Invalid JSON structure: expected {'products': [...]}"
                )

            products_data = data["products"]
            if not isinstance(products_data, list):
                raise InvalidProductDataException(
                    "Invalid JSON structure: 'products' must be an array"
                )

            loaded_count = 0
            for idx, product_data in enumerate(products_data):
                try:
                    # Convert price to Decimal for precision
                    if "price" in product_data:
                        product_data["price"] = Decimal(str(product_data["price"]))

                    product = Product(**product_data)
                    self._products[product.id] = product
                    loaded_count += 1

                except ValidationError as e:
                    logger.warning(
                        f"Skipping invalid product at index {idx}: {e}"
                    )
                    # Continue loading other products even if one is invalid
                    continue

            logger.info(f"Successfully loaded {loaded_count} products")

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format in {self._data_file_path}: {e}"
            logger.error(error_msg)
            raise RepositoryException(error_msg) from e

        except (InvalidProductDataException, RepositoryException):
            raise

        except Exception as e:
            error_msg = f"Failed to load products: {e}"
            logger.error(error_msg)
            raise RepositoryException(error_msg) from e

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
        try:
            return self._products.get(product_id)
        except Exception as e:
            error_msg = f"Failed to retrieve product {product_id}: {e}"
            logger.error(error_msg)
            raise RepositoryException(error_msg) from e

    def find_by_ids(self, product_ids: List[UUID]) -> List[Product]:
        """
        Retrieve multiple products by their identifiers.

        Args:
            product_ids: List of product UUIDs to retrieve

        Returns:
            List of found Product instances (may be empty)

        Raises:
            RepositoryException: If data access fails
        """
        try:
            products = []
            for product_id in product_ids:
                product = self._products.get(product_id)
                if product:
                    products.append(product)

            return products

        except Exception as e:
            error_msg = f"Failed to retrieve products: {e}"
            logger.error(error_msg)
            raise RepositoryException(error_msg) from e

    def find_all(self) -> List[Product]:
        """
        Retrieve all available products.

        Returns:
            List of all Product instances (may be empty)

        Raises:
            RepositoryException: If data access fails
        """
        try:
            return list(self._products.values())
        except Exception as e:
            error_msg = f"Failed to retrieve all products: {e}"
            logger.error(error_msg)
            raise RepositoryException(error_msg) from e

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
        try:
            return product_id in self._products
        except Exception as e:
            error_msg = f"Failed to check product existence: {e}"
            logger.error(error_msg)
            raise RepositoryException(error_msg) from e

    def count(self) -> int:
        """
        Get the total number of products.

        Returns:
            Total count of products

        Raises:
            RepositoryException: If data access fails
        """
        try:
            return len(self._products)
        except Exception as e:
            error_msg = f"Failed to count products: {e}"
            logger.error(error_msg)
            raise RepositoryException(error_msg) from e
