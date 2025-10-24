# Item Comparison API - Backend Development

## Context
You are building a RESTful API for an item comparison feature.

## Core Requirements

### API Functionality
Build a simple RESTful API with the following technical features:

**Endpoints Required:**
- GET endpoint to retrieve details for multiple items (support batch retrieval)
- Each product response must include:
  - Product name
  - Image URL
  - Description
  - Price
  - Rating
  - Specifications (as flexible key-value structure)

**Data Storage:**
- Use local JSON or CSV files (NO real databases)
- Create mock data for at least 5-10 diverse products
- Data should be realistic as possible

### Technical Stack & Architecture

**Framework:** FastAPI (Python 3.11+)

**Architecture Pattern:** Hexagonal Architecture (Ports & Adapters)
```
src/
├── api/                    # Adapters: HTTP layer (FastAPI routes)
├── domain/                 # Core business logic & entities
│   ├── models/            # Domain models (Product, etc.)
│   ├── ports/             # Interfaces/Abstract classes
│   └── services/          # Business logic
├── infrastructure/         # Adapters: Data access, external services
│   └── repositories/      # Data persistence implementation
├── config/                # Configuration management
└── main.py                # Application entry point
```

**Design Principles (MANDATORY):**
- Single Responsibility Principle
- Dependency Inversion
- Separation of Concerns
- Clean Code principles
- Repository pattern for data access
- Service layer for business logic

### Code Quality Standards

**Python Standards:**
- Strict PEP 8 compliance
- Type hints for all functions/methods (Python typing module)
- Docstrings (Google or NumPy style) for modules, classes, and public methods
- Maximum function complexity: keep functions focused and testable
- Use dataclasses or Pydantic models for data structures

**Error Handling:**
- Comprehensive exception handling
- Custom exception classes for domain-specific errors
- Proper HTTP status codes (200, 400, 404, 500, etc.)
- Structured error responses with meaningful messages

**Code Organization:**
- Modular structure with clear separation
- Reusable components
- Configuration separated from code (use environment variables or config files)
- Constants in dedicated files

### Documentation Requirements

**README.md must include:**
1. **Project Overview**: Brief description of the API purpose
2. **Architecture Decision**: Explanation of hexagonal architecture choice and benefits
3. **Technology Stack**: Detailed list with justifications for FastAPI and other choices
4. **Project Structure**: Directory tree with explanations
5. **Setup Instructions**: 
   - Prerequisites
   - Installation steps (virtual environment, dependencies)
   - Configuration (if any)
6. **Running the Project**: Clear commands to start the API
7. **API Documentation**: Overview of endpoints (FastAPI auto-docs available at /docs)
8. **Development Approach**: Brief explanation of how GenAI tools were leveraged
9. **Testing**: How to run tests (if implemented)
10. **Design Decisions**: Key architectural and technical choices made

**Inline Documentation:**
- Clear comments explaining complex logic
- NOT obvious comments (avoid over-commenting)
- Architecture decisions commented where relevant

**Optional Diagram:**
If you can generate a simple ASCII or Mermaid diagram showing:
- API architecture layers
- Request flow through the system
- Component dependencies

### Modern Development Practices

**Expected GenAI Integration:**
- Use AI tools for scaffolding, boilerplate reduction
- Code review and optimization suggestions
- Documentation generation assistance
- Test case generation (if applicable)

**Development Quality:**
- Consistent naming conventions (snake_case for Python)
- DRY principle (Don't Repeat Yourself)
- YAGNI (You Aren't Gonna Need It) - avoid over-engineering
- Logging for debugging and monitoring (use Python logging module)
- Consider API versioning strategy (e.g., /api/v1/)

### Deliverables

**Project Structure:**
```
item-comparison-api/
├── src/
│   ├── api/
│   ├── domain/
│   ├── infrastructure/
│   ├── config/
│   └── main.py
├── data/                  # JSON/CSV files with mock products
├── tests/                 # Optional but appreciated
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore
└── README.md
```

**Code Quality Expectations:**
- The code should be SO WELL-STRUCTURED that any improvements needed are refactors, NOT bug fixes
- Production-ready quality
- Easy to extend with new features
- Clear separation allows testing each layer independently

### Testing Considerations (Optional but Valued)
- If time permits, include basic unit tests for domain logic
- Use pytest framework
- Test coverage for critical business logic

## Success Criteria

- FastAPI application runs without errors
- Endpoints return properly structured JSON responses
- Hexagonal architecture clearly implemented
- Code follows PEP 8 and includes type hints
- Comprehensive README with all required sections
- Professional-grade error handling
- Mock data is realistic and properly structured
- Can compare multiple items in a single request
- Code demonstrates mid-senior engineering level
- Repository pattern properly abstracts data access

## Anti-Patterns to Avoid
- Mixing business logic in route handlers
- Direct file access in route handlers (use repository)
- Missing type hints
- Generic exception handling (catch specific exceptions)
- Hardcoded values (use configuration)
- Tightly coupled components
- Monolithic functions (>50 lines)
- Missing documentation

## Final Notes
- BACKEND ONLY - no frontend development required
- Focus on QUALITY over quantity of features
- Code readability is MANDATORY
- Think about how this would scale to a real production system
