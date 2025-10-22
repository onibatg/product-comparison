"""
Domain-specific exceptions.

This module defines custom exceptions for domain-level errors. These exceptions
are part of the ubiquitous language and represent business rule violations or
domain-specific error conditions.
"""


class DomainException(Exception):
    """
    Base exception for all domain-level errors.

    All domain-specific exceptions should inherit from this base class.
    This allows for centralized exception handling at the application boundary.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize domain exception.

        Args:
            message: Human-readable error message
        """
        self.message = message
        super().__init__(self.message)


class ProductNotFoundException(DomainException):
    """
    Exception raised when a requested product cannot be found.

    This exception indicates that a product with the specified identifier
    does not exist in the system.
    """

    def __init__(self, product_id: str) -> None:
        """
        Initialize product not found exception.

        Args:
            product_id: ID of the product that was not found
        """
        super().__init__(f"Product with ID '{product_id}' not found")
        self.product_id = product_id


class ProductValidationException(DomainException):
    """
    Exception raised when product data fails validation.

    This exception indicates that product data does not meet the required
    business rules or constraints.
    """

    def __init__(self, message: str, field: str = None) -> None:
        """
        Initialize product validation exception.

        Args:
            message: Description of the validation error
            field: Name of the field that failed validation (if applicable)
        """
        super().__init__(message)
        self.field = field


class InvalidProductDataException(DomainException):
    """
    Exception raised when product data is malformed or invalid.

    This exception indicates issues with the structure or format of product
    data, typically when loading from external sources.
    """

    pass


class RepositoryException(DomainException):
    """
    Exception raised when repository operations fail.

    This exception indicates errors at the data access layer that cannot be
    recovered from.
    """

    pass
