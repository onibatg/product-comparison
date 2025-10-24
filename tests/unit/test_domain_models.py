"""
Unit tests for domain models.

This module tests the Product and ProductResponse models, including validation,
serialization, and deserialization. All tests are isolated and use no external
dependencies.
"""

from decimal import Decimal
from typing import Any, Dict
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.domain.models.product import Product, ProductResponse


@pytest.mark.unit
class TestProductModel:
    """Test suite for Product domain model."""

    def test_should_create_valid_product_with_all_fields(
        self, test_product_data: Dict[str, Any]
    ) -> None:
        """
        GIVEN: Valid product data with all fields
        WHEN: Product is instantiated
        THEN: Product should be created successfully with correct values
        """
        # Arrange & Act
        product = Product(**test_product_data)

        # Assert
        assert product.id == UUID(test_product_data["id"])
        assert product.name == test_product_data["name"]
        assert str(product.image_url) == test_product_data["image_url"]
        assert product.description == test_product_data["description"]
        assert product.price == test_product_data["price"]
        assert product.rating == test_product_data["rating"]
        assert product.currency == test_product_data["currency"]
        assert product.specifications == test_product_data["specifications"]

    def test_should_create_product_with_minimal_required_fields(self) -> None:
        """
        GIVEN: Product data with only required fields
        WHEN: Product is instantiated
        THEN: Product should be created with default values for optional fields
        """
        # Arrange
        minimal_data = {
            "name": "Minimal Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Minimal description",
            "price": Decimal("99.99"),
            "rating": 4.5,
        }

        # Act
        product = Product(**minimal_data)

        # Assert
        assert isinstance(product.id, UUID)
        assert product.name == "Minimal Product"
        assert product.currency == "USD"  # Default value
        assert product.specifications == {}  # Default empty dict

    def test_should_reject_negative_price(self) -> None:
        """
        GIVEN: Product data with negative price
        WHEN: Product is instantiated
        THEN: ValidationError should be raised
        """
        # Arrange
        invalid_data = {
            "name": "Invalid Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Product with invalid price",
            "price": Decimal("-10.50"),
            "rating": 4.5,
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Product(**invalid_data)

        assert "price" in str(exc_info.value).lower()

    def test_should_reject_zero_price(self) -> None:
        """
        GIVEN: Product data with zero price
        WHEN: Product is instantiated
        THEN: ValidationError should be raised
        """
        # Arrange
        invalid_data = {
            "name": "Free Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Product with zero price",
            "price": Decimal("0.00"),
            "rating": 4.5,
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Product(**invalid_data)

        assert "price" in str(exc_info.value).lower()

    @pytest.mark.parametrize("invalid_rating", [-1.0, 5.5, 10.0, -0.1])
    def test_should_reject_rating_out_of_range(self, invalid_rating: float) -> None:
        """
        GIVEN: Product data with rating outside 0.0-5.0 range
        WHEN: Product is instantiated
        THEN: ValidationError should be raised
        """
        # Arrange
        invalid_data = {
            "name": "Invalid Rating Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Product with invalid rating",
            "price": Decimal("99.99"),
            "rating": invalid_rating,
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Product(**invalid_data)

        assert "rating" in str(exc_info.value).lower()

    @pytest.mark.parametrize("valid_rating", [0.0, 2.5, 5.0, 4.75])
    def test_should_accept_valid_ratings(self, valid_rating: float) -> None:
        """
        GIVEN: Product data with valid rating (0.0 to 5.0)
        WHEN: Product is instantiated
        THEN: Product should be created successfully
        """
        # Arrange
        valid_data = {
            "name": "Valid Rating Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Product with valid rating",
            "price": Decimal("99.99"),
            "rating": valid_rating,
        }

        # Act
        product = Product(**valid_data)

        # Assert
        assert product.rating == valid_rating

    def test_should_reject_empty_product_name(self) -> None:
        """
        GIVEN: Product data with empty name
        WHEN: Product is instantiated
        THEN: ValidationError should be raised
        """
        # Arrange
        invalid_data = {
            "name": "",
            "image_url": "https://example.com/image.jpg",
            "description": "Product with empty name",
            "price": Decimal("99.99"),
            "rating": 4.5,
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Product(**invalid_data)

        assert "name" in str(exc_info.value).lower()

    def test_should_reject_too_long_product_name(self) -> None:
        """
        GIVEN: Product data with name exceeding max length (200 chars)
        WHEN: Product is instantiated
        THEN: ValidationError should be raised
        """
        # Arrange
        invalid_data = {
            "name": "A" * 201,  # Exceeds max_length=200
            "image_url": "https://example.com/image.jpg",
            "description": "Product with too long name",
            "price": Decimal("99.99"),
            "rating": 4.5,
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Product(**invalid_data)

        assert "name" in str(exc_info.value).lower()

    def test_should_reject_invalid_image_url(self) -> None:
        """
        GIVEN: Product data with invalid URL format
        WHEN: Product is instantiated
        THEN: ValidationError should be raised
        """
        # Arrange
        invalid_data = {
            "name": "Invalid URL Product",
            "image_url": "not-a-valid-url",
            "description": "Product with invalid URL",
            "price": Decimal("99.99"),
            "rating": 4.5,
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Product(**invalid_data)

        assert "image_url" in str(exc_info.value).lower()

    def test_should_convert_currency_to_uppercase(self) -> None:
        """
        GIVEN: Product data with lowercase currency code
        WHEN: Product is instantiated
        THEN: Currency should be converted to uppercase
        """
        # Arrange
        data = {
            "name": "Currency Test Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Testing currency conversion",
            "price": Decimal("99.99"),
            "rating": 4.5,
            "currency": "usd",  # Lowercase
        }

        # Act
        product = Product(**data)

        # Assert
        assert product.currency == "USD"

    def test_should_accept_complex_specifications(self) -> None:
        """
        GIVEN: Product data with nested specifications
        WHEN: Product is instantiated
        THEN: Specifications should be stored correctly
        """
        # Arrange
        complex_specs = {
            "brand": "TestBrand",
            "dimensions": {"width": 10, "height": 20, "depth": 5},
            "features": ["feature1", "feature2", "feature3"],
            "warranty": {"years": 2, "type": "limited"},
            "available": True,
            "special_chars": "Test with émojis 🎉 and unicode ñ",
        }

        data = {
            "name": "Complex Specs Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Product with complex specifications",
            "price": Decimal("99.99"),
            "rating": 4.5,
            "specifications": complex_specs,
        }

        # Act
        product = Product(**data)

        # Assert
        assert product.specifications == complex_specs
        assert product.specifications["dimensions"]["width"] == 10
        assert "feature2" in product.specifications["features"]

    def test_should_handle_unicode_in_text_fields(self) -> None:
        """
        GIVEN: Product data with unicode characters
        WHEN: Product is instantiated
        THEN: Unicode should be preserved correctly
        """
        # Arrange
        data = {
            "name": "Produit français avec émojis 🎉",
            "image_url": "https://example.com/image.jpg",
            "description": "Descripción en español con ñ y acentos: café",
            "price": Decimal("99.99"),
            "rating": 4.5,
        }

        # Act
        product = Product(**data)

        # Assert
        assert "français" in product.name
        assert "🎉" in product.name
        assert "español" in product.description
        assert "café" in product.description


@pytest.mark.unit
class TestProductResponse:
    """Test suite for ProductResponse model."""

    def test_should_create_product_response_from_product(
        self, test_product: Product
    ) -> None:
        """
        GIVEN: A valid Product domain model
        WHEN: ProductResponse.from_product() is called
        THEN: ProductResponse should be created with correct field types
        """
        # Act
        response = ProductResponse.from_product(test_product)

        # Assert
        assert isinstance(response.id, str)
        assert response.id == str(test_product.id)
        assert response.name == test_product.name
        assert isinstance(response.image_url, str)
        assert isinstance(response.price, float)
        assert response.price == float(test_product.price)
        assert response.rating == test_product.rating
        assert response.currency == test_product.currency
        assert response.specifications == test_product.specifications

    def test_should_convert_uuid_to_string(self, test_product: Product) -> None:
        """
        GIVEN: Product with UUID id
        WHEN: Converting to ProductResponse
        THEN: UUID should be converted to string
        """
        # Act
        response = ProductResponse.from_product(test_product)

        # Assert
        assert isinstance(response.id, str)
        # Verify it's a valid UUID string
        UUID(response.id)

    def test_should_convert_decimal_price_to_float(self) -> None:
        """
        GIVEN: Product with Decimal price
        WHEN: Converting to ProductResponse
        THEN: Price should be converted to float
        """
        # Arrange
        product = Product(
            name="Price Conversion Test",
            image_url="https://example.com/image.jpg",
            description="Testing price conversion",
            price=Decimal("123.45"),
            rating=4.5,
        )

        # Act
        response = ProductResponse.from_product(product)

        # Assert
        assert isinstance(response.price, float)
        assert response.price == 123.45

    def test_should_serialize_to_json_compatible_dict(
        self, test_product: Product
    ) -> None:
        """
        GIVEN: ProductResponse instance
        WHEN: Serializing to dict
        THEN: All fields should be JSON-compatible types
        """
        # Arrange
        response = ProductResponse.from_product(test_product)

        # Act
        response_dict = response.model_dump()

        # Assert
        assert isinstance(response_dict["id"], str)
        assert isinstance(response_dict["name"], str)
        assert isinstance(response_dict["price"], float)
        assert isinstance(response_dict["rating"], float)
        assert isinstance(response_dict["specifications"], dict)

    def test_should_preserve_all_product_data(self, test_product: Product) -> None:
        """
        GIVEN: Product with complete data
        WHEN: Converting to ProductResponse and back to dict
        THEN: No data should be lost
        """
        # Act
        response = ProductResponse.from_product(test_product)
        response_dict = response.model_dump()

        # Assert
        assert response_dict["name"] == test_product.name
        assert response_dict["description"] == test_product.description
        assert response_dict["currency"] == test_product.currency
        assert (
            response_dict["specifications"]["brand"]
            == test_product.specifications["brand"]
        )


@pytest.mark.unit
class TestProductModelEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_should_handle_very_long_description(self) -> None:
        """
        GIVEN: Product with description at max length (2000 chars)
        WHEN: Product is instantiated
        THEN: Product should be created successfully
        """
        # Arrange
        long_description = "A" * 2000  # Exactly max length

        data = {
            "name": "Long Description Product",
            "image_url": "https://example.com/image.jpg",
            "description": long_description,
            "price": Decimal("99.99"),
            "rating": 4.5,
        }

        # Act
        product = Product(**data)

        # Assert
        assert len(product.description) == 2000

    def test_should_reject_too_long_description(self) -> None:
        """
        GIVEN: Product with description exceeding max length
        WHEN: Product is instantiated
        THEN: ValidationError should be raised
        """
        # Arrange
        too_long_description = "A" * 2001  # Exceeds max_length

        data = {
            "name": "Too Long Description",
            "image_url": "https://example.com/image.jpg",
            "description": too_long_description,
            "price": Decimal("99.99"),
            "rating": 4.5,
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Product(**data)

        assert "description" in str(exc_info.value).lower()

    def test_should_handle_very_small_price(self) -> None:
        """
        GIVEN: Product with very small positive price
        WHEN: Product is instantiated
        THEN: Product should be created successfully
        """
        # Arrange
        data = {
            "name": "Cheap Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Very cheap product",
            "price": Decimal("0.01"),
            "rating": 4.5,
        }

        # Act
        product = Product(**data)

        # Assert
        assert product.price == Decimal("0.01")

    def test_should_handle_very_large_price(self) -> None:
        """
        GIVEN: Product with very large price
        WHEN: Product is instantiated
        THEN: Product should be created successfully
        """
        # Arrange
        data = {
            "name": "Expensive Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Very expensive product",
            "price": Decimal("999999.99"),
            "rating": 4.5,
        }

        # Act
        product = Product(**data)

        # Assert
        assert product.price == Decimal("999999.99")

    def test_should_handle_empty_specifications(self) -> None:
        """
        GIVEN: Product with empty specifications dict
        WHEN: Product is instantiated
        THEN: Product should be created with empty dict
        """
        # Arrange
        data = {
            "name": "No Specs Product",
            "image_url": "https://example.com/image.jpg",
            "description": "Product without specifications",
            "price": Decimal("99.99"),
            "rating": 4.5,
            "specifications": {},
        }

        # Act
        product = Product(**data)

        # Assert
        assert product.specifications == {}

    def test_should_reject_invalid_currency_length(self) -> None:
        """
        GIVEN: Product with currency code not 3 characters
        WHEN: Product is instantiated
        THEN: ValidationError should be raised
        """
        # Arrange - Too short
        data = {
            "name": "Invalid Currency",
            "image_url": "https://example.com/image.jpg",
            "description": "Product with invalid currency",
            "price": Decimal("99.99"),
            "rating": 4.5,
            "currency": "US",  # Too short
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Product(**data)

        assert "currency" in str(exc_info.value).lower()
