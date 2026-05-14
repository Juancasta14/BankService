# TECH_CONSTRAINTS.md -- BankService: API Bancaria

## 1. Stack obligatorio
- **Lenguaje:** Python 3.11 o superior.
- **Backend:** FastAPI como framework web para exponer los endpoints (Adaptador HTTP).
- **Persistencia:** SQLAlchemy 2.0+ como ORM.
- **Base de Datos:** PostgreSQL (o Supabase) en entorno real.
- **Infraestructura:** Docker y Docker Compose para asegurar despliegues reproducibles.
- **Testing:** Pytest para la suite de pruebas unitarias (en memoria) y E2E.
- **Frontend:** Flask (exclusivo para el frontend independiente que consume la API, ubicado en `flask_app`).
- **Aislamiento de Dependencias:** Es obligatorio el uso de un entorno virtual (`.venv`) aislando las dependencias definidas en `requirements.txt`.

## 2. Prohibiciones (Restricciones Arquitectónicas)
- **Prohibido** importar o acoplar `FastAPI`, `Flask`, `SQLAlchemy`, `Requests`, `JSON` o `Pydantic` dentro de las carpetas `domain` o `application`.
- **Prohibido** modificar los balances de `Account` directamente desde los adaptadores (ej. rutas web) sin pasar por el caso de uso que verifica las invariantes.
- **Prohibido** procesar transferencias o pagos sin usar el patrón `UnitOfWork` (para evitar saldos inconsistentes si el sistema falla a la mitad).
- **Prohibido** usar SQLite para pruebas, el sistema debe usar implementaciones en memoria (`MockRepository`) en su lugar.
- **Prohibido** versionar o comitear archivos `.env` con credenciales reales en Git.

## 3. Convenciones de código
- **Idioma del código:** El código fuente (clases, variables, métodos y docstrings) de BankService debe estar íntegramente en **inglés**.
- **Nomenclatura:** Los archivos Python deben nombrarse en `snake_case` (ej. `pse_payments.py`), y las clases en `PascalCase`.
- **Tipado Fuerte:** Se requiere el uso riguroso de Type Hints (`typing`) en las firmas de todos los métodos y casos de uso.
- **Testing Obligatorio y Estructura:** 
  - `tests/unit/`: Debe contener pruebas ultrarrápidas usando `MockRepository` y `MockUoW`. Se debe testear el 100% de los archivos dentro de `domain/` y `application/`.
  - `tests/e2e/` (o integration): Debe testear la conexión real de los adaptadores (`FastAPI` y `SQLAlchemy`) usando un motor de base de datos de pruebas o en memoria, validando respuestas HTTP (200, 400).
- **Trazabilidad (Bitácora):** Ningún paso de desarrollo se considera terminado si la ejecución, las decisiones (DEC) y los bloqueos (BLOQ) no fueron registrados en `plan/BITACORA.md`.

## 4. Criterio de aceptación global
El sistema se considera estable y funcional cuando:
1. El comando `pytest tests/` logra una ejecución exitosa, obteniendo un **100% de cobertura** sobre el dominio y los casos de uso en **menos de 2 segundos** (Modo Memoria).
2. Los contenedores de Docker (FastAPI y Flask) pueden levantarse sin errores mediante `docker-compose up`.
3. Es posible autenticarse, consultar cuentas y procesar transacciones correctamente a través de la API expuesta.
