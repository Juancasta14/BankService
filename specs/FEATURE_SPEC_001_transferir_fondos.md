# FEATURE_SPEC_001_transferir_fondos.md -- Transferencia entre cuentas

## Bloque 1. Objetivo y precondiciones
- **Actor:** Usuario autenticado en el sistema.
- **Objetivo:** Mover dinero desde su cuenta origen hacia una cuenta destino de forma segura y atómica.
- **Precondiciones:**
  - Ambas cuentas (origen y destino) deben existir en el repositorio.
  - La cuenta de origen debe pertenecer al usuario autenticado (verificado en adaptadores HTTP o por el dominio).

## Bloque 2. Entrada
Entrada esperada por el caso de uso (`TransferService`):
```json
{
  "source_account_id": 1,
  "target_account_id": 2,
  "amount": 50000.00
}
```

## Bloque 3. Flujo principal
1. Se inicializa el contexto usando el `UnitOfWork`.
2. El repositorio carga en memoria la entidad `source` y la entidad `target`.
3. Se validan las invariantes: 
   - Que ambas existan.
   - Que el monto a transferir sea `> 0`.
   - Que `source.id != target.id`.
   - Que `source.balance >= amount`.
4. Se descuenta el monto de `source` y se suma al `target`.
5. Se crean registros inmutables (`Movement`) de tipo DEBIT para el origen y CREDIT para el destino.
6. El `UnitOfWork` hace `commit()` guardando todo atómicamente.

## Bloque 4. Errores de dominio (Excepciones esperadas)
- `InvalidAmount`: Lanzado si `amount <= 0`.
- `SameAccount`: Lanzado si origen y destino coinciden.
- `InsufficientFunds`: Lanzado si no hay fondos suficientes para cubrir el `amount`.
- `AccountNotFound`: Lanzado si alguna de las dos cuentas no es encontrada.

## Bloque 5. Criterios de aceptación
- **AC-01:** Una transferencia exitosa altera correctamente ambos saldos y guarda los `Movements`.
- **AC-02:** Enviar `amount = 0` o un número negativo lanza `InvalidAmount` y el UoW hace rollback.
- **AC-03:** Intentar transferir más del saldo actual lanza `InsufficientFunds` y el UoW hace rollback.
- **AC-04:** Una transferencia hacia la misma cuenta arroja `SameAccount` y aborta.
- **AC-05 (Atomicidad):** Si por cualquier error de infraestructura falla la grabación en destino, el débito al origen debe cancelarse automáticamente.
