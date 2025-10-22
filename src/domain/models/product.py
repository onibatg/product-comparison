"""
Domain model for Product entity.

This module defines the core Product entity that represents an item in the
comparison system. It follows domain-driven design principles and is
independent of any infrastructure concerns.
"""

from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Product(BaseModel):
    """
    Product entity representing an item available for comparison.

    This is the core domain model that encapsulates all product information
    needed for the comparison feature. Uses Pydantic for data validation
    and type safety.

    Attributes:
        id: Unique identifier for the product (UUID)
        name: Product name/title
        image_url: URL to the product image
        description: Detailed product description
        price: Product price (uses Decimal for precision)
        rating: Product rating (0.0 to 5.0)
        specifications: Flexible key-value pairs for product specifications
        currency: Currency code (default: USD)
    """

    id: UUID = Field(default_factory=uuid4, description="Unique product identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    image_url: HttpUrl = Field(..., description="URL to product image")
    description: str = Field(
        ..., min_length=1, max_length=2000, description="Product description"
    )
    price: Decimal = Field(
        ..., gt=0, decimal_places=2, description="Product price"
    )
    rating: float = Field(
        ..., ge=0.0, le=5.0, description="Product rating (0.0 to 5.0)"
    )
    specifications: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible key-value pairs for product specifications"
    )
    currency: str = Field(
        default="USD", min_length=3, max_length=3, description="Currency code (ISO 4217)"
    )

    @field_validator("currency")
    @classmethod
    def validate_currency_uppercase(cls, value: str) -> str:
        """
        Ensure currency code is uppercase.

        Args:
            value: Currency code to validate

        Returns:
            Uppercase currency code
        """
        return value.upper()

    class Config:
        """Pydantic model configuration."""

        json_encoders = {
            Decimal: lambda v: float(v),
            UUID: lambda v: str(v),
        }
        # Allow arbitrary precision for decimals
        arbitrary_types_allowed = False
        # Use enum values instead of enum objects
        use_enum_values = True


class ProductResponse(BaseModel):
    """
    Product response model for API endpoints.

    This model represents how Product data is serialized for API responses.
    Separating this from the domain model allows us to control the API
    contract independently from domain logic.

    Attributes:
        id: Unique product identifier (as string)
        name: Product name
        image_url: URL to product image
        description: Product description
        price: Product price (as float)
        rating: Product rating
        specifications: Product specifications
        currency: Currency code
    """

    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    image_url: str = Field(..., description="URL to product image")
    description: str = Field(..., description="Product description")
    price: float = Field(..., description="Product price")
    rating: float = Field(..., description="Product rating (0.0 to 5.0)")
    specifications: Dict[str, Any] = Field(
        ..., description="Product specifications"
    )
    currency: str = Field(..., description="Currency code")

    @classmethod
    def from_product(cls, product: Product) -> "ProductResponse":
        """
        Create a ProductResponse from a Product domain model.

        Args:
            product: Product domain model instance

        Returns:
            ProductResponse instance
        """
        return cls(
            id=str(product.id),
            name=product.name,
            image_url=str(product.image_url),
            description=product.description,
            price=float(product.price),
            rating=product.rating,
            specifications=product.specifications,
            currency=product.currency,
        )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Premium Wireless Headphones",
                "image_url": "https://example.com/images/headphones.jpg",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 299.99,
                "rating": 4.5,
                "specifications": {
                    "brand": "AudioTech",
                    "color": "Black",
                    "battery_life": "30 hours",
                    "connectivity": "Bluetooth 5.0",
                    "noise_cancellation": True
                },
                "currency": "USD"
            }
        }
