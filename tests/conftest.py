"""
Shared pytest fixtures for all tests.

This module provides common fixtures used across unit, integration, and e2e tests.
Following the DRY principle, fixtures are centralized here to avoid duplication.
"""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models.product import Product, ProductResponse
from src.domain.ports.product_repository import ProductRepositoryPort
from src.domain.services.product_service import ProductService
from src.infrastructure.repositories.json_product_repository import (
    JsonProductRepository,
)
from src.main import create_application


# ==============================================================================
# TEST DATA FIXTURES
# ==============================================================================


@pytest.fixture
def test_product_data() -> Dict[str, Any]:
    """
    Minimal valid product data for testing.

    Returns:
        Dictionary with valid product fields
    """
    return {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "name": "Test Product",
        "image_url": "https://example.com/test-product.jpg",
        "description": "Test product description for testing purposes",
        "price": Decimal("99.99"),
        "rating": 4.5,
        "currency": "USD",
        "specifications": {
            "brand": "TestBrand",
            "color": "Blue",
            "weight": "100g",
        },
    }


@pytest.fixture
def test_product(test_product_data: Dict[str, Any]) -> Product:
    """
    Valid Product domain model instance.

    Args:
        test_product_data: Product data fixture

    Returns:
        Product instance
    """
    return Product(**test_product_data)


@pytest.fixture
def test_products_list() -> List[Product]:
    """
    List of test products for batch operations.

    Returns:
        List of 5 Product instances
    """
    products = []
    for i in range(5):
        product = Product(
            id=uuid4(),
            name=f"Test Product {i+1}",
            image_url=f"https://example.com/product-{i+1}.jpg",
            description=f"Description for test product {i+1}",
            price=Decimal(str(100.00 + (i * 50))),
            rating=4.0 + (i * 0.1),
            currency="USD",
            specifications={"brand": "TestBrand", "index": i + 1},
        )
        products.append(product)
    return products


@pytest.fixture
def test_product_ids(test_products_list: List[Product]) -> List[UUID]:
    """
    List of product UUIDs from test products.

    Args:
        test_products_list: List of test products

    Returns:
        List of UUIDs
    """
    return [product.id for product in test_products_list]


@pytest.fixture
def sample_products_file_path() -> Path:
    """
    Path to test products JSON file.

    Returns:
        Path to fixtures/test_products.json
    """
    return Path(__file__).parent / "fixtures" / "test_products.json"


@pytest.fixture
def sample_products_data(sample_products_file_path: Path) -> List[Dict[str, Any]]:
    """
    Load sample products from JSON fixture file.

    Args:
        sample_products_file_path: Path to test data file

    Returns:
        List of product dictionaries
    """
    with open(sample_products_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["products"]


# ==============================================================================
# MOCK FIXTURES
# ==============================================================================


@pytest.fixture
def mock_product_repository() -> Mock:
    """
    Mock ProductRepositoryPort for unit testing.

    Returns:
        Mock repository with spec
    """
    return Mock(spec=ProductRepositoryPort)


@pytest.fixture
def mock_product_repository_with_data(
    mock_product_repository: Mock, test_products_list: List[Product]
) -> Mock:
    """
    Mock repository pre-configured with test data.

    Args:
        mock_product_repository: Base mock repository
        test_products_list: Test products to return

    Returns:
        Configured mock repository
    """
    # Configure find_by_id
    def mock_find_by_id(product_id: UUID):
        for product in test_products_list:
            if product.id == product_id:
                return product
        return None

    # Configure find_by_ids
    def mock_find_by_ids(product_ids: List[UUID]):
        return [p for p in test_products_list if p.id in product_ids]

    # Configure find_all
    def mock_find_all():
        return test_products_list

    # Configure exists
    def mock_exists(product_id: UUID):
        return any(p.id == product_id for p in test_products_list)

    # Configure count
    def mock_count():
        return len(test_products_list)

    mock_product_repository.find_by_id.side_effect = mock_find_by_id
    mock_product_repository.find_by_ids.side_effect = mock_find_by_ids
    mock_product_repository.find_all.side_effect = mock_find_all
    mock_product_repository.exists.side_effect = mock_exists
    mock_product_repository.count.side_effect = mock_count

    return mock_product_repository


# ==============================================================================
# SERVICE FIXTURES
# ==============================================================================


@pytest.fixture
def product_service(mock_product_repository: Mock) -> ProductService:
    """
    ProductService with mocked repository dependency.

    Args:
        mock_product_repository: Mock repository

    Returns:
        ProductService instance
    """
    return ProductService(product_repository=mock_product_repository)


@pytest.fixture
def product_service_with_data(
    mock_product_repository_with_data: Mock,
) -> ProductService:
    """
    ProductService with pre-configured mock data.

    Args:
        mock_product_repository_with_data: Mock repository with test data

    Returns:
        ProductService instance
    """
    return ProductService(product_repository=mock_product_repository_with_data)


# ==============================================================================
# REPOSITORY FIXTURES
# ==============================================================================


@pytest.fixture
def json_repository(sample_products_file_path: Path) -> JsonProductRepository:
    """
    Real JsonProductRepository for integration testing.

    Args:
        sample_products_file_path: Path to test data file

    Returns:
        JsonProductRepository instance
    """
    return JsonProductRepository(data_file_path=str(sample_products_file_path))


# ==============================================================================
# API CLIENT FIXTURES
# ==============================================================================


@pytest.fixture
async def test_client() -> AsyncClient:
    """
    Async HTTP client for testing FastAPI endpoints.

    Yields:
        AsyncClient instance with test app
    """
    app = create_application()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_client_with_test_data(
    sample_products_file_path: Path,
) -> AsyncClient:
    """
    Async HTTP client configured with test data.

    This fixture overrides the dependency injection to use test data.

    Args:
        sample_products_file_path: Path to test data file

    Yields:
        AsyncClient instance
    """
    app = create_application()

    # Override dependency to use test data
    from src.api.dependencies import get_product_service

    def override_get_product_service():
        repository = JsonProductRepository(data_file_path=str(sample_products_file_path))
        return ProductService(product_repository=repository)

    app.dependency_overrides[get_product_service] = override_get_product_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ==============================================================================
# PARAMETRIZE FIXTURES
# ==============================================================================


@pytest.fixture(params=[
    "",  # Empty string
    "not-a-uuid",  # Invalid format
    "12345",  # Numeric
    "f47ac10b-58cc-4372",  # Incomplete UUID
])
def invalid_uuid_string(request) -> str:
    """
    Parametrized fixture for invalid UUID strings.

    Returns:
        Invalid UUID string
    """
    return request.param


@pytest.fixture(params=[
    -10.50,  # Negative price
    0.00,  # Zero price
])
def invalid_price(request) -> float:
    """
    Parametrized fixture for invalid prices.

    Returns:
        Invalid price value
    """
    return request.param


@pytest.fixture(params=[
    -1.0,  # Below minimum
    5.5,  # Above maximum
    10.0,  # Way above
])
def invalid_rating(request) -> float:
    """
    Parametrized fixture for invalid ratings.

    Returns:
        Invalid rating value
    """
    return request.param
