"""
API route handlers.

This module defines the REST API endpoints for the item comparison feature.
Routes are organized following RESTful principles and use dependency
injection for service access.
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Query, status

from src.api.dependencies import ProductServiceDep
from src.domain.models.product import ProductResponse

logger = logging.getLogger(__name__)

# Create API router with version prefix
router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "type": "RepositoryError",
                            "message": "An error occurred while accessing data"
                        }
                    }
                }
            }
        }
    }
)


@router.get(
    "",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all products",
    description="""
    Retrieve all available products in the catalog.

    This endpoint returns the complete list of products available for comparison.
    Useful for displaying a catalog or selecting items to compare.
    """,
    responses={
        200: {
            "description": "List of all products",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                            "name": "Sony WH-1000XM5 Wireless Headphones",
                            "image_url": "https://images.example.com/sony-wh1000xm5.jpg",
                            "description": "Industry-leading noise canceling...",
                            "price": 399.99,
                            "rating": 4.8,
                            "specifications": {
                                "brand": "Sony",
                                "color": "Black"
                            },
                            "currency": "USD"
                        }
                    ]
                }
            }
        }
    }
)
async def get_all_products(
    product_service: ProductServiceDep
) -> List[ProductResponse]:
    """
    Get all available products.

    Args:
        product_service: Injected product service

    Returns:
        List of all products as ProductResponse objects
    """
    logger.info("GET /products - Retrieving all products")

    products = product_service.get_all_products()

    response = [ProductResponse.from_product(product) for product in products]

    logger.info(f"Successfully retrieved {len(response)} products")
    return response


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product by ID",
    description="""
    Retrieve a single product by its unique identifier.

    The product ID must be a valid UUID. Returns detailed product information
    including specifications, pricing, and ratings.
    """,
    responses={
        200: {
            "description": "Product details",
            "content": {
                "application/json": {
                    "example": {
                        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                        "name": "Sony WH-1000XM5 Wireless Headphones",
                        "image_url": "https://images.example.com/sony-wh1000xm5.jpg",
                        "description": "Industry-leading noise canceling...",
                        "price": 399.99,
                        "rating": 4.8,
                        "specifications": {
                            "brand": "Sony",
                            "color": "Black"
                        },
                        "currency": "USD"
                    }
                }
            }
        },
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "type": "ProductNotFound",
                            "message": "Product with ID 'xxx' not found",
                            "details": {"product_id": "xxx"}
                        }
                    }
                }
            }
        }
    }
)
async def get_product_by_id(
    product_id: UUID,
    product_service: ProductServiceDep
) -> ProductResponse:
    """
    Get a product by its unique identifier.

    Args:
        product_id: UUID of the product to retrieve
        product_service: Injected product service

    Returns:
        Product details as ProductResponse

    Raises:
        ProductNotFoundException: If product is not found
    """
    logger.info(f"GET /products/{product_id} - Retrieving product")

    product = product_service.get_product_by_id(product_id)

    response = ProductResponse.from_product(product)

    logger.info(f"Successfully retrieved product: {product.name}")
    return response


@router.get(
    "/compare/batch",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Get multiple products for comparison",
    description="""
    Retrieve multiple products by their IDs for comparison purposes.

    This endpoint supports batch retrieval of products, which is essential
    for the comparison feature. Provide multiple product IDs as query parameters.

    All requested products must exist; if any product is not found, a 404
    error will be returned with details about which products are missing.

    Products are returned in the same order as the requested IDs.
    """,
    responses={
        200: {
            "description": "List of products for comparison",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                            "name": "Sony WH-1000XM5 Wireless Headphones",
                            "image_url": "https://images.example.com/sony-wh1000xm5.jpg",
                            "description": "Industry-leading noise canceling...",
                            "price": 399.99,
                            "rating": 4.8,
                            "specifications": {"brand": "Sony"},
                            "currency": "USD"
                        },
                        {
                            "id": "b8d7c6e5-4a3b-2c1d-9e8f-7a6b5c4d3e2f",
                            "name": "Samsung Galaxy S24 Ultra",
                            "image_url": "https://images.example.com/samsung-s24-ultra.jpg",
                            "description": "Flagship smartphone...",
                            "price": 1299.99,
                            "rating": 4.7,
                            "specifications": {"brand": "Samsung"},
                            "currency": "USD"
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Invalid request (empty IDs or duplicates)",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "type": "ValidationError",
                            "message": "At least one product ID must be provided"
                        }
                    }
                }
            }
        },
        404: {
            "description": "One or more products not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "type": "ProductNotFound",
                            "message": "Products not found: xxx, yyy"
                        }
                    }
                }
            }
        }
    }
)
async def get_products_for_comparison(
    product_ids: List[UUID] = Query(
        ...,
        description="List of product UUIDs to retrieve",
        min_length=1,
        examples=[
            "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "b8d7c6e5-4a3b-2c1d-9e8f-7a6b5c4d3e2f"
        ]
    ),
    product_service: ProductServiceDep = None
) -> List[ProductResponse]:
    """
    Get multiple products for comparison.

    This endpoint retrieves multiple products in a single request, optimized
    for comparison use cases. All requested products must exist.

    Args:
        product_ids: List of product UUIDs to retrieve
        product_service: Injected product service

    Returns:
        List of products in the order requested

    Raises:
        ValueError: If product_ids is empty or contains duplicates
        ProductNotFoundException: If any requested product is not found
    """
    logger.info(
        f"GET /products/compare/batch - Retrieving {len(product_ids)} products"
    )

    products = product_service.get_products_for_comparison(product_ids)

    response = [ProductResponse.from_product(product) for product in products]

    logger.info(f"Successfully retrieved {len(response)} products for comparison")
    return response


@router.get(
    "/health/count",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get product count",
    description="""
    Get the total number of available products.

    This is a health check endpoint that also provides information about
    the catalog size.
    """,
    responses={
        200: {
            "description": "Product count",
            "content": {
                "application/json": {
                    "example": {
                        "count": 10,
                        "status": "healthy"
                    }
                }
            }
        }
    }
)
async def get_product_count(
    product_service: ProductServiceDep
) -> dict:
    """
    Get the total number of products.

    Args:
        product_service: Injected product service

    Returns:
        Dictionary with product count and status
    """
    logger.info("GET /products/health/count - Getting product count")

    count = product_service.get_product_count()

    logger.info(f"Product count: {count}")
    return {
        "count": count,
        "status": "healthy"
    }
