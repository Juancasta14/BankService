# ARCHITECTURE.md -- BankService: API Bancaria con Arquitectura Hexagonal

## 1. Principio rector
La capa de dominio (`domain`) y la capa de aplicación (`application`) no conocen en absoluto sobre Flask, FastAPI, HTTP, JSON, SQLAlchemy, PostgreSQL, AWS Lambda, variables de entorno, ni detalles de la interfaz o la persistencia. Son código Python puro.

## 2. Estilo arquitectónico
Se utiliza **Arquitectura Hexagonal (Ports & Adapters)** estructurada en tres zonas principales:
- **`domain`**: Entidades puras de negocio (`User`, `Account`, `Movement`, `Wallet`), excepciones de negocio (`InsufficientFunds`, `InvalidCredentials`), e invariantes.
- **`application`**: Casos de uso (`TransferService`, `LoginService`, `CreatePSEPaymentService`) y puertos (interfaces abstractas / protocolos como `AccountsRepository`, `UnitOfWork`, `TokenService`).
- **`adapters`**: Implementaciones técnicas:
  - **`inbound`**: Rutas HTTP de FastAPI (reciben peticiones web y llaman a los casos de uso).
  - **`outbound`**: Repositorios basados en SQLAlchemy, utilidades criptográficas para JWT/Hashing, y notificaciones HTTP a servicios externos (ej. AWS Lambda).

## 3. Estructura de Directorios
```text
App/
├── fastapi_app/
│   ├── domain/              # Entidades puras y excepciones del negocio (núcleo)
│   ├── application/         # Casos de uso y definición de puertos (interfaces)
│   ├── adapters/            # Implementaciones de infraestructura
│   │   ├── inbound/http/    # Controladores FastAPI (routers)
│   │   └── outbound/        # Repositorios (SQLAlchemy, Mocks), utilidades (JWT)
│   ├── tests/
│   │   ├── unit/            # Pruebas unitarias ultrarrápidas con Mocks
│   │   └── e2e/             # Pruebas integrales contra la API
│   └── main.py              # Punto de entrada e Inyección de Dependencias
└── flask_app/               # Aplicación cliente web independiente
```

## 4. Reglas de dependencia
- `domain/` no importa absolutamente NADA de `application/` ni de `adapters/`.
- `application/` solo puede importar de `domain/`.
- `adapters/` puede importar de `application/` y de `domain/`.
- El flujo de control en tiempo de ejecución se invierte mediante Inyección de Dependencias (DI): los adaptadores de entrada instancian los casos de uso pasándoles (inyectando) los adaptadores de salida.
- Las dependencias de código siempre apuntan hacia el núcleo (adentro).

## 5. Puertos principales
La capa de aplicación define interfaces estrictas (puertos) que la infraestructura debe implementar, por ejemplo:
- `UserRepository(Protocol)`
- `AccountsRepository(Protocol)`
- `PSETransactionRepository(Protocol)`
- `UnitOfWork(ABC)`
- `TokenService(Protocol)`
- `PasswordHasher(Protocol)`

## 6. Adaptadores permitidos
- **Entrada (Inbound):**
  - Controladores y routers HTTP basados en FastAPI en `adapters/inbound/http/`.
  - Scripts de inicialización o tests unitarios que ejecutan los casos de uso directamente.
- **Salida (Outbound):**
  - Persistencia relacional usando SQLAlchemy en `adapters/outbound/persistence/sqlalchemy/`.
  - Servicios de seguridad (PyJWT, Passlib) en `adapters/outbound/security/`.
  - Mock Repositories para ejecución en "Modo Memoria" sin base de datos.
- **Frontend:** Existe una aplicación web independiente (en `flask_app`) que actúa como cliente de la API HTTP.

## 7. Verificación arquitectónica mínima
Se debe asegurar mediante comprobaciones estáticas que las capas internas están totalmente limpias de frameworks de infraestructura.

PowerShell:
```powershell
Get-ChildItem .\App\fastapi_app\domain -Recurse -Filter *.py | Select-String -Pattern "fastapi|flask|sqlalchemy|pydantic|requests|http"
Get-ChildItem .\App\fastapi_app\application -Recurse -Filter *.py | Select-String -Pattern "fastapi|flask|sqlalchemy|pydantic|requests|http"
```

Bash o Git Bash:
```bash
grep -R -E "fastapi|flask|sqlalchemy|pydantic|requests|http" App/fastapi_app/domain || true
grep -R -E "fastapi|flask|sqlalchemy|pydantic|requests|http" App/fastapi_app/application || true
```
La verificación se considera **aprobada** cuando los comandos no devuelven ninguna importación de estas librerías dentro de las carpetas de `domain/` y `application/`. (Librerías estándar como `dataclasses`, `typing`, `datetime` o `enum` están permitidas).
