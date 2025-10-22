"""
API exception handlers.

This module defines custom exception handlers that convert domain exceptions
into appropriate HTTP responses with proper status codes and error messages.
"""

import logging
from typing import Any, Dict

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.domain.models.exceptions import (
    DomainException,
    InvalidProductDataException,
    ProductNotFoundException,
    ProductValidationException,
    RepositoryException,
)

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    error_type: str,
    message: str,
    details: Dict[str, Any] = None
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        status_code: HTTP status code
        error_type: Type of error (e.g., 'ProductNotFound')
        message: Human-readable error message
        details: Additional error details (optional)

    Returns:
        JSONResponse with standardized error format
    """
    content = {
        "error": {
            "type": error_type,
            "message": message,
        }
    }

    if details:
        content["error"]["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def product_not_found_exception_handler(
    request: Request,
    exc: ProductNotFoundException
) -> JSONResponse:
    """
    Handle ProductNotFoundException.

    Args:
        request: The incoming request
        exc: The exception instance

    Returns:
        404 JSON response
    """
    logger.warning(f"Product not found: {exc.message}")

    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        error_type="ProductNotFound",
        message=exc.message,
        details={"product_id": exc.product_id}
    )


async def product_validation_exception_handler(
    request: Request,
    exc: ProductValidationException
) -> JSONResponse:
    """
    Handle ProductValidationException.

    Args:
        request: The incoming request
        exc: The exception instance

    Returns:
        400 JSON response
    """
    logger.warning(f"Product validation error: {exc.message}")

    details = {}
    if exc.field:
        details["field"] = exc.field

    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_type="ProductValidation",
        message=exc.message,
        details=details if details else None
    )


async def invalid_product_data_exception_handler(
    request: Request,
    exc: InvalidProductDataException
) -> JSONResponse:
    """
    Handle InvalidProductDataException.

    Args:
        request: The incoming request
        exc: The exception instance

    Returns:
        500 JSON response
    """
    logger.error(f"Invalid product data: {exc.message}")

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="InvalidProductData",
        message="An error occurred while processing product data"
    )


async def repository_exception_handler(
    request: Request,
    exc: RepositoryException
) -> JSONResponse:
    """
    Handle RepositoryException.

    Args:
        request: The incoming request
        exc: The exception instance

    Returns:
        500 JSON response
    """
    logger.error(f"Repository error: {exc.message}")

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="RepositoryError",
        message="An error occurred while accessing data"
    )


async def domain_exception_handler(
    request: Request,
    exc: DomainException
) -> JSONResponse:
    """
    Handle generic DomainException.

    This is a catch-all handler for domain exceptions that don't have
    specific handlers.

    Args:
        request: The incoming request
        exc: The exception instance

    Returns:
        500 JSON response
    """
    logger.error(f"Domain error: {exc.message}")

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="DomainError",
        message="An unexpected error occurred"
    )


async def value_error_exception_handler(
    request: Request,
    exc: ValueError
) -> JSONResponse:
    """
    Handle ValueError (typically from validation).

    Args:
        request: The incoming request
        exc: The exception instance

    Returns:
        400 JSON response
    """
    logger.warning(f"Value error: {str(exc)}")

    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_type="ValidationError",
        message=str(exc)
    )


# Exception handler mapping
EXCEPTION_HANDLERS = {
    ProductNotFoundException: product_not_found_exception_handler,
    ProductValidationException: product_validation_exception_handler,
    InvalidProductDataException: invalid_product_data_exception_handler,
    RepositoryException: repository_exception_handler,
    DomainException: domain_exception_handler,
    ValueError: value_error_exception_handler,
}
