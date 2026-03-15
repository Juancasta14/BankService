# PUERTOS.md — Catálogo Completo de Puertos 🔌

**Proyecto:** BankService (Arquitectura Hexagonal)
**Patrón:** Ports & Adapters (Hexagonal Architecture)

En la Arquitectura Hexagonal todos los puertos son **interfaces abstractas** (`Protocol` de Python). Definen el **contrato** que el núcleo necesita del mundo exterior, sin importar la implementación concreta.

---

## Índice

1. [Auth — Puertos Outbound](#1-autenticación--puertos-outbound)
   - [UserRepository](#11-userrepository)
   - [PasswordHasher](#12-passwordhasher)
   - [TokenService](#13-tokenservice)
   - [LoginNotifier](#14-loginnotifier)
2. [Customers — Puertos Outbound](#2-clientes--puertos-outbound)
   - [AccountsRepository](#21-accountsrepository)
   - [MovementsRepository](#22-movementsrepository)
   - [WalletsRepository](#23-walletsrepository)
3. [PSE — Puertos Outbound](#3-pse--puertos-outbound)
   - [PSETransactionRepository](#31-psetransactionrepository)
   - [AccountRepository (PSE)](#32-accountrepository-pse)
   - [MovementRepository (PSE)](#33-movementrepository-pse)
   - [UnitOfWork](#34-unitofwork)

---

## 1. Autenticación — Puertos Outbound

### 1.1 `UserRepository`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/auth/ports/user_repository.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Permite que los casos de uso de autenticación busquen usuarios sin conocer cómo están almacenados. El core nunca sabe si el usuario viene de PostgreSQL, un CSV o un diccionario en memoria. |
| **Usado por** | `LoginService`, `AuthenticateService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `get_by_username` | `(username: str) -> Optional[User]` | Busca un usuario por nombre de usuario. Retorna `None` si no existe. |
| `get_by_id` | `(user_id: int) -> Optional[User]` | Busca un usuario por su ID numérico. Retorna `None` si no existe. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `UserRepositorySQLAlchemy` | `adapters/outbound/persistence/sqlalchemy/user_repository_sqlalchemy.py` | Producción (PostgreSQL) |
| `MockUserRepository` | `tests/unit/application/auth/mock_ports.py` | Tests unitarios (RAM) |

---

### 1.2 `PasswordHasher`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/auth/ports/password_hasher.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Abstrae el algoritmo de hashing de contraseñas. El caso de uso `LoginService` puede verificar credenciales sin conocer si se usa `bcrypt`, `argon2` o cualquier otra estrategia. Facilita el cambio de algoritmo sin tocar la lógica de autenticación. |
| **Usado por** | `LoginService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `verify` | `(plain_password: str, hashed_password: str) -> bool` | Compara una contraseña en texto plano contra su hash. Retorna `True` si coinciden. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `PasslibHasher` | `adapters/outbound/security/password_hasher_passlib.py` | Producción (`passlib` + `bcrypt`) |
| `MockPasswordHasher` | `tests/unit/application/auth/mock_ports.py` | Tests unitarios (comparación directa) |

---

### 1.3 `TokenService`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/auth/ports/token_service.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Abstrae la creación y decodificación de tokens de acceso (JWT). La capa de aplicación puede emitir y leer tokens sin acoplarse a `python-jose` ni al estándar JWT en particular. |
| **Usado por** | `LoginService`, `AuthenticateService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `create_access_token` | `(subject: str) -> str` | Genera un token JWT firmado a partir del identificador de usuario (`username`). |
| `decode_subject` | `(token: str) -> Optional[str]` | Decodifica un token JWT y retorna el `subject`. Retorna `None` si el token es inválido o expirado. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `JWTTokenService` | `adapters/outbound/security/jwt_token_service.py` | Producción (`python-jose`) |
| `MockTokenService` | `tests/unit/application/auth/mock_ports.py` | Tests unitarios |

---

### 1.4 `LoginNotifier`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/auth/ports/login_notifier.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Emite un evento cada vez que se intenta un login, sea exitoso o no. Permite registrar auditoría de accesos o disparar alertas de seguridad en un sistema externo (p. ej. AWS Lambda), sin que `LoginService` sepa nada del canal de notificación. |
| **Usado por** | `LoginService` (en modo silencioso: si el notificador falla, el login sigue funcionando) |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `notify_login` | `(*, user_id: int \| None, username: str, success: bool, ip: str \| None, user_agent: str \| None) -> None` | Notifica el intento de login con metadatos contextuales: IP, User-Agent, y si fue exitoso. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `HttpLoginNotifier` | `adapters/outbound/notifications/http_login_notifier.py` | Producción (POST a AWS Lambda URL) |
| `MockLoginNotifier` | `tests/unit/application/auth/mock_ports.py` | Tests unitarios (guarda eventos en lista) |

---

## 2. Clientes — Puertos Outbound

### 2.1 `AccountsRepository`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/customers/ports/outbound/accounts_repository.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Permite a los casos de uso de clientes leer y persistir cuentas bancarias. Separa la regla "qué es una cuenta y qué operaciones permite" de "cómo se guarda en base de datos". |
| **Usado por** | `GetAccountsService`, `GetSummaryService`, `TransferService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `get` | `(account_id: int) -> Account \| None` | Obtiene una cuenta por su ID. |
| `save` | `(account) -> None` | Persiste los cambios de una cuenta (balance actualizado, etc.). |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `AccountsRepositorySQLAlchemy` | `adapters/outbound/persistence/sqlalchemy/accounts_repository_sqlalchemy.py` | Producción (PostgreSQL) |
| `MockAccountsRepository` (dict en RAM) | `tests/unit/application/customers/test_info_services.py` y `test_transfer_service.py` | Tests unitarios |

---

### 2.2 `MovementsRepository`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/customers/ports/outbound/movements_repository.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Abstrae la consulta del historial de movimientos de un cliente. Permite filtrar por tipo de cuenta y rango de fechas sin que el caso de uso conozca SQL. |
| **Usado por** | `GetMovementsService`, `GetSummaryService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `list_by_customer` | `(customer_id: int, account_type: Optional[str], date_from: Optional[str], date_to: Optional[str]) -> list` | Lista los movimientos de un cliente con filtros opcionales. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `MovementsRepositorySQLAlchemy` | `adapters/outbound/persistence/sqlalchemy/movements_repository_sqlalchemy.py` | Producción (PostgreSQL) |
| `MockMovementsRepository` | `tests/unit/application/customers/test_info_services.py` | Tests unitarios |

---

### 2.3 `WalletsRepository`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/customers/ports/outbound/wallets_repository.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Abstrae el acceso a la billetera virtual de un cliente. Separa el concepto de negocio "saldo disponible en billetera" de la lógica de persistencia. |
| **Usado por** | `GetWalletService`, `GetSummaryService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `get_by_customer` | `(customer_id: int) -> Wallet \| None` | Retorna la billetera de un cliente. Retorna `None` si no tiene billetera activa. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `WalletsRepositorySQLAlchemy` | `adapters/outbound/persistence/sqlalchemy/wallets_repository_sqlalchemy.py` | Producción (PostgreSQL) |
| `MockWalletsRepository` | `tests/unit/application/customers/test_info_services.py` | Tests unitarios |

---

## 3. PSE — Puertos Outbound

### 3.1 `PSETransactionRepository`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/pse/ports/outbound/pse_transaction_repository.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Gestiona el ciclo de vida de las transacciones PSE: creación, búsqueda y actualización de estado (PENDING → APPROVED / REJECTED / EXPIRED). Aísla la persistencia del flujo de pagos. |
| **Usado por** | `CreatePSEPaymentService`, `GetPSEPaymentService`, `ProcessPSEGatewayService`, `ProcessPSECallbackService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `get_by_internal_order_id` | `(internal_order_id: str) -> PSETransaction \| None` | Recupera una transacción por su identificador único interno. |
| `add` | `(tx) -> None` | Registra una nueva transacción PSE en estado PENDING. |
| `save` | `(tx) -> None` | Persiste los cambios de estado de una transacción existente. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `PSETransactionRepositorySQLAlchemy` | `adapters/outbound/persistence/sqlalchemy/pse_transaction_repository_sqlalchemy.py` | Producción (PostgreSQL) |
| `MockPSETransactionRepository` | `tests/unit/application/pse/mock_uow_pse.py` | Tests unitarios |

---

### 3.2 `AccountRepository` (PSE)

| Campo | Detalle |
|---|---|
| **Archivo** | `application/pse/ports/outbound/account_repository.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Versión especializada del repositorio de cuentas para el contexto PSE. Permite que los servicios de pago lean y actualicen saldos de cuentas bancarias de forma atómica, dentro de la misma unidad de trabajo (UoW). |
| **Usado por** | `CreatePSEPaymentService`, `ProcessPSEGatewayService`, `ProcessPSECallbackService` (vía `UnitOfWork.accounts`) |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `get` | `(account_id: int) -> Account \| None` | Obtiene una cuenta bancaria por ID. |
| `save` | `(account) -> None` | Persiste cambios de saldo de la cuenta (débito/crédito). |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `AccountsRepositorySQLAlchemy` | `adapters/outbound/persistence/sqlalchemy/accounts_repository_sqlalchemy.py` | Producción (reutilizado dentro del UoW) |
| `MockAccountRepository` (PSE) | `tests/unit/application/pse/mock_uow_pse.py` | Tests unitarios |

---

### 3.3 `MovementRepository` (PSE)

| Campo | Detalle |
|---|---|
| **Archivo** | `application/pse/ports/outbound/movement_repository.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Registra los movimientos contables derivados del flujo PSE: un crédito al recibirse un pago exitoso, y los dos asientos (débito + crédito) de una transferencia. Mantiene el libro contable del banco independiente de cómo se almacena. |
| **Usado por** | `TransferService`, `ProcessPSECallbackService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `add_credit` | `(*, account_id, customer_id, account_type, date, description, amount) -> None` | Registra un movimiento tipo crédito (abono). Ej: pago PSE exitoso. |
| `add_transfer_movements` | `(*, acc_out_id, acc_in_id, customer_out_id, customer_in_id, acc_out_type, acc_in_type, date, amount) -> None` | Registra los 2 asientos de una transferencia: débito en origen y crédito en destino. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `MovementRepositorySQLAlchemy` | `adapters/outbound/persistence/sqlalchemy/movement_repository_sqlalchemy.py` | Producción (PostgreSQL) |
| `MockMovementRepository` | `tests/unit/application/pse/mock_uow_pse.py` | Tests unitarios |

---

### 3.4 `UnitOfWork`

| Campo | Detalle |
|---|---|
| **Archivo** | `application/pse/ports/outbound/unit_of_work.py` |
| **Tipo** | `Protocol` (Outbound) |
| **Intención de negocio** | Agrupa múltiples operaciones de repositorio en una sola **transacción atómica**. Si algún paso falla, se hace rollback de todo. Es crítico para garantizar la consistencia en flujos multi-paso como crear un pago PSE (reservar saldo + crear transacción) o procesar un callback (actualizar transacción + acreditar cuenta + registrar movimiento). |
| **Contiene** | `pse: PSETransactionRepository`, `accounts: AccountRepository` |
| **Usado por** | `CreatePSEPaymentService`, `ProcessPSEGatewayService`, `ProcessPSECallbackService`, `TransferService` |

**Métodos expuestos:**

| Método | Firma | Descripción |
|---|---|---|
| `commit` | `() -> None` | Confirma todas las operaciones pendientes en la transacción actual. |
| `rollback` | `() -> None` | Revierte todas las operaciones si ocurre un error. |
| `pse` | _atributo_ | Acceso al `PSETransactionRepository` dentro de la unidad de trabajo. |
| `accounts` | _atributo_ | Acceso al `AccountRepository` dentro de la unidad de trabajo. |

**Adaptadores que lo implementan:**

| Adaptador | Archivo | Entorno |
|---|---|---|
| `UnitOfWorkSQLAlchemy` | `adapters/outbound/persistence/sqlalchemy/unit_of_work_sqlalchemy.py` | Producción (sesión SQLAlchemy con commit/rollback real) |
| `MockUnitOfWork` | `tests/unit/application/pse/mock_uow_pse.py` | Tests unitarios (operaciones en diccionarios RAM) |

---

## Resumen Visual

```
Dominio / Application Core
         │
         ▼
┌─────────────────────────────────────────────────────┐
│               PUERTOS (Interfaces ABC/Protocol)     │
│                                                     │
│  AUTH                CUSTOMERS        PSE           │
│  ├─ UserRepository   ├─ Accounts      ├─ PSETxRepo  │
│  ├─ PasswordHasher   ├─ Movements     ├─ AccountRepo│
│  ├─ TokenService     └─ Wallets       ├─ MovRepo    │
│  └─ LoginNotifier                    └─ UnitOfWork  │
└─────────────────────────────────────────────────────┘
         │
         ▼  (implementado por)
┌─────────────────────────────────────────────────────┐
│            ADAPTADORES (Implementaciones)            │
│                                                     │
│  Producción            Tests                        │
│  ├─ SQLAlchemy repos   ├─ MockUoW                   │
│  ├─ JWTTokenService    ├─ MockRepositories          │
│  ├─ PasslibHasher      └─ MockNotifier              │
│  └─ HttpLoginNotifier                               │
└─────────────────────────────────────────────────────┘
```

> **Total de puertos:** 11 interfaces | **Total de adaptadores de producción:** 8 | **Total de adaptadores de test:** 8
