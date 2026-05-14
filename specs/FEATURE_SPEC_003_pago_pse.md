# FEATURE_SPEC_003_pago_pse.md -- Creación y consolidación de Pago PSE

## Bloque 1. Objetivo y precondiciones
- **Actor:** Usuario autenticado (Inicia el pago) y Pasarela externa (Consolida el pago vía Webhook).
- **Objetivo:** Simular la integración con un sistema de pagos externos, manejando el asincronismo y garantizando los fondos.
- **Precondiciones:**
  - La cuenta de origen debe existir en el repositorio.
  - La cuenta debe tener fondos suficientes para cubrir el monto del pago PSE.

## Bloque 2. Entrada
Entrada para la inicialización del pago:
```json
{
  "account_id": 1,
  "amount": 120000.00
}
```

Entrada esperada en el Webhook de la pasarela:
```json
{
  "transaction_id": "pse-uuid-1234",
  "status": "APPROVED" // o "REJECTED"
}
```

## Bloque 3. Flujo principal
**Fase 1: Inicialización**
1. El usuario solicita pagar un servicio vía PSE.
2. El sistema valida la cuenta y que haya fondos suficientes (lanzando excepciones si aplica).
3. El sistema crea una transacción PSE en estado `PENDING`.
4. (Opcional) El sistema bloquea o reserva los fondos en la cuenta para evitar que el usuario los gaste mientras la pasarela responde.

**Fase 2: Resolución (Webhook asíncrono)**
1. La pasarela PSE llama al webhook del banco con el estado final (`APPROVED` o `REJECTED`).
2. Si es `APPROVED`, el `UnitOfWork` hace efectivo el débito consolidando el balance y marcando el pago como exitoso.
3. Si es `REJECTED`, la transacción se marca fallida y se liberan los fondos reservados (si aplicó la estrategia de congelamiento).

## Bloque 4. Errores de dominio
- `AccountNotFound`: Si la cuenta enviada a debitar no existe.
- `InsufficientFunds`: Si el usuario intenta inicializar un pago para el cual no tiene dinero.
- `InvalidAmount`: Si el pago es <= 0.
- `PSETransactionNotFound`: Si llega un webhook para una transacción que no figura en nuestros registros.

## Bloque 5. Criterios de aceptación
- **AC-01:** Inicializar un pago con saldo suficiente crea la transacción en `PENDING` y retorna el ID de rastreo.
- **AC-02:** Inicializar un pago sin fondos arroja `InsufficientFunds` antes de siquiera crear el registro.
- **AC-03:** Recibir un webhook con estado `APPROVED` debita la cuenta definitivamente.
- **AC-04:** Recibir un webhook con estado `REJECTED` cancela la operación y deja el saldo de la cuenta intacto.
