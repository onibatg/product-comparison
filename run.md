# Cómo Ejecutar el Proyecto

Este archivo detalla los pasos necesarios para configurar y ejecutar el microservicio de comparación de productos.

## 1. Requisitos Previos

Tener instalado lo siguiente:

*   **Python 3.11+**
*   **pip** (gestor de paquetes de Python)

## 2. Configuración del Entorno

Sigue estos pasos para preparar tu entorno de desarrollo:

### 2.1. Clonar el Repositorio (si aún no lo has hecho)

```bash
git clone https://github.com/onibatg/product-comparison.git
cd product-comparison
```

### 2.2. Crear y Activar un Entorno Virtual

Usar un entorno virtual para aislar las dependencias del proyecto.

```bash
python -m venv .venv
# Para activar en Windows:
.venv\Scripts\activate
# Para activar en macOS/Linux:
source .venv/bin/activate
```

### 2.3. Instalar Dependencias

Una vez activado el entorno virtual, instalar todas las dependencias del proyecto usando `pip`:

```bash
pip install -r requirements.txt
```

## 3. Ejecutar el Microservicio

El microservicio está construido con FastAPI y se ejecuta con Uvicorn.

### 3.1. Iniciar el Servidor

Desde la raíz del proyecto, ejecuta el siguiente comando:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3.2. Acceder a la Documentación de la API

Una vez que el servidor esté en funcionamiento, puedes acceder a la documentación interactiva de la API (Swagger UI) en tu navegador:

*   **Swagger UI:** `http://localhost:8000/docs`

## 4. Ejecutar los Tests

El proyecto incluye una suite de tests unitarios, de integración y end-to-end utilizando `pytest`.

### 4.1. Ejecutar Todos los Tests

Desde la raíz del proyecto, puedes ejecutar todos los tests con el siguiente comando:

```bash
pytest
```

### 4.2. Ejecutar Tests Específicos

Puedes ejecutar tests de un módulo o carpeta específica:

```bash
pytest tests/unit/
pytest tests/integration/test_api_routes.py
```

### 4.3. Ejecutar Tests con Cobertura de Código

Para generar un informe de cobertura de código, usa `pytest-cov`:

```bash
pytest --cov=src --cov-report=term-missing
```

### 4.4. Ejecutar Tests y Guardar Resultados en un Archivo

Para guardar los resultados de los tests en un archivo Markdown (ej. `test_results.md`):

```bash
pytest --cov=src --cov-report=term-missing -v --tb=short --html=test_results.html --self-contained-html > test_results.md
```
**Nota:** El comando anterior genera un informe HTML y redirige la salida de la consola a `test_results.md`.

## 5. Datos de Prueba

El microservicio utiliza un archivo `data/products.json` para cargar datos de productos.

---
