# GLOSSARY.md -- BankService: API Bancaria

## User
Entidad que representa a un cliente registrado y autenticado en el sistema.

## Account
Cuenta bancaria asociada a un `User`. Contiene un balance numérico que debe protegerse de quedar en negativo. No confundir con Billetera (Wallet).

## Wallet
Billetera digital asociada al usuario. Es un producto financiero independiente a la cuenta principal, utilizado para separar y resguardar fondos.

## Movement
Registro inmutable (débito o crédito) que justifica un cambio en el balance de una cuenta.

## Transfer
Operación financiera atómica que mueve fondos de una `Account` origen a una `Account` destino validando las invariantes de dominio.

## PSE (Pagos Seguros en Línea)
Sistema/Pasarela externa de pagos. En este proyecto se simula su comportamiento asíncrono (Webhooks y Callbacks).

## UnitOfWork (UoW)
Patrón de diseño utilizado en infraestructura que agrupa múltiples operaciones de base de datos en una sola transacción atómica (asegurando Commit o Rollback global).

## MockRepository / MockUow
Implementaciones falsas en memoria de un puerto de la capa de aplicación, diseñadas exclusivamente para ejecutar pruebas unitarias a gran velocidad sin interactuar con la red ni con bases de datos reales.
