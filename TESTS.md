# TESTS.md — Reporte de Pruebas y Cobertura 🧪

**Proyecto:** BankService (Arquitectura Hexagonal)  
**Framework:** pytest 9.0.2 + pytest-cov 5.0.0  
**Python:** 3.14.3 / Windows  
**Tiempo total de ejecución:** ⚡ **1.16 segundos**

---

## 📋 Listado de Pruebas Ejecutadas (40 tests)

### E2E — tests/e2e/ (9 tests)

#### `test_api_auth.py` (2 tests)
| Test | Descripción |
|---|---|
| `test_login_success` | Login con credenciales válidas vía HTTP → token retornado |
| `test_login_failure` | Login con contraseña incorrecta → error 401 |

#### `test_api_customers.py` (7 tests)
| Test | Descripción |
|---|---|
| `test_get_accounts` | Consultar lista de cuentas del cliente |
| `test_get_wallet` | Consultar billetera del cliente |
| `test_get_summary` | Resumen financiero (cuentas + wallet + total) |
| `test_get_movements` | Historial de movimientos |
| `test_transfer_success` | Transferencia exitosa entre cuentas |
| `test_transfer_insufficient_funds` | Transferencia rechazada por saldo insuficiente |
| `test_transfer_invalid` | Transferencia inválida (monta negativo / misma cuenta) |

---

### Unit — tests/unit/ (31 tests)

#### `test_authenticate_service.py` (3 tests)
| Test | Descripción |
|---|---|
| `test_valid_token` | Token JWT válido → retorna usuario autenticado |
| `test_invalid_token` | Token JWT inválido → lanza excepción |
| `test_expired_token` | Token JWT expirado → lanza excepción |

#### `test_login_service.py` (4 tests)
| Test | Descripción |
|---|---|
| `test_login_success` | Login correcto → retorna token y datos de usuario |
| `test_login_invalid_password_raises_exception` | Contraseña incorrecta → `InvalidCredentials` |
| `test_login_user_not_found_raises_exception` | Usuario no existe → `InvalidCredentials` |
| `test_login_notifier_exception_handled_gracefully` | Falla en notificador → login sigue funcionando |

#### `test_info_services.py` (4 tests)
| Test | Descripción |
|---|---|
| `test_get_accounts` | Devuelve cuentas del cliente / lista vacía si no existe |
| `test_get_wallet` | Devuelve billetera / `None` si no existe |
| `test_get_movements` | Lista movimientos con y sin filtros |
| `test_get_summary` | Resumen con total calculado / `None` si no hay productos |

#### `test_transfer_service.py` (5 tests)
| Test | Descripción |
|---|---|
| `test_transfer_success` | Transferencia ok → saldos actualizados y movimiento registrado |
| `test_transfer_insufficient_funds` | Saldo insuficiente → `InsufficientFunds` |
| `test_transfer_same_account` | Misma cuenta origen/destino → `ValueError` |
| `test_transfer_from_not_found` | Cuenta origen no existe → `ValueError` |
| `test_transfer_to_not_found` | Cuenta destino no existe → `ValueError` |

#### `test_pse_services.py` (15 tests)

**Crear Pago (3 tests)**
| Test | Descripción |
|---|---|
| `test_create_payment_success` | Crea transacción PSE en estado PENDING |
| `test_create_payment_insufficient_funds` | Saldo insuficiente → `ValueError` |
| `test_create_payment_account_not_found` | Cuenta no encontrada → `ValueError` |

**Consultar Pago (2 tests)**
| Test | Descripción |
|---|---|
| `test_get_payment_success` | Recupera transacción PSE por ID |
| `test_get_payment_not_found` | ID inválido → `ValueError` |

**Pasarela PSE (5 tests)**
| Test | Descripción |
|---|---|
| `test_gateway_transaction_not_found` | Transacción no existe → `ValueError` |
| `test_gateway_rejected_by_simulation` | Simulación rechazada (random=0.99) → `REJECTED` + url failure |
| `test_gateway_expired_transaction` | Transacción expirada → `EXPIRED` + url failure |
| `test_gateway_account_not_found_on_process` | Cuenta inválida en procesamiento → `REJECTED` |
| `test_gateway_insufficient_funds_on_process` | Saldo insuficiente en procesamiento → `REJECTED` |
| `test_gateway_success` | Aprobación simulada (random=0.1) → `APPROVED` + saldo descontado |

**Callback PSE (4 tests)**
| Test | Descripción |
|---|---|
| `test_callback_success` | Callback SUCCESS → saldo acreditado + movimiento registrado |
| `test_callback_failure_does_not_increment_balance` | Callback DECLINED → saldo sin cambios |
| `test_callback_not_found` | Transacción no existe → `ValueError` |
| `test_callback_success_account_not_found` | Cuenta eliminada antes del callback → `ValueError` |

---

## 📊 Cobertura por Módulo

```
---------- coverage: platform win32, python 3.14.3-final-0 -----------
Name                                                           Stmts   Miss  Cover
--------------------------------------------------------------------------------------------
application\auth\ports\login_notifier.py                           2      0   100%
application\auth\ports\password_hasher.py                          2      0   100%
application\auth\ports\token_service.py                            2      0   100%
application\auth\ports\user_repository.py                          3      0   100%
application\auth\services\authenticate_service.py                 14      0   100%
application\auth\services\login_service.py                        26      0   100%
application\customers\ports\outbound\accounts_repository.py        2      0   100%
application\customers\ports\outbound\movements_repository.py       2      0   100%
application\customers\ports\outbound\wallets_repository.py         2      0   100%
application\customers\services\get_accounts_service.py             5      0   100%
application\customers\services\get_movements_service.py            6      0   100%
application\customers\services\get_summary_service.py             12      0   100%
application\customers\services\get_wallet_service.py               5      0   100%
application\customers\services\transfer_service.py                25      0   100%
application\pse\ports\outbound\account_repository.py               2      0   100%
application\pse\ports\outbound\movement_repository.py              4      0   100%
application\pse\ports\outbound\pse_transaction_repository.py       2      0   100%
application\pse\ports\outbound\unit_of_work.py                     4      0   100%
application\pse\services\create_payment_service.py                17      0   100%
application\pse\services\get_payment_service.py                    9      0   100%
application\pse\services\process_callback_service.py              25      0   100%
application\pse\services\process_gateway_service.py               39      0   100%
domain\auth\exceptions.py                                          4      0   100%
domain\auth\user.py                                                3      0   100%
domain\banking\exceptions.py                                       5      0   100%
domain\pse\exceptions.py                                           0      0   100%
(+ todos los __init__.py: 100%)
--------------------------------------------------------------------------------------------
TOTAL                                                            222      0   100%

======================== 40 passed, 1 warning in 1.16s ========================
```

---

## 🏆 Resumen

| Métrica | Valor |
|---|---|
| Tests totales | **40** |
| Tests E2E | 9 |
| Tests Unitarios | 31 |
| Líneas totales cubiertas | **222 / 222** |
| Líneas no cubiertas | **0** |
| Cobertura total | **100%** |
| Tiempo de ejecución | **1.16 segundos** |
| Requiere Base de Datos | ❌ No (100% mocks en RAM) |
