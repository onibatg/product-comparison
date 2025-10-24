"""
Integration tests for JsonProductRepository.

These tests verify the repository's interaction with real JSON files,
testing data loading, parsing, and querying without mocks.
"""

import json
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import List
from uuid import UUID, uuid4

import pytest

from src.domain.models.exceptions import (
    InvalidProductDataException,
    RepositoryException,
)
from src.domain.models.product import Product
from src.infrastructure.repositories.json_product_repository import (
    JsonProductRepository,
)


@pytest.mark.integration
class TestJsonRepositoryInitialization:
    """Test repository initialization and data loading."""

    def test_should_load_valid_json_file(
        self, sample_products_file_path: Path
    ) -> None:
        """
        GIVEN: Valid JSON file with product data
        WHEN: JsonProductRepository is initialized
        THEN: Products should be loaded successfully
        """
        # Act
        repository = JsonProductRepository(data_file_path=str(sample_products_file_path))

        # Assert
        assert repository.count() > 0
        products = repository.find_all()
        assert all(isinstance(p, Product) for p in products)

    def test_should_raise_error_for_missing_file(self) -> None:
        """
        GIVEN: Path to non-existent file
        WHEN: JsonProductRepository is initialized
        THEN: RepositoryException should be raised
        """
        # Arrange
        non_existent_path = "/tmp/nonexistent_products.json"

        # Act & Assert
        with pytest.raises(RepositoryException) as exc_info:
            JsonProductRepository(data_file_path=non_existent_path)

        assert "not found" in str(exc_info.value).lower()

    def test_should_raise_error_for_invalid_json(self) -> None:
        """
        GIVEN: File with invalid JSON syntax
        WHEN: JsonProductRepository is initialized
        THEN: RepositoryException should be raised
        """
        # Arrange - Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name

        try:
            # Act & Assert
            with pytest.raises(RepositoryException) as exc_info:
                JsonProductRepository(data_file_path=temp_file)

            assert "invalid json" in str(exc_info.value).lower()
        finally:
            # Cleanup
            Path(temp_file).unlink()

    def test_should_raise_error_for_missing_products_key(self) -> None:
        """
        GIVEN: JSON file without 'products' key
        WHEN: JsonProductRepository is initialized
        THEN: InvalidProductDataException should be raised
        """
        # Arrange
        invalid_structure = {"items": []}  # Wrong key

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(invalid_structure, f)
            temp_file = f.name

        try:
            # Act & Assert
            with pytest.raises(InvalidProductDataException) as exc_info:
                JsonProductRepository(data_file_path=temp_file)

            assert "products" in str(exc_info.value).lower()
        finally:
            Path(temp_file).unlink()

    def test_should_skip_invalid_products_and_load_valid_ones(self) -> None:
        """
        GIVEN: JSON file with mix of valid and invalid products
        WHEN: JsonProductRepository is initialized
        THEN: Valid products should be loaded, invalid ones skipped
        """
        # Arrange
        mixed_data = {
            "products": [
                {
                    "id": str(uuid4()),
                    "name": "Valid Product 1",
                    "image_url": "https://example.com/1.jpg",
                    "description": "Valid product",
                    "price": "99.99",
                    "rating": 4.5,
                },
                {
                    "id": str(uuid4()),
                    "name": "Invalid Product",
                    "image_url": "https://example.com/2.jpg",
                    "description": "Invalid - negative price",
                    "price": "-10.00",  # Invalid
                    "rating": 4.5,
                },
                {
                    "id": str(uuid4()),
                    "name": "Valid Product 2",
                    "image_url": "https://example.com/3.jpg",
                    "description": "Another valid product",
                    "price": "149.99",
                    "rating": 4.8,
                },
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(mixed_data, f)
            temp_file = f.name

        try:
            # Act
            repository = JsonProductRepository(data_file_path=temp_file)

            # Assert - Should load 2 valid products, skip 1 invalid
            assert repository.count() == 2
        finally:
            Path(temp_file).unlink()

    def test_should_handle_empty_products_array(self) -> None:
        """
        GIVEN: JSON file with empty products array
        WHEN: JsonProductRepository is initialized
        THEN: Repository should be created with zero products
        """
        # Arrange
        empty_data = {"products": []}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(empty_data, f)
            temp_file = f.name

        try:
            # Act
            repository = JsonProductRepository(data_file_path=temp_file)

            # Assert
            assert repository.count() == 0
            assert repository.find_all() == []
        finally:
            Path(temp_file).unlink()


@pytest.mark.integration
class TestJsonRepositoryFindById:
    """Test finding products by ID."""

    def test_should_find_existing_product(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Product exists in repository
        WHEN: find_by_id is called
        THEN: Product should be returned
        """
        # Arrange
        all_products = json_repository.find_all()
        assert len(all_products) > 0
        existing_product = all_products[0]

        # Act
        result = json_repository.find_by_id(existing_product.id)

        # Assert
        assert result is not None
        assert result.id == existing_product.id
        assert result.name == existing_product.name

    def test_should_return_none_for_non_existent_product(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Product ID that doesn't exist
        WHEN: find_by_id is called
        THEN: None should be returned
        """
        # Arrange
        non_existent_id = uuid4()

        # Act
        result = json_repository.find_by_id(non_existent_id)

        # Assert
        assert result is None

    def test_should_return_complete_product_data(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Product with complete data
        WHEN: find_by_id is called
        THEN: All product fields should be populated
        """
        # Arrange
        all_products = json_repository.find_all()
        product_id = all_products[0].id

        # Act
        result = json_repository.find_by_id(product_id)

        # Assert
        assert result is not None
        assert isinstance(result.id, UUID)
        assert isinstance(result.name, str)
        assert len(result.name) > 0
        assert isinstance(result.price, Decimal)
        assert result.price > 0
        assert 0.0 <= result.rating <= 5.0
        assert isinstance(result.specifications, dict)


@pytest.mark.integration
class TestJsonRepositoryFindByIds:
    """Test batch finding products."""

    def test_should_find_all_existing_products(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Multiple product IDs that exist
        WHEN: find_by_ids is called
        THEN: All products should be returned
        """
        # Arrange
        all_products = json_repository.find_all()
        requested_ids = [p.id for p in all_products[:3]]

        # Act
        result = json_repository.find_by_ids(requested_ids)

        # Assert
        assert len(result) == 3
        result_ids = {p.id for p in result}
        assert result_ids == set(requested_ids)

    def test_should_return_only_found_products(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Mix of existing and non-existing IDs
        WHEN: find_by_ids is called
        THEN: Only existing products should be returned
        """
        # Arrange
        all_products = json_repository.find_all()
        existing_id = all_products[0].id
        non_existent_id = uuid4()
        requested_ids = [existing_id, non_existent_id]

        # Act
        result = json_repository.find_by_ids(requested_ids)

        # Assert
        assert len(result) == 1
        assert result[0].id == existing_id

    def test_should_return_empty_list_for_no_matches(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: IDs that don't exist
        WHEN: find_by_ids is called
        THEN: Empty list should be returned
        """
        # Arrange
        non_existent_ids = [uuid4(), uuid4(), uuid4()]

        # Act
        result = json_repository.find_by_ids(non_existent_ids)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_should_handle_empty_id_list(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Empty list of IDs
        WHEN: find_by_ids is called
        THEN: Empty list should be returned
        """
        # Act
        result = json_repository.find_by_ids([])

        # Assert
        assert result == []

    @pytest.mark.performance
    def test_should_handle_large_batch_efficiently(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Large number of product IDs
        WHEN: find_by_ids is called
        THEN: Should complete in reasonable time (<100ms)
        """
        import time

        # Arrange
        all_products = json_repository.find_all()
        # Request same products multiple times
        requested_ids = [p.id for p in all_products] * 20

        # Act
        start_time = time.time()
        result = json_repository.find_by_ids(requested_ids)
        elapsed_ms = (time.time() - start_time) * 1000

        # Assert
        assert len(result) > 0
        assert elapsed_ms < 100, f"Batch query took {elapsed_ms}ms (limit: 100ms)"


@pytest.mark.integration
class TestJsonRepositoryFindAll:
    """Test finding all products."""

    def test_should_return_all_loaded_products(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Repository with loaded products
        WHEN: find_all is called
        THEN: All products should be returned
        """
        # Act
        result = json_repository.find_all()

        # Assert
        assert len(result) > 0
        assert all(isinstance(p, Product) for p in result)

    def test_should_return_consistent_results(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Repository with products
        WHEN: find_all is called multiple times
        THEN: Same products should be returned each time
        """
        # Act
        result_1 = json_repository.find_all()
        result_2 = json_repository.find_all()

        # Assert
        assert len(result_1) == len(result_2)
        ids_1 = {p.id for p in result_1}
        ids_2 = {p.id for p in result_2}
        assert ids_1 == ids_2


@pytest.mark.integration
class TestJsonRepositoryExists:
    """Test product existence checking."""

    def test_should_return_true_for_existing_product(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Product exists in repository
        WHEN: exists is called
        THEN: True should be returned
        """
        # Arrange
        existing_product = json_repository.find_all()[0]

        # Act
        result = json_repository.exists(existing_product.id)

        # Assert
        assert result is True

    def test_should_return_false_for_non_existent_product(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Product doesn't exist
        WHEN: exists is called
        THEN: False should be returned
        """
        # Arrange
        non_existent_id = uuid4()

        # Act
        result = json_repository.exists(non_existent_id)

        # Assert
        assert result is False


@pytest.mark.integration
class TestJsonRepositoryCount:
    """Test product counting."""

    def test_should_return_correct_count(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Repository with products
        WHEN: count is called
        THEN: Correct number should be returned
        """
        # Arrange
        all_products = json_repository.find_all()

        # Act
        count = json_repository.count()

        # Assert
        assert count == len(all_products)
        assert count > 0

    def test_should_match_find_all_length(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Repository with products
        WHEN: Comparing count() and len(find_all())
        THEN: Values should match
        """
        # Act
        count = json_repository.count()
        all_products_len = len(json_repository.find_all())

        # Assert
        assert count == all_products_len


@pytest.mark.integration
class TestJsonRepositoryDataIntegrity:
    """Test data integrity and edge cases."""

    def test_should_preserve_decimal_precision(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Products with precise decimal prices
        WHEN: Loading from JSON
        THEN: Decimal precision should be maintained
        """
        # Act
        products = json_repository.find_all()

        # Assert
        for product in products:
            assert isinstance(product.price, Decimal)
            # Check decimal places
            price_str = str(product.price)
            if "." in price_str:
                decimal_places = len(price_str.split(".")[1])
                assert decimal_places <= 2

    def test_should_handle_unicode_characters(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Products with unicode characters in fields
        WHEN: Loading from JSON
        THEN: Unicode should be preserved correctly
        """
        # Create test file with unicode
        unicode_data = {
            "products": [
                {
                    "id": str(uuid4()),
                    "name": "Produit français 🇫🇷",
                    "image_url": "https://example.com/français.jpg",
                    "description": "Description avec accents: café, crème",
                    "price": "99.99",
                    "rating": 4.5,
                }
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(unicode_data, f, ensure_ascii=False)
            temp_file = f.name

        try:
            # Act
            repository = JsonProductRepository(data_file_path=temp_file)
            products = repository.find_all()

            # Assert
            assert len(products) == 1
            assert "français" in products[0].name
            assert "🇫🇷" in products[0].name
            assert "café" in products[0].description
        finally:
            Path(temp_file).unlink()

    def test_should_handle_large_specifications(
        self, json_repository: JsonProductRepository
    ) -> None:
        """
        GIVEN: Product with many specification fields
        WHEN: Loading from repository
        THEN: All specifications should be preserved
        """
        # Arrange
        products = json_repository.find_all()

        # Act & Assert
        for product in products:
            if product.specifications:
                # Verify specifications is a dict
                assert isinstance(product.specifications, dict)
                # Verify we can access nested values
                for key, value in product.specifications.items():
                    assert key is not None
