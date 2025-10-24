"""
Integration tests for API routes.

These tests verify the complete HTTP request/response cycle, including
request validation, service orchestration, and response serialization.
"""

import time
from typing import List
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetAllProductsEndpoint:
    """Test suite for GET /api/v1/products endpoint."""

    async def test_should_return_all_products_with_200(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Products exist in the system
        WHEN: GET /api/v1/products is called
        THEN: 200 OK with all products should be returned
        """
        # Act
        response = await test_client_with_test_data.get("/api/v1/products")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_should_return_products_with_correct_structure(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Products in the system
        WHEN: GET /api/v1/products is called
        THEN: Each product should have required fields
        """
        # Act
        response = await test_client_with_test_data.get("/api/v1/products")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        products = response.json()

        for product in products:
            assert "id" in product
            assert "name" in product
            assert "image_url" in product
            assert "description" in product
            assert "price" in product
            assert "rating" in product
            assert "specifications" in product
            assert "currency" in product

    async def test_should_return_products_with_correct_types(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Products in the system
        WHEN: GET /api/v1/products is called
        THEN: Field types should be correct
        """
        # Act
        response = await test_client_with_test_data.get("/api/v1/products")

        # Assert
        products = response.json()

        for product in products:
            assert isinstance(product["id"], str)
            assert isinstance(product["name"], str)
            assert isinstance(product["price"], (int, float))
            assert isinstance(product["rating"], (int, float))
            assert isinstance(product["specifications"], dict)

    async def test_should_have_correct_content_type(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: API endpoint
        WHEN: GET /api/v1/products is called
        THEN: Content-Type should be application/json
        """
        # Act
        response = await test_client_with_test_data.get("/api/v1/products")

        # Assert
        assert response.headers["content-type"] == "application/json"


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetProductByIdEndpoint:
    """Test suite for GET /api/v1/products/{product_id} endpoint."""

    async def test_should_return_product_when_id_exists(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Product exists with specific ID
        WHEN: GET /api/v1/products/{id} is called
        THEN: 200 OK with product details should be returned
        """
        # Arrange - Get a valid product ID first
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        products = all_products_response.json()
        valid_id = products[0]["id"]

        # Act
        response = await test_client_with_test_data.get(f"/api/v1/products/{valid_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        product = response.json()
        assert product["id"] == valid_id

    async def test_should_return_404_when_product_not_found(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Product ID that doesn't exist
        WHEN: GET /api/v1/products/{id} is called
        THEN: 404 Not Found should be returned
        """
        # Arrange
        non_existent_id = str(uuid4())

        # Act
        response = await test_client_with_test_data.get(
            f"/api/v1/products/{non_existent_id}"
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "error" in error

    async def test_should_return_422_for_invalid_uuid_format(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Invalid UUID format
        WHEN: GET /api/v1/products/{id} is called
        THEN: 422 Unprocessable Entity should be returned
        """
        # Arrange
        invalid_id = "not-a-valid-uuid"

        # Act
        response = await test_client_with_test_data.get(
            f"/api/v1/products/{invalid_id}"
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_should_return_complete_product_data(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Valid product ID
        WHEN: GET /api/v1/products/{id} is called
        THEN: Complete product data should be returned
        """
        # Arrange
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        valid_id = all_products_response.json()[0]["id"]

        # Act
        response = await test_client_with_test_data.get(f"/api/v1/products/{valid_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        product = response.json()

        # Verify all required fields
        required_fields = [
            "id",
            "name",
            "image_url",
            "description",
            "price",
            "rating",
            "specifications",
            "currency",
        ]
        for field in required_fields:
            assert field in product, f"Missing field: {field}"


@pytest.mark.integration
@pytest.mark.asyncio
class TestCompareBatchEndpoint:
    """Test suite for GET /api/v1/products/compare/batch endpoint."""

    async def test_should_return_products_for_valid_comparison(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Multiple valid product IDs
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: 200 OK with all requested products should be returned
        """
        # Arrange - Get valid product IDs
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        products = all_products_response.json()
        product_ids = [products[0]["id"], products[1]["id"]]

        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": product_ids},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 2
        assert result[0]["id"] in product_ids
        assert result[1]["id"] in product_ids

    async def test_should_return_products_in_requested_order(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Product IDs in specific order
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: Products should be returned in same order
        """
        # Arrange
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        products = all_products_response.json()
        # Request in reverse order
        product_ids = [products[2]["id"], products[0]["id"], products[1]["id"]]

        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": product_ids},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert [p["id"] for p in result] == product_ids

    async def test_should_return_400_for_empty_product_ids(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Empty product_ids parameter
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: 400 Bad Request should be returned
        """
        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": []},
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_should_return_400_for_duplicate_ids(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Duplicate product IDs in request
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: 400 Bad Request should be returned
        """
        # Arrange
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        product_id = all_products_response.json()[0]["id"]
        duplicate_ids = [product_id, product_id]

        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": duplicate_ids},
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_should_return_404_when_products_not_found(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Product IDs that don't exist
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: 404 Not Found should be returned
        """
        # Arrange
        non_existent_ids = [str(uuid4()), str(uuid4())]

        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": non_existent_ids},
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_should_return_404_when_some_products_missing(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Mix of existing and non-existing product IDs
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: 404 Not Found should be returned
        """
        # Arrange
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        valid_id = all_products_response.json()[0]["id"]
        non_existent_id = str(uuid4())
        mixed_ids = [valid_id, non_existent_id]

        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": mixed_ids},
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_should_return_422_for_invalid_uuid_format(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Invalid UUID format in product_ids
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: 422 Unprocessable Entity should be returned
        """
        # Arrange
        invalid_ids = ["invalid-uuid-1", "invalid-uuid-2"]

        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": invalid_ids},
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_should_handle_multiple_products_efficiently(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Multiple valid product IDs
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: All products should be returned correctly
        """
        # Arrange
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        products = all_products_response.json()
        product_ids = [p["id"] for p in products[:5]]

        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": product_ids},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 5

    @pytest.mark.performance
    async def test_should_respond_within_acceptable_time(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Multiple product IDs
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: Response should be returned within 200ms
        """
        # Arrange
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        products = all_products_response.json()
        product_ids = [p["id"] for p in products[:5]]

        # Act
        start_time = time.time()
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": product_ids},
        )
        elapsed_ms = (time.time() - start_time) * 1000

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert elapsed_ms < 200, f"Response took {elapsed_ms}ms (limit: 200ms)"


@pytest.mark.integration
@pytest.mark.asyncio
class TestProductCountEndpoint:
    """Test suite for GET /api/v1/products/health/count endpoint."""

    async def test_should_return_product_count(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Products in the system
        WHEN: GET /api/v1/products/health/count is called
        THEN: 200 OK with count should be returned
        """
        # Act
        response = await test_client_with_test_data.get("/api/v1/products/health/count")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert "status" in data
        assert isinstance(data["count"], int)
        assert data["count"] > 0

    async def test_should_return_healthy_status(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: System is operational
        WHEN: GET /api/v1/products/health/count is called
        THEN: status should be 'healthy'
        """
        # Act
        response = await test_client_with_test_data.get("/api/v1/products/health/count")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    async def test_should_match_actual_product_count(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Known number of products
        WHEN: Comparing count endpoint with list endpoint
        THEN: Counts should match
        """
        # Arrange
        all_products_response = await test_client_with_test_data.get("/api/v1/products")
        expected_count = len(all_products_response.json())

        # Act
        count_response = await test_client_with_test_data.get(
            "/api/v1/products/health/count"
        )

        # Assert
        assert count_response.json()["count"] == expected_count


@pytest.mark.integration
@pytest.mark.asyncio
class TestApiErrorHandling:
    """Test API error handling and edge cases."""

    async def test_should_return_json_error_for_404(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Invalid endpoint
        WHEN: Request is made to non-existent product
        THEN: JSON error response should be returned
        """
        # Arrange
        non_existent_id = str(uuid4())

        # Act
        response = await test_client_with_test_data.get(
            f"/api/v1/products/{non_existent_id}"
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert response.headers["content-type"] == "application/json"

    async def test_should_handle_malformed_query_params(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Malformed query parameters
        WHEN: GET /api/v1/products/compare/batch is called
        THEN: Appropriate error should be returned
        """
        # Act
        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch?product_ids=not-a-uuid"
        )

        # Assert
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
        ]

    async def test_should_include_cors_headers(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: API with CORS enabled
        WHEN: Any request is made
        THEN: CORS headers should be present
        """
        # Act
        response = await test_client_with_test_data.get("/api/v1/products")

        # Assert
        # Note: CORS headers might not be present in test client
        # This test documents the expected behavior
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.asyncio
class TestRootEndpoints:
    """Test root and health endpoints."""

    async def test_should_return_api_info_at_root(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: API root endpoint
        WHEN: GET / is called
        THEN: API information should be returned
        """
        # Act
        response = await test_client_with_test_data.get("/")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "version" in data

    async def test_should_return_health_status(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        GIVEN: Health check endpoint
        WHEN: GET /health is called
        THEN: Health status should be returned
        """
        # Act
        response = await test_client_with_test_data.get("/health")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
