# Item Comparison API

A production-ready RESTful API for comparing products, built with FastAPI and hexagonal architecture principles.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture Decision](#architecture-decision)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Development Approach](#development-approach)
- [Design Decisions](#design-decisions)
- [Testing](#testing)

## Project Overview

The Item Comparison API is a backend service designed to facilitate product comparison features in e-commerce applications. It provides endpoints to retrieve product information including specifications, pricing, ratings, and images, enabling clients to build rich comparison interfaces.

**Key Features:**
- Retrieve individual product details
- Batch retrieval of multiple products for comparison
- Comprehensive product specifications with flexible schema
- Health check and monitoring endpoints
- Production-ready error handling and logging
- Interactive API documentation

## Architecture Decision

This project implements **Hexagonal Architecture** (also known as Ports and Adapters pattern), a design pattern that promotes separation of concerns and maintainability.

### Why Hexagonal Architecture?

**Benefits:**
1. **Independence**: Core business logic is independent of frameworks, databases, and external agencies
2. **Testability**: Each layer can be tested independently with mock implementations
3. **Flexibility**: Easy to swap implementations (e.g., JSON files → PostgreSQL) without changing business logic
4. **Maintainability**: Clear boundaries between layers make the codebase easier to understand and modify
5. **Scalability**: Well-defined interfaces make it easier to scale specific components

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  (FastAPI Routes, Dependencies, Exception Handlers)         │
│  • HTTP request/response handling                           │
│  • Input validation                                         │
│  • Dependency injection setup                               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Domain Layer                             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Models     │  │   Ports      │  │  Services    │     │
│  │              │  │              │  │              │     │
│  │ • Product    │  │ • Repository │  │ • Product    │     │
│  │ • Exceptions │  │   Interface  │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  • Core business logic                                      │
│  • Technology-agnostic                                      │
│  • Defines contracts (ports)                                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  (Repository Implementations, External Services)            │
│  • JSON file repository                                     │
│  • Data access logic                                        │
│  • External service integrations                            │
└─────────────────────────────────────────────────────────────┘

                    Configuration Layer
              (Settings, Environment Variables)
```

### Request Flow

```
1. Client Request → API Route Handler
2. Route Handler → Dependency Injection (Service + Repository)
3. Service → Domain Logic Execution
4. Service → Repository Port (Interface)
5. Repository Implementation → Data Source (JSON)
6. Data → Domain Model Validation
7. Domain Model → Response Model Conversion
8. Response Model → JSON Response to Client
```

## Technology Stack

### Core Framework
- **FastAPI (v0.109.0)**: Modern, fast web framework for building APIs with Python 3.11+
  - **Why**: Automatic API documentation, built-in validation with Pydantic, async support, excellent performance
  - Type hints for better IDE support and fewer bugs
  - OpenAPI and JSON Schema automatic generation

### ASGI Server
- **Uvicorn (v0.27.0)**: Lightning-fast ASGI server
  - **Why**: Production-ready, supports async/await, excellent performance
  - Auto-reload for development
  - Support for HTTP/1.1 and WebSockets

### Data Validation
- **Pydantic (v2.5.3)**: Data validation using Python type hints
  - **Why**: Runtime type checking, data parsing, and validation
  - JSON schema generation
  - Excellent integration with FastAPI

- **Pydantic Settings (v2.1.0)**: Settings management with environment variables
  - **Why**: Type-safe configuration, environment variable support, .env file loading
  - Follows twelve-factor app methodology

### Programming Language
- **Python 3.11+**: Latest stable Python version
  - **Why**: Improved performance, better type hints support, modern syntax features
  - Strong ecosystem for web development
  - Excellent async/await support

## Project Structure

```
item-comparison-api/
├── src/                            # Source code
│   ├── api/                        # API Layer (Adapters)
│   │   ├── __init__.py
│   │   ├── dependencies.py         # Dependency injection configuration
│   │   ├── exception_handlers.py  # HTTP exception handling
│   │   └── routes.py               # API route handlers
│   │
│   ├── domain/                     # Domain Layer (Core)
│   │   ├── models/                 # Domain entities and exceptions
│   │   │   ├── __init__.py
│   │   │   ├── product.py          # Product entity and response models
│   │   │   └── exceptions.py       # Domain-specific exceptions
│   │   │
│   │   ├── ports/                  # Interfaces (Ports)
│   │   │   ├── __init__.py
│   │   │   └── product_repository.py  # Repository interface
│   │   │
│   │   └── services/               # Business logic
│   │       ├── __init__.py
│   │       └── product_service.py  # Product business logic
│   │
│   ├── infrastructure/             # Infrastructure Layer (Adapters)
│   │   ├── repositories/           # Repository implementations
│   │   │   ├── __init__.py
│   │   │   └── json_product_repository.py  # JSON-based repository
│   │   └── __init__.py
│   │
│   ├── config/                     # Configuration
│   │   ├── __init__.py
│   │   └── settings.py             # Application settings
│   │
│   ├── __init__.py
│   └── main.py                     # Application entry point
│
├── data/                           # Data storage
│   └── products.json               # Product catalog (10 diverse items)
│
├── tests/                          # Test suite
│   └── __init__.py
│
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
└── requirements.txt                # Python dependencies
```

### Directory Explanations

- **`src/api/`**: HTTP adapter layer, handles web requests and responses. Contains FastAPI routes, dependency injection, and exception handlers.

- **`src/domain/`**: Core business logic, independent of any framework. Contains entities, business rules, and interface definitions.

- **`src/infrastructure/`**: Implementations of domain interfaces. Contains concrete repository implementations and external service integrations.

- **`src/config/`**: Configuration management using Pydantic settings, supporting environment variables and .env files.

- **`data/`**: Local data storage (JSON files). In production, this would be replaced with a database.

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Virtual environment tool (venv, recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd product-comparison
   ```

2. **Create a virtual environment**
   ```bash
   # Using venv (recommended)
   python3 -m venv venv

   # Activate virtual environment
   # On Linux/macOS:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables (optional)**
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env file with your preferences
   # Default values work out of the box
   ```

### Configuration

The application can be configured via environment variables or a `.env` file. All settings have sensible defaults for local development.

**Key Configuration Options:**
- `APP_ENVIRONMENT`: Deployment environment (development/staging/production)
- `APP_LOG_LEVEL`: Logging verbosity (DEBUG/INFO/WARNING/ERROR)
- `APP_DATA_FILE_PATH`: Path to product data JSON file
- `APP_HOST`: Server host (default: 0.0.0.0)
- `APP_PORT`: Server port (default: 8000)

See `.env.example` for all available configuration options.

## Running the Project

### Development Server

**Method 1: Using Python directly**
```bash
python -m uvicorn src.main:app --reload
```

**Method 2: Using the main module**
```bash
python src/main.py
```

The API will start on `http://localhost:8000`

**Server Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Production Deployment

For production, disable auto-reload and set appropriate environment:

```bash
# Set environment variables
export APP_ENVIRONMENT=production
export APP_RELOAD=false
export APP_LOG_LEVEL=WARNING

# Run with production settings
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)

A Dockerfile can be created for containerized deployment:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
  - Interactive interface to test API endpoints
  - Automatic request/response examples
  - Schema definitions

- **ReDoc**: http://localhost:8000/api/v1/redoc
  - Clean, readable API documentation
  - Better for documentation review

- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json
  - Raw OpenAPI specification
  - Can be imported into tools like Postman

### Available Endpoints

#### 1. Get All Products
```http
GET /api/v1/products
```
Retrieves all products in the catalog.

**Response**: `200 OK`
```json
[
  {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "Sony WH-1000XM5 Wireless Headphones",
    "image_url": "https://images.example.com/sony-wh1000xm5.jpg",
    "description": "Industry-leading noise canceling...",
    "price": 399.99,
    "rating": 4.8,
    "specifications": {
      "brand": "Sony",
      "color": "Black",
      "battery_life": "30 hours"
    },
    "currency": "USD"
  }
]
```

#### 2. Get Product by ID
```http
GET /api/v1/products/{product_id}
```
Retrieves a specific product by UUID.

**Parameters**:
- `product_id` (path, UUID): Product identifier

**Response**: `200 OK` (product details) or `404 Not Found`

#### 3. Compare Products (Batch Retrieval)
```http
GET /api/v1/products/compare/batch?product_ids={id1}&product_ids={id2}
```
Retrieves multiple products for comparison.

**Parameters**:
- `product_ids` (query, array of UUIDs): Product identifiers to compare

**Example**:
```bash
curl "http://localhost:8000/api/v1/products/compare/batch?product_ids=f47ac10b-58cc-4372-a567-0e02b2c3d479&product_ids=b8d7c6e5-4a3b-2c1d-9e8f-7a6b5c4d3e2f"
```

**Response**: `200 OK` (array of products in requested order)

**Error Responses**:
- `400 Bad Request`: Empty or duplicate IDs
- `404 Not Found`: One or more products not found

#### 4. Health Check
```http
GET /api/v1/products/health/count
```
Returns product count and API health status.

**Response**: `200 OK`
```json
{
  "count": 10,
  "status": "healthy"
}
```

#### 5. Root Endpoint
```http
GET /
```
Returns API information and available endpoints.

### Example Usage with cURL

```bash
# Get all products
curl http://localhost:8000/api/v1/products

# Get specific product
curl http://localhost:8000/api/v1/products/f47ac10b-58cc-4372-a567-0e02b2c3d479

# Compare products
curl "http://localhost:8000/api/v1/products/compare/batch?product_ids=f47ac10b-58cc-4372-a567-0e02b2c3d479&product_ids=b8d7c6e5-4a3b-2c1d-9e8f-7a6b5c4d3e2f"

# Health check
curl http://localhost:8000/api/v1/products/health/count
```

### Error Response Format

All errors follow a consistent structure:

```json
{
  "error": {
    "type": "ProductNotFound",
    "message": "Product with ID 'xxx' not found",
    "details": {
      "product_id": "xxx"
    }
  }
}
```

## Development Approach

This project was developed leveraging GenAI tools to demonstrate modern development practices:

### GenAI Integration

1. **Architecture Design**: AI-assisted in designing the hexagonal architecture structure and ensuring proper separation of concerns.

2. **Code Generation**: Used AI to generate boilerplate code for:
   - Pydantic models with comprehensive validation
   - Repository interfaces and implementations
   - FastAPI route handlers with proper type hints
   - Exception handlers with standardized error responses

3. **Documentation**: AI assisted in creating:
   - Comprehensive docstrings (Google style)
   - Inline code comments for complex logic
   - This README with detailed explanations
   - API documentation examples

4. **Best Practices**: AI provided guidance on:
   - SOLID principles implementation
   - Python PEP 8 compliance
   - Type hints and validation strategies
   - Error handling patterns

5. **Code Review**: AI performed self-review to ensure:
   - Consistent code style
   - Proper separation of concerns
   - Complete type hints
   - Comprehensive error handling

### Development Workflow

1. **Design First**: Started with architecture design and domain modeling
2. **Inside-Out**: Built from domain layer outward (domain → infrastructure → API)
3. **Dependency Inversion**: Domain defines interfaces, infrastructure implements
4. **Test-Friendly**: Code structure allows easy unit testing (though tests not included in this version)
5. **Documentation-Driven**: Comprehensive documentation at all levels

## Design Decisions

### 1. Hexagonal Architecture

**Decision**: Implement hexagonal architecture (ports and adapters pattern)

**Rationale**:
- Separates business logic from infrastructure concerns
- Makes the codebase highly testable and maintainable
- Allows easy migration from JSON to database without changing domain logic
- Aligns with SOLID principles, especially Dependency Inversion

**Trade-offs**:
- More initial setup compared to a simple layered architecture
- Requires discipline to maintain boundaries
- May be over-engineering for very simple applications

**Verdict**: Appropriate for this project as it demonstrates professional-grade architecture and prepares for future scaling.

### 2. JSON File Storage

**Decision**: Use JSON files for data persistence instead of a database

**Rationale**:
- Meets the requirement of "NO real databases"
- Simple to set up and understand
- Easy to inspect and modify data
- Sufficient for demonstration purposes
- In-memory caching provides good performance

**Migration Path**: The repository pattern makes it trivial to swap to a real database:
```python
# Just change the repository implementation
# from JsonProductRepository to PostgresProductRepository
# Domain and API layers remain unchanged
```

### 3. Pydantic for Validation

**Decision**: Use Pydantic models for all data structures

**Rationale**:
- Runtime validation prevents invalid data
- Automatic JSON schema generation for API docs
- Type safety with IDE support
- Excellent integration with FastAPI
- Clear error messages for validation failures

### 4. Dependency Injection

**Decision**: Use FastAPI's dependency injection system

**Rationale**:
- Loose coupling between components
- Easy to mock dependencies for testing
- Clear declaration of dependencies in route signatures
- Follows SOLID principles (Dependency Inversion)
- Centralized configuration

### 5. Comprehensive Exception Handling

**Decision**: Custom exception classes with specific HTTP handlers

**Rationale**:
- Clear error messages for API consumers
- Proper HTTP status codes (404, 400, 500)
- Consistent error response format
- Separation of domain exceptions from HTTP concerns
- Better debugging and monitoring

### 6. Logging

**Decision**: Structured logging throughout the application

**Rationale**:
- Essential for production debugging
- Performance monitoring
- Audit trail for operations
- Configurable log levels per environment

### 7. Type Hints Everywhere

**Decision**: Full type hint coverage

**Rationale**:
- Better IDE support (autocomplete, refactoring)
- Catches bugs before runtime
- Self-documenting code
- Enables static type checking with mypy
- Required by project specification (PEP 8 compliance)

### 8. API Versioning

**Decision**: Include version prefix in API URLs (`/api/v1/`)

**Rationale**:
- Allows breaking changes in future versions
- Industry best practice
- Clients can specify which version to use
- Smooth migration path for API evolution

### 9. Separation of Product and ProductResponse

**Decision**: Separate domain model from API response model

**Rationale**:
- Domain model can evolve independently
- API contract remains stable
- Different validation rules for internal vs external
- Allows API-specific transformations (UUID → string)

### 10. Single Responsibility Principle

**Decision**: Each class/module has one clear responsibility

**Examples**:
- `ProductService`: Business logic only
- `JsonProductRepository`: Data access only
- Routes: HTTP handling only
- Models: Data structure and validation only

**Rationale**:
- Easier to understand and maintain
- Facilitates testing
- Reduces coupling
- Enables independent evolution of components

## Testing

While automated tests are not included in this initial version, the architecture is designed for easy testing:

### Test Structure (If Implemented)

```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_product_model.py
│   │   └── test_product_service.py
│   └── infrastructure/
│       └── test_json_repository.py
├── integration/
│   └── test_api_routes.py
└── conftest.py
```

### Testing Approach

**Unit Tests**:
```python
# Example: Testing ProductService with mock repository
def test_get_product_by_id():
    mock_repo = MockProductRepository()
    service = ProductService(mock_repo)
    product = service.get_product_by_id(UUID("..."))
    assert product.name == "Expected Product"
```

**Integration Tests**:
```python
# Example: Testing API endpoints with TestClient
from fastapi.testclient import TestClient

def test_get_all_products():
    client = TestClient(app)
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

### Running Tests (If Implemented)

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Testability Features

1. **Dependency Injection**: Easy to inject mock dependencies
2. **Repository Pattern**: Can swap real repository with in-memory mock
3. **Pure Functions**: Most functions have no side effects
4. **Clear Interfaces**: Ports define clear contracts for testing
5. **Isolated Layers**: Each layer can be tested independently

---

## Additional Information

### Mock Data

The `data/products.json` file contains 10 diverse products:
1. Sony WH-1000XM5 Wireless Headphones
2. Apple MacBook Pro 14-inch M3
3. Samsung Galaxy S24 Ultra
4. LG C3 65-inch OLED 4K TV
5. Dyson V15 Detect Absolute Cordless Vacuum
6. Instant Pot Duo Plus 9-in-1
7. Canon EOS R6 Mark II Camera
8. Peloton Bike+ Indoor Exercise Bike
9. Bose SoundLink Revolve+ II Speaker
10. Ninja Creami Ice Cream Maker

Each product includes comprehensive specifications relevant to its category.

### Performance Considerations

- **In-Memory Caching**: Products are loaded once and cached in memory
- **Singleton Repository**: Repository instance is reused across requests
- **Async Support**: FastAPI's async capabilities allow high concurrency
- **Efficient JSON Parsing**: Pydantic's optimized C bindings for validation

### Security Considerations

- **Input Validation**: All inputs validated with Pydantic
- **UUID Validation**: Prevents injection attacks
- **CORS Configuration**: Configurable allowed origins
- **Error Message Safety**: Sensitive information not exposed in error messages
- **Logging**: Sensitive data not logged

### Future Enhancements

1. **Database Integration**: Migrate from JSON to PostgreSQL/MongoDB
2. **Caching Layer**: Add Redis for improved performance
3. **Authentication**: Add JWT-based authentication
4. **Rate Limiting**: Prevent abuse with rate limiting
5. **Search Functionality**: Add product search with filters
6. **Pagination**: Add pagination for large product catalogs
7. **Automated Tests**: Comprehensive test suite with >80% coverage
8. **CI/CD Pipeline**: Automated testing and deployment
9. **Monitoring**: Add Prometheus metrics and Grafana dashboards
10. **API Gateway**: Add Kong or similar for enterprise features

---

## License

This project is developed as a technical assessment. Please refer to your organization's licensing requirements.

## Support

For issues, questions, or contributions, please contact the development team or open an issue in the repository.

---

**Built with FastAPI and Claude Code GenAI**
