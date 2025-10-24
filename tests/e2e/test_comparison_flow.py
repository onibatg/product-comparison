"""
End-to-end tests for complete comparison workflows.

These tests verify complete user journeys through the API, testing
real-world scenarios without mocks.
"""

import time

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.e2e
@pytest.mark.asyncio
class TestComparisonWorkflowE2E:
    """End-to-end tests for product comparison workflow."""

    async def test_complete_comparison_workflow(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Complete workflow: List products → Select products → Compare

        GIVEN: User wants to compare products
        WHEN: User lists products, selects some, and compares them
        THEN: Complete workflow should succeed
        """
        # Step 1: Get list of all available products
        list_response = await test_client_with_test_data.get("/api/v1/products")

        # Assert list endpoint works
        assert list_response.status_code == status.HTTP_200_OK
        all_products = list_response.json()
        assert len(all_products) > 0

        # Step 2: Select products to compare (take first 3)
        selected_products = all_products[:3]
        selected_ids = [p["id"] for p in selected_products]

        # Step 3: Compare selected products
        compare_response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": selected_ids},
        )

        # Assert comparison works
        assert compare_response.status_code == status.HTTP_200_OK
        compared_products = compare_response.json()
        assert len(compared_products) == 3

        # Verify returned products match selected ones
        compared_ids = [p["id"] for p in compared_products]
        assert compared_ids == selected_ids

        # Step 4: Get details for one specific product
        detail_response = await test_client_with_test_data.get(
            f"/api/v1/products/{selected_ids[0]}"
        )

        # Assert detail endpoint works
        assert detail_response.status_code == status.HTTP_200_OK
        product_detail = detail_response.json()
        assert product_detail["id"] == selected_ids[0]

    async def test_workflow_with_product_verification(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Workflow with product existence verification.

        GIVEN: User wants to verify products exist before comparing
        WHEN: User checks products and then compares them
        THEN: Workflow should complete successfully
        """
        # Step 1: Get all products
        list_response = await test_client_with_test_data.get("/api/v1/products")
        products = list_response.json()

        # Step 2: Verify individual products exist
        for product in products[:2]:
            detail_response = await test_client_with_test_data.get(
                f"/api/v1/products/{product['id']}"
            )
            assert detail_response.status_code == status.HTTP_200_OK

        # Step 3: Compare verified products
        product_ids = [p["id"] for p in products[:2]]
        compare_response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": product_ids},
        )

        assert compare_response.status_code == status.HTTP_200_OK
        assert len(compare_response.json()) == 2

    async def test_workflow_with_maximum_products(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Compare maximum number of products.

        GIVEN: User wants to compare maximum allowed products
        WHEN: User selects and compares up to 5 products
        THEN: Comparison should succeed with all products
        """
        # Step 1: Get products
        list_response = await test_client_with_test_data.get("/api/v1/products")
        products = list_response.json()

        # Step 2: Select up to 5 products (or all if less than 5)
        num_to_compare = min(5, len(products))
        selected_ids = [p["id"] for p in products[:num_to_compare]]

        # Step 3: Compare
        compare_response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": selected_ids},
        )

        # Assert
        assert compare_response.status_code == status.HTTP_200_OK
        result = compare_response.json()
        assert len(result) == num_to_compare

    async def test_workflow_with_price_comparison(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Compare products and verify price information.

        GIVEN: User wants to compare product prices
        WHEN: User compares products
        THEN: All price information should be accurate
        """
        # Step 1: Get products
        list_response = await test_client_with_test_data.get("/api/v1/products")
        products = list_response.json()
        selected_ids = [p["id"] for p in products[:3]]

        # Step 2: Compare products
        compare_response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": selected_ids},
        )

        # Assert price information is present and valid
        compared_products = compare_response.json()
        for product in compared_products:
            assert "price" in product
            assert isinstance(product["price"], (int, float))
            assert product["price"] > 0
            assert "currency" in product
            assert isinstance(product["currency"], str)

    async def test_workflow_with_specifications_comparison(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Compare product specifications.

        GIVEN: User wants to compare product specifications
        WHEN: User compares products
        THEN: All specifications should be available
        """
        # Step 1: Get products
        list_response = await test_client_with_test_data.get("/api/v1/products")
        products = list_response.json()
        selected_ids = [p["id"] for p in products[:3]]

        # Step 2: Compare products
        compare_response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": selected_ids},
        )

        # Assert specifications are present
        compared_products = compare_response.json()
        for product in compared_products:
            assert "specifications" in product
            assert isinstance(product["specifications"], dict)


@pytest.mark.e2e
@pytest.mark.asyncio
class TestErrorRecoveryWorkflows:
    """Test error handling in complete workflows."""

    async def test_workflow_with_invalid_product_id(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Handle invalid product ID gracefully.

        GIVEN: User provides invalid product ID
        WHEN: User tries to get product details
        THEN: Appropriate error should be returned
        """
        # Step 1: Try to get non-existent product
        invalid_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client_with_test_data.get(
            f"/api/v1/products/{invalid_id}"
        )

        # Assert error is handled
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "error" in error

    async def test_workflow_with_partial_invalid_comparison(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Handle comparison with some invalid IDs.

        GIVEN: User provides mix of valid and invalid IDs
        WHEN: User tries to compare products
        THEN: Error should be returned
        """
        # Step 1: Get one valid product
        list_response = await test_client_with_test_data.get("/api/v1/products")
        valid_id = list_response.json()[0]["id"]

        # Step 2: Try to compare with invalid ID
        invalid_id = "00000000-0000-0000-0000-000000000000"
        mixed_ids = [valid_id, invalid_id]

        response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": mixed_ids},
        )

        # Assert error handling
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.performance
class TestPerformanceWorkflows:
    """Test performance of complete workflows."""

    async def test_complete_workflow_performance(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Verify complete workflow completes in acceptable time.

        GIVEN: User performs complete comparison workflow
        WHEN: All steps are executed
        THEN: Total time should be under 500ms
        """
        start_time = time.time()

        # Step 1: List products
        list_response = await test_client_with_test_data.get("/api/v1/products")
        products = list_response.json()

        # Step 2: Get details for one product
        await test_client_with_test_data.get(f"/api/v1/products/{products[0]['id']}")

        # Step 3: Compare products
        selected_ids = [p["id"] for p in products[:3]]
        await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": selected_ids},
        )

        elapsed_ms = (time.time() - start_time) * 1000

        # Assert performance
        assert elapsed_ms < 500, f"Workflow took {elapsed_ms}ms (limit: 500ms)"

    async def test_rapid_sequential_comparisons(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Test multiple rapid comparisons.

        GIVEN: User performs multiple comparisons in sequence
        WHEN: Multiple comparison requests are made
        THEN: All should succeed without degradation
        """
        # Get products
        list_response = await test_client_with_test_data.get("/api/v1/products")
        products = list_response.json()

        # Perform 5 rapid comparisons
        for i in range(5):
            selected_ids = [p["id"] for p in products[i:i+2]]
            if len(selected_ids) < 2:
                break

            response = await test_client_with_test_data.get(
                "/api/v1/products/compare/batch",
                params={"product_ids": selected_ids},
            )

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.e2e
@pytest.mark.asyncio
class TestDataIntegrityWorkflows:
    """Test data integrity across complete workflows."""

    async def test_product_data_consistency(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Verify product data is consistent across endpoints.

        GIVEN: Same product accessed via different endpoints
        WHEN: Product is retrieved individually and in batch
        THEN: Data should be identical
        """
        # Step 1: Get product via list endpoint
        list_response = await test_client_with_test_data.get("/api/v1/products")
        product_from_list = list_response.json()[0]
        product_id = product_from_list["id"]

        # Step 2: Get same product via detail endpoint
        detail_response = await test_client_with_test_data.get(
            f"/api/v1/products/{product_id}"
        )
        product_from_detail = detail_response.json()

        # Step 3: Get same product via comparison endpoint
        compare_response = await test_client_with_test_data.get(
            "/api/v1/products/compare/batch",
            params={"product_ids": [product_id]},
        )
        product_from_compare = compare_response.json()[0]

        # Assert all representations are identical
        assert product_from_list == product_from_detail
        assert product_from_detail == product_from_compare

    async def test_rating_values_are_valid(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Verify all ratings are within valid range.

        GIVEN: Products in the system
        WHEN: Products are retrieved
        THEN: All ratings should be between 0.0 and 5.0
        """
        # Get all products
        response = await test_client_with_test_data.get("/api/v1/products")
        products = response.json()

        # Verify all ratings
        for product in products:
            assert "rating" in product
            assert 0.0 <= product["rating"] <= 5.0

    async def test_all_products_have_required_fields(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Verify all products have required fields.

        GIVEN: Products in the system
        WHEN: Products are retrieved
        THEN: All required fields should be present
        """
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

        # Get all products
        response = await test_client_with_test_data.get("/api/v1/products")
        products = response.json()

        # Verify all products have required fields
        for product in products:
            for field in required_fields:
                assert field in product, f"Product missing field: {field}"


@pytest.mark.e2e
@pytest.mark.asyncio
class TestHealthCheckWorkflow:
    """Test health check and monitoring workflows."""

    async def test_health_check_workflow(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Verify system health check.

        GIVEN: System is running
        WHEN: Health endpoints are checked
        THEN: All should report healthy status
        """
        # Check main health endpoint
        health_response = await test_client_with_test_data.get("/health")
        assert health_response.status_code == status.HTTP_200_OK
        assert health_response.json()["status"] == "healthy"

        # Check product count health endpoint
        count_response = await test_client_with_test_data.get(
            "/api/v1/products/health/count"
        )
        assert count_response.status_code == status.HTTP_200_OK
        assert count_response.json()["status"] == "healthy"
        assert count_response.json()["count"] > 0

    async def test_api_documentation_availability(
        self, test_client_with_test_data: AsyncClient
    ) -> None:
        """
        Verify API documentation is accessible.

        GIVEN: API is running
        WHEN: Root endpoint is accessed
        THEN: API information should be returned
        """
        response = await test_client_with_test_data.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
