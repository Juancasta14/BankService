# DOMAIN.md -- BankService: API Bancaria con Arquitectura Hexagonal

## 1. Lenguaje ubicuo
| Término | Definición |
|---|---|
| User | Cliente registrado y autenticado en el sistema bancario. |
| Account | Cuenta bancaria asociada a un User, con un balance (saldo) específico. |
| Movement | Registro histórico inmutable de una transacción que afectó el balance de una Account (débito o crédito). |
| Wallet | Producto financiero asociado al usuario para manejar saldos independientes de la cuenta principal. |
| Transferencia | Operación atómica de movimiento de fondos entre dos cuentas bancarias. |
| Pago PSE | Intención de pago iniciada por el sistema hacia una pasarela externa (PSE) que se resuelve de forma asíncrona. |

## 2. Aggregate roots
Dependiendo del contexto (Bounded Context), el sistema usa diferentes Aggregate Roots:
- Para el flujo de autenticación, `User` es el aggregate root.
- Para las operaciones financieras, `Account` actúa como la entidad principal que debe proteger las invariantes de negocio (su balance) antes de permitir que se generen `Movement`. Ninguna parte del sistema puede manipular saldos evadiendo las validaciones del dominio.

## 3. Invariantes
- **INV-01 (Saldo Positivo):** Una cuenta nunca puede quedar con saldo negativo. Si el balance no cubre el monto a debitar, la operación es estrictamente rechazada.
- **INV-02 (Transferencia Cíclica):** No se permite iniciar una transferencia donde la cuenta origen y la cuenta destino sean exactamente la misma.
- **INV-03 (Cantidades Válidas):** Todos los movimientos financieros (retiros, transferencias, pagos) deben ser por montos estrictamente mayores a cero.
- **INV-04 (Atomicidad Financiera):** Una transferencia entre cuentas exige un débito y un crédito simultáneos; si uno de los dos falla, el otro debe revertirse forzosamente (delegado al UnitOfWork de infraestructura, pero exigido por el diseño del caso de uso).

## 4. Errores de dominio
Ubicados en `domain/banking/exceptions.py`, `domain/auth/exceptions.py` (entre otros):
- `InsufficientFunds`: Lanzado cuando el balance de la cuenta no cubre el débito (protege INV-01).
- `SameAccount`: Lanzado cuando origen y destino coinciden en una transferencia (protege INV-02).
- `InvalidAmount`: Lanzado cuando el monto de la operación es 0 o negativo (protege INV-03).
- `AccountNotFound`: Lanzado cuando la cuenta solicitada para la operación no existe.
- `UserNotFound` / `InvalidCredentials`: Invariantes de autenticación insatisfechas.

## 5. Operaciones de dominio autorizadas
La lógica central de la capa de aplicación respeta estas operaciones:
- `TransferService`: Valida explícitamente `INV-01`, `INV-02` e `INV-03` antes de realizar restas y sumas en memoria. Luego delega la persistencia al `UnitOfWork`.
- Validaciones *fail-fast*: Antes de hacer cualquier cálculo matemático, los servicios deben verificar la existencia de los recursos (ej. verificar que origen y destino existan) y arrojar excepciones del dominio.

## 6. Reglas de nomenclatura y diseño
- **Inglés como idioma del código:** en todas las entidades, variables y clases están en inglés (`User`, `Account`, `BankingError`) para alinear con estándares de la industria.
- **Errores expresivos y puros:** Los errores de negocio son clases que heredan de una base genérica (ej. `BankingError` -> `Exception`), sin sufijos técnicos innecesarios (se llama `InsufficientFunds`, no `InsufficientFundsException`).
- **Interfaces Implícitas (Duck Typing):** Se utiliza activamente `typing.Protocol` para definir los puertos de los repositorios. Esto evita obligar a las clases de infraestructura a heredar forzosamente de las abstracciones del dominio, promoviendo el aislamiento real.
