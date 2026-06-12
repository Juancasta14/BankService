# Reporte de Transacciones y Movimientos - Noviembre 2025

Este reporte resume la actividad registrada en la base de datos durante el mes de noviembre de 2025, cubriendo tanto los **Movimientos de Cuenta** ([MovementDB](file:///C:/Users/Cristian%20Rivera/work_spaces/BankService/App/fastapi_app/adapters/outbound/persistence/sqlalchemy/models.py#L54)) como las **Transacciones PSE** ([PSETransactionDB](file:///C:/Users/Cristian%20Rivera/work_spaces/BankService/App/fastapi_app/adapters/outbound/persistence/sqlalchemy/models.py#L72)).

---

## 1. Resumen de Actividad

| Métrica | Movimientos de Cuenta (`movements`) | Transacciones PSE (`pse_transactions`) |
| :--- | :---: | :---: |
| **Total de Registros** | 16 | 38 |
| **Volumen Total (Monto)** | $4,891.50 | $12,058.00 |

---

## 2. Movimientos de Cuenta (`movements`)

Estos son los 16 movimientos contables registrados en las cuentas del banco durante noviembre de 2025, ordenados cronológicamente:

| ID | ID Cuenta | ID Cliente | Tipo Cuenta | Fecha | Descripción | Monto | Tipo |
| :---: | :---: | :---: | :--- | :---: | :--- | :---: | :--- |
| **5** | 3 | 101 | ahorros | 2025-11-14 | Depósito en efectivo | $2,000.00 | credito |
| **1** | 1 | 100 | ahorros | 2025-11-15 | Nómina | $1,200.00 | credito |
| **2** | 1 | 100 | ahorros | 2025-11-16 | Pago supermercado | $150.50 | debito |
| **3** | 2 | 100 | corriente | 2025-11-17 | Pago tarjeta de crédito | $300.00 | debito |
| **4** | 2 | 100 | corriente | 2025-11-18 | Transferencia recibida | $500.00 | credito |
| **6** | 3 | 101 | ahorros | 2025-11-19 | Pago servicios públicos | $220.75 | debito |
| **7** | 2 | 100 | corriente | 2025-11-24 | Transferencia enviada a cuenta 1 | $100.00 | debito |
| **8** | 1 | 100 | ahorros | 2025-11-24 | Transferencia recibida desde cuenta 2 | $100.00 | credito |
| **9** | 2 | 100 | corriente | 2025-11-24 | Transferencia enviada a cuenta 1 | $100.00 | debito |
| **10** | 1 | 100 | ahorros | 2025-11-24 | Transferencia recibida desde cuenta 2 | $100.00 | credito |
| **11** | 1 | 100 | ahorros | 2025-11-24 | Transferencia enviada a cuenta 2 | $100.00 | debito |
| **12** | 2 | 100 | corriente | 2025-11-24 | Transferencia recibida desde cuenta 1 | $100.00 | credito |
| **13** | 1 | 100 | ahorros | 2025-11-24 | Transferencia enviada a cuenta 2 | $100.00 | debito |
| **14** | 2 | 100 | corriente | 2025-11-24 | Transferencia recibida desde cuenta 1 | $100.00 | credito |
| **15** | 2 | 100 | corriente | 2025-11-24 | Transferencia enviada a cuenta 3 | $100.00 | debito |
| **16** | 3 | 101 | ahorros | 2025-11-24 | Transferencia recibida desde cuenta 2 | $100.00 | credito |

---

## 3. Transacciones PSE (`pse_transactions`)

Durante noviembre de 2025 se iniciaron 38 transacciones a través de la pasarela PSE. A continuación se presenta el estado de dichas transacciones:

### Resumen por Estado
* **APPROVED (Aprobadas)**: 17 transacciones (Monto Total: $11,940.00)
* **PENDING (Pendientes)**: 20 transacciones (Monto Total: $117.00)
* **REJECTED (Rechazadas)**: 1 transacción (Monto Total: $1.00)

### Listado Completo de Transacciones PSE

| ID | ID Orden Interna | ID Cliente | ID Cuenta | Monto | Estado | Creado El |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | PSE-8e52ee91b9d047cc9812 | 100 | 1 | $1.00 | PENDING | 2025-11-24 00:29 |
| **2** | PSE-2d3607539c604bedb04b | 100 | 1 | $1.00 | APPROVED | 2025-11-24 01:45 |
| **3** | PSE-0e342b3bed12412aa788 | 100 | 1 | $1.00 | PENDING | 2025-11-24 02:18 |
| **4** | PSE-da5e140011844291ac40 | 100 | 1 | $10.00 | PENDING | 2025-11-24 02:37 |
| **5** | PSE-4e276e0dcae445a88a1b | 100 | 1 | $1.00 | PENDING | 2025-11-24 02:45 |
| **6** | PSE-c2f365ea5cf242b2986d | 100 | 2 | $100.00 | PENDING | 2025-11-24 02:46 |
| **7** | PSE-c3f6b84f89354eb88725 | 100 | 1 | $1.00 | PENDING | 2025-11-24 02:54 |
| **8** | PSE-8869212775e24a469d26 | 100 | 1 | $1.00 | PENDING | 2025-11-24 03:15 |
| **9** | PSE-952fc9617af1442f8736 | 100 | 2 | $10.00 | PENDING | 2025-11-24 03:32 |
| **10** | PSE-26dd0a67eca84dd689d7 | 100 | 1 | $9.00 | PENDING | 2025-11-24 03:32 |
| **11** | PSE-10230fc8c35942ab9b4f | 100 | 1 | $1.00 | PENDING | 2025-11-24 03:38 |
| **12** | PSE-664c608da75347a190a0 | 100 | 1 | $100.00 | PENDING | 2025-11-24 03:39 |
| **13** | PSE-e905afb9883b4ea99132 | 100 | 1 | $100.00 | PENDING | 2025-11-24 03:39 |
| **14** | PSE-987310b6e42a4a1987ff | 100 | 1 | $100.00 | PENDING | 2025-11-24 03:42 |
| **15** | PSE-e1ce20224ae742d1b45b | 100 | 1 | $12.00 | PENDING | 2025-11-24 03:47 |
| **16** | PSE-6400d62831d242b8bc82 | 100 | 1 | $12.00 | PENDING | 2025-11-24 03:53 |
| **17** | PSE-a2a1dab09e1a4ee9801f | 100 | 1 | $100.00 | APPROVED | 2025-11-24 04:04 |
| **18** | PSE-7f3743863fc14b28bf62 | 100 | 1 | $100.00 | APPROVED | 2025-11-24 04:05 |
| **19** | PSE-c72320376f464a23a79d | 100 | 1 | $1.00 | APPROVED | 2025-11-24 04:22 |
| **20** | PSE-df55f5c3c5a24e2eac25 | 101 | 3 | $1.00 | APPROVED | 2025-11-24 04:29 |
| **21** | PSE-38f41887ec764bb2b775 | 101 | 3 | $1.00 | APPROVED | 2025-11-24 04:35 |
| **22** | PSE-773fbdd4432d44289dcf | 101 | 3 | $1.00 | APPROVED | 2025-11-24 04:36 |
| **23** | PSE-46f755b0c4d744fcb526 | 101 | 3 | $1.00 | REJECTED | 2025-11-24 04:46 |
| **24** | PSE-4a6efaa070564abfaecd | 101 | 3 | $1.00 | APPROVED | 2025-11-24 05:03 |
| **25** | PSE-d77453a126cd4d3b9072 | 101 | 3 | $1.00 | APPROVED | 2025-11-24 05:12 |
| **26** | PSE-fe62eed00f93492d8a5f | 101 | 3 | $1.00 | APPROVED | 2025-11-24 05:14 |
| **27** | PSE-f80c4c0750cb446fa86b | 101 | 3 | $1.00 | APPROVED | 2025-11-24 05:15 |
| **28** | PSE-196b1e4e90f84a77a159 | 101 | 3 | $1.00 | APPROVED | 2025-11-24 05:15 |
| **29** | PSE-a6fabbb0e643407e822e | 101 | 3 | $1.00 | APPROVED | 2025-11-24 05:16 |
| **30** | PSE-d88867e7026b46788ca1 | 101 | 3 | $9,990.00 | APPROVED | 2025-11-24 05:16 |
| **31** | PSE-45d346d68c784882b60e | 101 | 3 | $1.00 | APPROVED | 2025-11-24 05:19 |
| **32** | PSE-44c14576d17047ac8ac6 | 101 | 3 | $10.00 | APPROVED | 2025-11-27 00:56 |
| **33** | PSE-0aa5f7a460b045e68d10 | 101 | 3 | $10.00 | APPROVED | 2025-11-27 01:19 |
| **34** | PSE-99430fa770c045309171 | 101 | 3 | $1.00 | APPROVED | 2025-11-28 02:34 |
| **35** | PSE-ec43e62abc94463aa489 | 100 | 1 | $1.00 | APPROVED | 2025-11-28 02:34 |
| **36** | PSE-7638d8d6bf384f8ba0bc | 100 | 1 | $1.00 | APPROVED | 2025-11-28 02:42 |
| **37** | PSE-5b1c4317984a48b0b389 | 100 | 1 | $1,210.00 | APPROVED | 2025-11-28 02:47 |
| **38** | PSE-c32bf25af3674bf7b5ac | 100 | 2 | $100.00 | APPROVED | 2025-11-28 02:50 |
