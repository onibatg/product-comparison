"""
Unit tests for ProductService domain service.

This module tests the business logic layer, ensuring proper orchestration
of repository operations, validation, and error handling. All dependencies
are mocked for isolation.
"""

from typing import List
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from src.domain.models.exceptions import ProductNotFoundException
from src.domain.models.product import Product
from src.domain.services.product_service import ProductService


@pytest.mark.unit
class TestProductServiceGetById:
    """Test suite for get_product_by_id method."""

    def test_should_return_product_when_id_exists(
        self,
        product_service: ProductService,
        mock_product_repository: Mock,
        test_product: Product,
    ) -> None:
        """
        GIVEN: A product exists in the repository
        WHEN: get_product_by_id is called with valid ID
        THEN: Product should be returned
        """
        # Arrange
        product_id = test_product.id
        mock_product_repository.find_by_id.return_value = test_product

        # Act
        result = product_service.get_product_by_id(product_id)

        # Assert
        assert result == test_product
        mock_product_repository.find_by_id.assert_called_once_with(product_id)

    def test_should_raise_not_found_when_product_missing(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: A product ID that doesn't exist
        WHEN: get_product_by_id is called
        THEN: ProductNotFoundException should be raised
        """
        # Arrange
        product_id = uuid4()
        mock_product_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ProductNotFoundException) as exc_info:
            product_service.get_product_by_id(product_id)

        assert str(product_id) in str(exc_info.value)
        mock_product_repository.find_by_id.assert_called_once_with(product_id)

    def test_should_pass_uuid_correctly_to_repository(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: A UUID product ID
        WHEN: get_product_by_id is called
        THEN: UUID should be passed unchanged to repository
        """
        # Arrange
        product_id = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        mock_product_repository.find_by_id.return_value = None

        # Act
        try:
            product_service.get_product_by_id(product_id)
        except ProductNotFoundException:
            pass

        # Assert
        call_args = mock_product_repository.find_by_id.call_args[0][0]
        assert isinstance(call_args, UUID)
        assert call_args == product_id


@pytest.mark.unit
class TestProductServiceGetBatch:
    """Test suite for get_products_for_comparison method."""

    def test_should_return_all_products_when_all_exist(
        self,
        product_service_with_data: ProductService,
        test_products_list: List[Product],
        test_product_ids: List[UUID],
    ) -> None:
        """
        GIVEN: Multiple products exist in repository
        WHEN: get_products_for_comparison is called with all valid IDs
        THEN: All products should be returned in correct order
        """
        # Arrange
        requested_ids = test_product_ids[:3]

        # Act
        result = product_service_with_data.get_products_for_comparison(requested_ids)

        # Assert
        assert len(result) == 3
        assert [p.id for p in result] == requested_ids

    def test_should_raise_error_when_some_products_missing(
        self,
        product_service: ProductService,
        mock_product_repository: Mock,
        test_products_list: List[Product],
    ) -> None:
        """
        GIVEN: Some requested products don't exist
        WHEN: get_products_for_comparison is called
        THEN: ProductNotFoundException should be raised with missing IDs
        """
        # Arrange
        existing_ids = [test_products_list[0].id, test_products_list[1].id]
        missing_id = uuid4()
        requested_ids = existing_ids + [missing_id]

        # Only return existing products
        mock_product_repository.find_by_ids.return_value = [
            test_products_list[0],
            test_products_list[1],
        ]

        # Act & Assert
        with pytest.raises(ProductNotFoundException) as exc_info:
            product_service.get_products_for_comparison(requested_ids)

        assert str(missing_id) in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()

    def test_should_raise_error_when_all_products_missing(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: None of the requested products exist
        WHEN: get_products_for_comparison is called
        THEN: ProductNotFoundException should be raised
        """
        # Arrange
        requested_ids = [uuid4(), uuid4()]
        mock_product_repository.find_by_ids.return_value = []

        # Act & Assert
        with pytest.raises(ProductNotFoundException):
            product_service.get_products_for_comparison(requested_ids)

    def test_should_raise_error_for_empty_id_list(
        self, product_service: ProductService
    ) -> None:
        """
        GIVEN: Empty list of product IDs
        WHEN: get_products_for_comparison is called
        THEN: ValueError should be raised
        """
        # Arrange
        empty_list: List[UUID] = []

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            product_service.get_products_for_comparison(empty_list)

        assert "at least one" in str(exc_info.value).lower()

    def test_should_raise_error_for_duplicate_ids(
        self,
        product_service: ProductService,
        mock_product_repository: Mock,
        test_products_list: List[Product],
    ) -> None:
        """
        GIVEN: List with duplicate product IDs
        WHEN: get_products_for_comparison is called
        THEN: ValueError should be raised
        """
        # Arrange
        product_id = test_products_list[0].id
        duplicate_ids = [product_id, product_id, test_products_list[1].id]

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            product_service.get_products_for_comparison(duplicate_ids)

        assert "unique" in str(exc_info.value).lower()

    def test_should_return_products_in_requested_order(
        self,
        product_service_with_data: ProductService,
        test_products_list: List[Product],
    ) -> None:
        """
        GIVEN: Products in repository
        WHEN: get_products_for_comparison is called with specific order
        THEN: Products should be returned in the same order as requested
        """
        # Arrange - Request in reverse order
        requested_ids = [
            test_products_list[4].id,
            test_products_list[2].id,
            test_products_list[0].id,
        ]

        # Act
        result = product_service_with_data.get_products_for_comparison(requested_ids)

        # Assert
        assert [p.id for p in result] == requested_ids

    def test_should_handle_single_product_id(
        self,
        product_service_with_data: ProductService,
        test_products_list: List[Product],
    ) -> None:
        """
        GIVEN: Single product ID in list
        WHEN: get_products_for_comparison is called
        THEN: Single product should be returned in list
        """
        # Arrange
        single_id = [test_products_list[0].id]

        # Act
        result = product_service_with_data.get_products_for_comparison(single_id)

        # Assert
        assert len(result) == 1
        assert result[0].id == single_id[0]

    def test_should_handle_maximum_batch_size(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: Large number of product IDs
        WHEN: get_products_for_comparison is called
        THEN: Should handle efficiently without errors
        """
        # Arrange
        num_products = 100
        products = []
        product_ids = []

        for i in range(num_products):
            product_id = uuid4()
            product = Product(
                id=product_id,
                name=f"Product {i}",
                image_url=f"https://example.com/product-{i}.jpg",
                description=f"Description {i}",
                price=100.00 + i,
                rating=4.0,
            )
            products.append(product)
            product_ids.append(product_id)

        mock_product_repository.find_by_ids.return_value = products

        # Act
        result = product_service.get_products_for_comparison(product_ids)

        # Assert
        assert len(result) == num_products
        assert [p.id for p in result] == product_ids


@pytest.mark.unit
class TestProductServiceGetAll:
    """Test suite for get_all_products method."""

    def test_should_return_all_products(
        self,
        product_service_with_data: ProductService,
        test_products_list: List[Product],
    ) -> None:
        """
        GIVEN: Products exist in repository
        WHEN: get_all_products is called
        THEN: All products should be returned
        """
        # Act
        result = product_service_with_data.get_all_products()

        # Assert
        assert len(result) == len(test_products_list)
        assert all(isinstance(p, Product) for p in result)

    def test_should_return_empty_list_when_no_products(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: No products in repository
        WHEN: get_all_products is called
        THEN: Empty list should be returned
        """
        # Arrange
        mock_product_repository.find_all.return_value = []

        # Act
        result = product_service.get_all_products()

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_should_call_repository_find_all(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: ProductService instance
        WHEN: get_all_products is called
        THEN: Repository's find_all method should be called
        """
        # Arrange
        mock_product_repository.find_all.return_value = []

        # Act
        product_service.get_all_products()

        # Assert
        mock_product_repository.find_all.assert_called_once()


@pytest.mark.unit
class TestProductServiceExists:
    """Test suite for product_exists method."""

    def test_should_return_true_when_product_exists(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: Product exists in repository
        WHEN: product_exists is called
        THEN: True should be returned
        """
        # Arrange
        product_id = uuid4()
        mock_product_repository.exists.return_value = True

        # Act
        result = product_service.product_exists(product_id)

        # Assert
        assert result is True
        mock_product_repository.exists.assert_called_once_with(product_id)

    def test_should_return_false_when_product_not_exists(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: Product doesn't exist in repository
        WHEN: product_exists is called
        THEN: False should be returned
        """
        # Arrange
        product_id = uuid4()
        mock_product_repository.exists.return_value = False

        # Act
        result = product_service.product_exists(product_id)

        # Assert
        assert result is False
        mock_product_repository.exists.assert_called_once_with(product_id)


@pytest.mark.unit
class TestProductServiceCount:
    """Test suite for get_product_count method."""

    def test_should_return_correct_count(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: Multiple products in repository
        WHEN: get_product_count is called
        THEN: Correct count should be returned
        """
        # Arrange
        expected_count = 42
        mock_product_repository.count.return_value = expected_count

        # Act
        result = product_service.get_product_count()

        # Assert
        assert result == expected_count
        mock_product_repository.count.assert_called_once()

    def test_should_return_zero_when_no_products(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: No products in repository
        WHEN: get_product_count is called
        THEN: Zero should be returned
        """
        # Arrange
        mock_product_repository.count.return_value = 0

        # Act
        result = product_service.get_product_count()

        # Assert
        assert result == 0


@pytest.mark.unit
class TestProductServiceEdgeCases:
    """Test edge cases and error handling."""

    def test_should_preserve_product_order_with_mixed_ids(
        self,
        product_service_with_data: ProductService,
        test_products_list: List[Product],
    ) -> None:
        """
        GIVEN: Products requested in non-sequential order
        WHEN: get_products_for_comparison is called
        THEN: Exact order should be preserved
        """
        # Arrange - Request in specific mixed order
        requested_order = [
            test_products_list[3].id,
            test_products_list[0].id,
            test_products_list[4].id,
            test_products_list[1].id,
        ]

        # Act
        result = product_service_with_data.get_products_for_comparison(requested_order)

        # Assert
        result_ids = [p.id for p in result]
        assert result_ids == requested_order

    def test_should_handle_repository_returning_different_order(
        self, product_service: ProductService, mock_product_repository: Mock
    ) -> None:
        """
        GIVEN: Repository returns products in different order than requested
        WHEN: get_products_for_comparison is called
        THEN: Service should reorder to match request
        """
        # Arrange
        product_1 = Product(
            id=uuid4(),
            name="Product 1",
            image_url="https://example.com/1.jpg",
            description="First",
            price=100,
            rating=4.0,
        )
        product_2 = Product(
            id=uuid4(),
            name="Product 2",
            image_url="https://example.com/2.jpg",
            description="Second",
            price=200,
            rating=4.5,
        )
        product_3 = Product(
            id=uuid4(),
            name="Product 3",
            image_url="https://example.com/3.jpg",
            description="Third",
            price=300,
            rating=5.0,
        )

        # Request order: 3, 1, 2
        requested_ids = [product_3.id, product_1.id, product_2.id]

        # Repository returns in different order: 1, 2, 3
        mock_product_repository.find_by_ids.return_value = [
            product_1,
            product_2,
            product_3,
        ]

        # Act
        result = product_service.get_products_for_comparison(requested_ids)

        # Assert - Should match requested order, not repository order
        assert [p.id for p in result] == requested_ids
        assert result[0] == product_3
        assert result[1] == product_1
        assert result[2] == product_2
