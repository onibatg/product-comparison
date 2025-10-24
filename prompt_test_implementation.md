---
# ============================================================================
# TEST IMPLEMENTATION PROMPT - Suite Completa de Testing
# ============================================================================
version: "2.0"
type: "implementation_task"
complexity: "mid_senior"
language: "spanish"

# ----------------------------------------------------------------------------
# METADATA
# ----------------------------------------------------------------------------
metadata:
  task: "Implementar suite completa de tests para Item Comparison API"
  target_coverage: ">80%"
  testing_levels: ["unit", "integration", "e2e"]
  framework: "pytest"
  quality_standard: "production_ready"

# ----------------------------------------------------------------------------
# PROJECT CONTEXT
# ----------------------------------------------------------------------------
project_context:
  name: "Item Comparison API"
  description: |
    API RESTful construida con FastAPI usando arquitectura hexagonal.
    Provee endpoints para comparación de productos con datos almacenados
    en archivos JSON/CSV locales.
  
  architecture:
    pattern: "Hexagonal Architecture (Ports & Adapters)"
    structure: |
src/
├── api/# HTTP layer (FastAPI routes)
├── domain/   # Core business logic
│   ├── models/    # Domain entities
│   ├── ports/     # Interfaces
│   └── services/  # Business logic
├── infrastructure/ # Data access
│   └── repositories/    # Data persistence
└── config/  # Configuration
  
  tech_stack:
    - Python 3.11+
    - FastAPI
    - Pydantic
    - JSON/CSV for data storage
  
  existing_endpoints:
    - "GET /api/v1/products/compare/batch?product_ids=UUID1&product_ids=UUID2"
    - "GET /api/v1/products/{product_id}"
    - "GET /api/v1/products (list all)"

# ----------------------------------------------------------------------------
# TESTING REQUIREMENTS
# ----------------------------------------------------------------------------
testing_requirements:
  coverage_target: 85
  
  testing_pyramid:
    unit_tests: 70%# 70% de los tests son unitarios
    integration_tests: 20%  # 20% tests de integración
    e2e_tests: 10% # 10% tests end-to-end
  
  mandatory_test_types:
    - name: "Unit Tests"
scope: "Domain logic, services, models"
isolation: "Complete - mock all dependencies"
speed: "< 100ms per test"

    - name: "Integration Tests"
scope: "API routes + repositories"
isolation: "Partial - use test data files"
speed: "< 500ms per test"

    - name: "End-to-End Tests"
scope: "Full request/response cycle"
isolation: "None - real API calls"
speed: "< 2s per test"

# ----------------------------------------------------------------------------
# TECHNICAL SPECIFICATIONS
# ----------------------------------------------------------------------------
technical_specs:
  
  frameworks_and_tools:
    primary: "pytest"
    additional:
- "pytest-asyncio (for async tests)"
- "pytest-cov (coverage reporting)"
- "httpx (for API testing)"
- "pytest-mock (mocking)"
- "faker (test data generation)"
    
  test_structure: |
    tests/
    ├── conftest.py  # Fixtures compartidos
    ├── unit/  # Tests unitarios
    │   ├── test_domain_models.py
    │   ├── test_services.py
    │   └── test_validators.py
    ├── integration/ # Tests de integración
    │   ├── test_repositories.py
    │   ├── test_api_routes.py
    │   └── test_data_loading.py
    ├── e2e/   # Tests end-to-end
    │   └── test_comparison_flow.py
    └── fixtures/    # Test data
  └── test_products.json
  
  naming_conventions:
    test_files: "test_*.py"
    test_functions: "test_*"
    test_classes: "Test*"
    fixtures: "fixture_name (lowercase with underscores)"
  
  code_quality:
    - "Type hints en todas las funciones de test"
    - "Docstrings descriptivos"
    - "Arrange-Act-Assert pattern"
    - "One assertion per test (cuando sea posible)"
    - "Descriptive test names (test_should_do_something_when_condition)"

# ----------------------------------------------------------------------------
# TEST CASES TO IMPLEMENT
# ----------------------------------------------------------------------------
test_cases:
  
  domain_layer:
    models:
- test_product_model_validation:
    description: "Validar que Product model rechaza datos inválidos"
    scenarios:
- "Invalid UUID format"
- "Negative price"
- "Rating out of range (0-5)"
- "Missing required fields"
- "Valid product creation"

- test_product_serialization:
    description: "Validar serialización/deserialización"
    scenarios:
- "To dict"
- "From dict"
- "JSON serialization"
    
    services:
- test_product_service_get_by_id:
    description: "Obtener producto por ID"
    scenarios:
- "Product exists - returns product"
- "Product not found - raises NotFoundError"
- "Invalid UUID format - raises ValidationError"
- "Repository error - propagates exception"

- test_product_service_get_batch:
    description: "Obtener múltiples productos"
    scenarios:
- "All products exist - returns all"
- "Some products missing - returns found + logs missing"
- "Empty list - returns empty"
- "Duplicate IDs - returns unique products"
- "Max batch size exceeded - raises ValidationError"

- test_product_service_comparison_logic:
    description: "Lógica de comparación"
    scenarios:
- "Compare 2 products successfully"
- "Compare 10 products (max allowed)"
- "Less than 2 products - raises ValidationError"
- "More than 10 products - raises ValidationError"
  
  infrastructure_layer:
    repositories:
- test_json_repository_load_data:
    description: "Cargar datos desde JSON"
    scenarios:
- "Load valid JSON file"
- "File not found - raises FileNotFoundError"
- "Invalid JSON format - raises ParseError"
- "Empty file - returns empty list"

- test_json_repository_find_by_id:
    description: "Buscar producto por ID en JSON"
    scenarios:
- "Product exists"
- "Product not found"
- "Multiple files - searches all"

- test_json_repository_find_batch:
    description: "Buscar múltiples productos"
    scenarios:
- "All IDs found"
- "Partial match"
- "No matches"
- "Performance test - 100 IDs < 100ms"
  
  api_layer:
    endpoints:
- test_compare_batch_endpoint:
    description: "GET /api/v1/products/compare/batch"
    scenarios:
- "Valid request with 2 products - 200 OK"
- "Valid request with 10 products - 200 OK"
- "Missing product_ids param - 422 Unprocessable"
- "Less than 2 IDs - 400 Bad Request"
- "More than 10 IDs - 400 Bad Request"
- "Invalid UUID format - 422 Unprocessable"
- "Some products not found - 200 OK with partial results"
- "All products not found - 404 Not Found"
- "Response structure validation"
- "Response time < 200ms"

- test_get_product_by_id_endpoint:
    description: "GET /api/v1/products/{product_id}"
    scenarios:
- "Valid ID - 200 OK"
- "Invalid UUID - 422 Unprocessable"
- "Not found - 404 Not Found"
- "Response structure validation"

- test_list_products_endpoint:
    description: "GET /api/v1/products"
    scenarios:
- "Returns all products - 200 OK"
- "Pagination support (if implemented)"
- "Response structure validation"

- test_error_handling:
    description: "Error responses"
    scenarios:
- "404 returns proper JSON structure"
- "422 validation errors include details"
- "500 internal errors are handled gracefully"
- "CORS headers present (if configured)"
  
  edge_cases:
    - test_concurrent_requests:
  description: "Múltiples requests simultáneos"
  scenario: "10 concurrent requests don't cause race conditions"
    
    - test_large_specifications:
  description: "Productos con specifications muy grandes"
  scenario: "Handle products with 50+ specification fields"
    
    - test_special_characters:
  description: "Caracteres especiales en nombres/descripciones"
  scenario: "Unicode, emojis, special chars handled correctly"
    
    - test_performance_degradation:
  description: "Performance con dataset grande"
  scenario: "Load 1000 products, compare 10 - time < 500ms"

# ----------------------------------------------------------------------------
# FIXTURES & TEST DATA
# ----------------------------------------------------------------------------
fixtures:
  
  sample_products: |
    # tests/fixtures/test_products.json
    [
{
  "id": "test-uuid-1",
  "name": "Test Product 1",
  "image_url": "https://example.com/image1.jpg",
  "description": "Test description 1",
  "price": 99.99,
  "rating": 4.5,
  "specifications": {
    "brand": "TestBrand",
    "color": "Blue"
  },
  "currency": "USD"
},
{
  "id": "test-uuid-2",
  "name": "Test Product 2",
  "image_url": "https://example.com/image2.jpg",
  "description": "Test description 2",
  "price": 149.99,
  "rating": 4.8,
  "specifications": {
    "brand": "TestBrand",
    "color": "Red"
  },
  "currency": "USD"
}
    ]
  
  pytest_fixtures: |
    # tests/conftest.py
    
    @pytest.fixture
    def test_product_data():
  """Datos de producto de prueba"""
  return {
"id": "test-uuid",
"name": "Test Product",
"price": 99.99,
"rating": 4.5
  }
    
    @pytest.fixture
    def mock_repository():
  """Repository mockeado"""
  return Mock(spec=ProductRepository)
    
    @pytest.fixture
    def product_service(mock_repository):
  """Service con repository mockeado"""
  return ProductService(repository=mock_repository)
    
    @pytest.fixture
    async def test_client():
  """Cliente HTTP para tests de API"""
  async with AsyncClient(app=app, base_url="http://test") as client:
yield client
    
    @pytest.fixture
    def sample_products():
  """Carga productos de prueba desde JSON"""
  with open("tests/fixtures/test_products.json") as f:
return json.load(f)

# ----------------------------------------------------------------------------
# TEST EXAMPLES (PATTERNS TO FOLLOW)
# ----------------------------------------------------------------------------
test_examples:
  
  unit_test_example: |
    # tests/unit/test_services.py
    
    import pytest
    from unittest.mock import Mock, patch
    from src.domain.services import ProductService
    from src.domain.exceptions import NotFoundError, ValidationError
    
    class TestProductService:
  """Suite de tests para ProductService"""
  
  def test_should_return_product_when_id_exists(
self,
product_service: ProductService,
mock_repository: Mock,
test_product_data: dict
  ):
"""
GIVEN: Un producto existente en el repositorio
WHEN: Se solicita el producto por ID
THEN: Debe retornar el producto correctamente
"""
# Arrange
product_id = "test-uuid"
mock_repository.find_by_id.return_value = test_product_data

# Act
result = product_service.get_product(product_id)

# Assert
assert result is not None
assert result["id"] == product_id
mock_repository.find_by_id.assert_called_once_with(product_id)
  
  def test_should_raise_not_found_when_product_missing(
self,
product_service: ProductService,
mock_repository: Mock
  ):
"""
GIVEN: Un ID de producto que no existe
WHEN: Se solicita el producto por ID
THEN: Debe lanzar NotFoundError
"""
# Arrange
product_id = "non-existent-uuid"
mock_repository.find_by_id.return_value = None

# Act & Assert
with pytest.raises(NotFoundError) as exc_info:
    product_service.get_product(product_id)

assert "not found" in str(exc_info.value).lower()
  
  @pytest.mark.parametrize("invalid_id", [
"",
"invalid-uuid",
"12345",
None
  ])
  def test_should_raise_validation_error_for_invalid_uuid(
self,
product_service: ProductService,
invalid_id: str
  ):
"""
GIVEN: Un formato de UUID inválido
WHEN: Se solicita el producto
THEN: Debe lanzar ValidationError
"""
with pytest.raises(ValidationError):
    product_service.get_product(invalid_id)
  
  def test_should_return_multiple_products_when_batch_requested(
self,
product_service: ProductService,
mock_repository: Mock,
sample_products: list
  ):
"""
GIVEN: Múltiples productos existentes
WHEN: Se solicita batch de productos
THEN: Debe retornar todos los productos encontrados
"""
# Arrange
product_ids = ["uuid-1", "uuid-2", "uuid-3"]
mock_repository.find_batch.return_value = sample_products[:3]

# Act
result = product_service.get_products_batch(product_ids)

# Assert
assert len(result) == 3
assert all(p["id"] in product_ids for p in result)
  
  def test_should_enforce_max_batch_size(
self,
product_service: ProductService
  ):
"""
GIVEN: Más de 10 IDs en la solicitud
WHEN: Se solicita batch
THEN: Debe lanzar ValidationError
"""
# Arrange
product_ids = [f"uuid-{i}" for i in range(11)]

# Act & Assert
with pytest.raises(ValidationError) as exc_info:
    product_service.get_products_batch(product_ids)

assert "maximum" in str(exc_info.value).lower()
  
  integration_test_example: |
    # tests/integration/test_api_routes.py
    
    import pytest
    from httpx import AsyncClient
    from fastapi import status
    
    @pytest.mark.asyncio
    class TestComparisonEndpoint:
  """Tests de integración para endpoint de comparación"""
  
  async def test_should_return_products_for_valid_comparison_request(
self,
test_client: AsyncClient,
sample_products: list
  ):
"""
GIVEN: Endpoint de comparación disponible
WHEN: Se hace request con 2 product IDs válidos
THEN: Debe retornar 200 con ambos productos
"""
# Arrange
product_ids = [sample_products[0]["id"], sample_products[1]["id"]]
params = {"product_ids": product_ids}

# Act
response = await test_client.get(
    "/api/v1/products/compare/batch",
    params=params
)

# Assert
assert response.status_code == status.HTTP_200_OK
data = response.json()
assert len(data) == 2
assert all("id" in product for product in data)
assert all("price" in product for product in data)
assert all("rating" in product for product in data)
  
  async def test_should_return_400_when_less_than_two_products(
self,
test_client: AsyncClient
  ):
"""
GIVEN: Endpoint de comparación disponible
WHEN: Se envía menos de 2 product IDs
THEN: Debe retornar 400 Bad Request
"""
# Arrange
params = {"product_ids": ["single-uuid"]}

# Act
response = await test_client.get(
    "/api/v1/products/compare/batch",
    params=params
)

# Assert
assert response.status_code == status.HTTP_400_BAD_REQUEST
error_detail = response.json()
assert "detail" in error_detail
  
  async def test_should_return_422_for_invalid_uuid_format(
self,
test_client: AsyncClient
  ):
"""
GIVEN: Endpoint de comparación disponible
WHEN: Se envía UUID con formato inválido
THEN: Debe retornar 422 Unprocessable Entity
"""
# Arrange
params = {"product_ids": ["invalid-uuid", "another-invalid"]}

# Act
response = await test_client.get(
    "/api/v1/products/compare/batch",
    params=params
)

# Assert
assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  
  @pytest.mark.performance
  async def test_should_respond_within_200ms(
self,
test_client: AsyncClient,
sample_products: list
  ):
"""
GIVEN: Endpoint de comparación disponible
WHEN: Se hace request válido
THEN: Debe responder en menos de 200ms
"""
import time

# Arrange
product_ids = [p["id"] for p in sample_products[:5]]
params = {"product_ids": product_ids}

# Act
start_time = time.time()
response = await test_client.get(
    "/api/v1/products/compare/batch",
    params=params
)
elapsed = (time.time() - start_time) * 1000  # ms

# Assert
assert response.status_code == status.HTTP_200_OK
assert elapsed < 200, f"Response took {elapsed}ms (limit: 200ms)"
  
  e2e_test_example: |
    # tests/e2e/test_comparison_flow.py
    
    import pytest
    from httpx import AsyncClient
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    class TestComparisonFlowE2E:
  """Tests end-to-end del flujo completo de comparación"""
  
  async def test_complete_comparison_workflow(
self,
test_client: AsyncClient
  ):
"""
Flujo completo: Listar productos → Seleccionar → Comparar
"""
# Step 1: Obtener lista de productos disponibles
list_response = await test_client.get("/api/v1/products")
assert list_response.status_code == 200
products = list_response.json()
assert len(products) > 0

# Step 2: Seleccionar 3 productos para comparar
selected_ids = [p["id"] for p in products[:3]]

# Step 3: Realizar comparación
compare_response = await test_client.get(
    "/api/v1/products/compare/batch",
    params={"product_ids": selected_ids}
)

# Validaciones finales
assert compare_response.status_code == 200
compared_products = compare_response.json()
assert len(compared_products) == 3

# Verificar estructura completa de respuesta
for product in compared_products:
    assert "id" in product
    assert "name" in product
    assert "price" in product
    assert "rating" in product
    assert "specifications" in product
    assert product["id"] in selected_ids

# ----------------------------------------------------------------------------
# PYTEST CONFIGURATION
# ----------------------------------------------------------------------------
pytest_configuration: |
  # pytest.ini
  [pytest]
  minversion = 7.0
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  
  # Markers
  markers =
unit: Unit tests (fast, isolated)
integration: Integration tests (moderate speed)
e2e: End-to-end tests (slow)
performance: Performance tests
slow: Slow tests (>1s)
  
  # Coverage
  addopts =
--cov=src
--cov-report=html
--cov-report=term-missing
--cov-fail-under=80
-v
-ra
--strict-markers
--disable-warnings
  
  # Async support
  asyncio_mode = auto

# ----------------------------------------------------------------------------
# QUALITY GATES
# ----------------------------------------------------------------------------
quality_gates:
  mandatory:
    - coverage: ">= 85%"
    - test_execution_time: "< 10 seconds (all tests)"
    - no_skipped_tests: true
    - no_warnings: true
    - type_hints: "100%"
    - docstrings: "100%"
  
  code_quality:
    - "All tests use Arrange-Act-Assert pattern"
    - "Test names are descriptive (what, when, then)"
    - "One logical assertion per test"
    - "No hard-coded values (use fixtures/constants)"
    - "No print statements (use logging)"
    - "No sleep() calls (use mocking)"

# ----------------------------------------------------------------------------
# SUCCESS CRITERIA
# ----------------------------------------------------------------------------
success_criteria:
  must_have:
    - "Coverage >= 85%"
    - "All tests pass (0 failures)"
    - "Tests execute in < 10s"
    - "No flaky tests"
    - "CI/CD ready (pytest.ini configured)"
    - "Clear test organization (unit/integration/e2e)"
    - "Fixtures properly defined in conftest.py"
    - "Test data in fixtures folder"
  
  nice_to_have:
    - "Parameterized tests for edge cases"
    - "Performance benchmarks"
    - "Property-based tests (hypothesis)"
    - "Mutation testing score > 70%"
    - "Test documentation in README"

# ----------------------------------------------------------------------------
# IMPLEMENTATION INSTRUCTIONS
# ----------------------------------------------------------------------------
implementation_instructions: |
  
  PASO 1: SETUP INICIAL
  ----------------------
  1. Instalar dependencias:
     pip install pytest pytest-asyncio pytest-cov httpx pytest-mock faker
  
  2. Crear estructura de directorios:
     mkdir -p tests/{unit,integration,e2e,fixtures}
  
  3. Crear pytest.ini con configuración básica
  
  PASO 2: FIXTURES Y TEST DATA
  -----------------------------
  1. Crear tests/conftest.py con fixtures compartidos
  2. Crear tests/fixtures/test_products.json con datos de prueba
  3. Implementar fixtures para:
     - Mock repository
     - Mock services
     - Test client (AsyncClient)
     - Sample data
  
  PASO 3: UNIT TESTS (70% del esfuerzo)
  --------------------------------------
  1. tests/unit/test_domain_models.py
     - Validación de modelos Pydantic
     - Serialización/deserialización
     - Edge cases en validaciones
  
  2. tests/unit/test_services.py
     - Lógica de negocio del ProductService
     - Manejo de errores
     - Validaciones de entrada
     - Mock de dependencias
  
  3. tests/unit/test_validators.py (si existen)
     - Validación de UUIDs
     - Validación de parámetros
  
  PASO 4: INTEGRATION TESTS (20% del esfuerzo)
  ---------------------------------------------
  1. tests/integration/test_repositories.py
     - Carga de datos desde JSON/CSV
     - Búsqueda por ID
     - Búsqueda en batch
  
  2. tests/integration/test_api_routes.py
     - Endpoints completos con TestClient
     - Validación de respuestas
     - Status codes
     - Error handling
  
  PASO 5: E2E TESTS (10% del esfuerzo)
  -------------------------------------
  1. tests/e2e/test_comparison_flow.py
     - Flujo completo de comparación
     - Integración de múltiples endpoints
  
  PASO 6: VERIFICACIÓN
  ---------------------
  1. Ejecutar: pytest -v --cov=src --cov-report=html
  2. Verificar coverage >= 85%
  3. Verificar tiempo de ejecución < 10s
  4. Revisar reporte HTML en htmlcov/index.html
  5. Corregir tests faltantes o fallidos
  
  PASO 7: CI/CD INTEGRATION
  --------------------------
  1. Crear .github/workflows/tests.yml (si usando GitHub Actions)
  2. Configurar pre-commit hooks (opcional)
  3. Documentar en README cómo ejecutar tests

# ----------------------------------------------------------------------------
# ANTI-PATTERNS TO AVOID
# ----------------------------------------------------------------------------
anti_patterns:
  never_do:
    - "Tests que dependen de orden de ejecución"
    - "Tests que modifican estado global"
    - "Tests con sleep() o time.sleep()"
    - "Tests que dependen de servicios externos reales"
    - "Tests con valores hard-coded sin explicación"
    - "Tests sin assertions"
    - "Tests genéricos sin propósito claro"
    - "Copy-paste de tests sin adaptar"
    - "Mock de todo (over-mocking)"
    - "Tests que testean el framework, no tu código"

# ----------------------------------------------------------------------------
# FINAL CHECKLIST
# ----------------------------------------------------------------------------
final_checklist: |
  Antes de considerar la tarea completa, verifica:
  
   Estructura
     - Carpetas unit/integration/e2e creadas
     - conftest.py con fixtures
     - pytest.ini configurado
     - Test data en fixtures/
  
   Coverage
     - Domain models: 90%+
     - Services: 90%+
     - Repositories: 85%+
     - API routes: 80%+
     - Total: 85%+
  
   Test Quality
     - Nombres descriptivos
     - Arrange-Act-Assert pattern
     - Type hints presentes
     - Docstrings en tests complejos
     - Parametrized tests donde aplique
  
   Execution
     - Todos los tests pasan
     - Tiempo total < 10s
     - Sin warnings
     - Sin tests skipped
  
   Documentation
     - README actualizado con comandos
     - Comentarios en tests complejos
     - Coverage report generado

# ----------------------------------------------------------------------------
# END OF PROMPT
# ----------------------------------------------------------------------------
---
