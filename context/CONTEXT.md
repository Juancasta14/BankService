# CONTEXT.md -- BankService: API Bancaria con Arquitectura Hexagonal

## 1. Propósito
Construir una API bancaria robusta aplicando Arquitectura Hexagonal (Ports & Adapters) y Domain-Driven Design (DDD) usando Python y FastAPI. El sistema debe soportar un "modo memoria" para pruebas ultrarrápidas y un "modo real" con bases de datos PostgreSQL. Además, se incluye un frontend en Flask para consumir dicha API.

## 2. Problema de negocio
Las aplicaciones bancarias tradicionales o monolíticas suelen sufrir un alto acoplamiento entre la lógica de negocio y la infraestructura (bases de datos, frameworks web, etc.), lo que dificulta las pruebas aisladas y el mantenimiento. Se requiere un sistema desacoplado que permita simular o reemplazar la base de datos sin afectar las reglas de negocio, garantizando transacciones seguras y soportando integraciones complejas (ej. pagos con la pasarela PSE).

## 3. Usuario principal
- **Usuarios finales (Clientes):** Personas que desean consultar sus saldos, visualizar su resumen financiero, realizar transferencias internas y ejecutar pagos a través de PSE.
- **Sistemas externos:** Pasarelas de pago y proveedores (ej. callbacks de simulación de PSE).
- **Desarrolladores:** Equipo técnico que requiere ejecutar y probar la lógica de negocio de manera completamente aislada (en memoria) sin depender de infraestructura externa.

## 4. Métricas de éxito
- Lograr y mantener una cobertura de pruebas del 100% sobre los casos de uso y el dominio.
- Lograr la ejecución completa de la suite de pruebas unitarias en menos de 2 segundos gracias al modo memoria.
- Aislamiento arquitectónico absoluto: cero (0) dependencias de bases de datos, ORMs (SQLAlchemy) o frameworks web (FastAPI) dentro de las capas `domain` y `application`.
- Despliegue reproducible y consistente en modo real usando Docker Compose.

## 5. Alcance incluido
- **Gestión de Cuentas y Resumen Financiero:** Consulta de múltiples cuentas, billeteras y un resumen consolidado por cliente.
- **Transferencias:** Transferencias internas de fondos validando el saldo disponible y aplicando reglas de negocio.
- **Pagos PSE:** Creación de intenciones de pago, simulación de la pasarela PSE y procesamiento asíncrono vía webhooks (callback).
- **Autenticación y Seguridad:** Login con usuario y contraseña emitiendo tokens JWT para rutas protegidas.
- **Arquitectura Hexagonal Estricta:** Separación rigurosa en capas funcionales (`domain`), de orquestación (`application` con puertos) y de adaptadores (`adapters` inbound/outbound).
- **Modo Memoria / Mocking:** Implementación de repositorios falsos (MockRepository) y Unit of Work en memoria para pruebas sin latencia de I/O.
- **Despliegue y Persistencia:** Uso de contenedores Docker y motor PostgreSQL mediante SQLAlchemy.
- **Frontend Interactivo:** Una aplicación web en Flask independiente que actúa como cliente consumiendo la API de FastAPI.

## 6. Alcance excluido
- [FUERA] Creación, registro u onboarding de nuevos clientes desde la interfaz pública.
- [FUERA] Integración real con el switch de ACH/PSE de Colombia (solamente se provee un simulador local).
- [FUERA] Gestión de tarjetas de crédito, préstamos o productos de inversión complejos.
- [FUERA] Pasarelas de pago internacionales basadas en tarjeta de crédito (Stripe, PayPal, etc.).
- [FUERA] Panel de administración (Backoffice) para gestión de usuarios u operaciones bancarias por parte de empleados.
- [FUERA] Despliegue automatizado en la nube o pipelines CI/CD de producción (solo se incluyen las pruebas automatizadas en CI).

## 7. Riesgos del alcance
- **Riesgo:** Acoplamiento accidental de dependencias de infraestructura (FastAPI, SQLAlchemy) en el dominio.
  **Mitigación:** Respetar estrictamente la regla de dependencia hacia adentro de la Arquitectura Hexagonal y validar mediante pruebas estáticas y revisiones de código.
- **Riesgo:** Inconsistencia de datos financieros debido a transferencias concurrentes o interrupciones en el flujo.
  **Mitigación:** Uso riguroso del patrón Unit of Work (UoW) y transacciones atómicas de la base de datos en los adaptadores persistentes.
- **Riesgo:** Fallos en la integración con el flujo asíncrono de PSE.
  **Mitigación:** Implementación estructurada de Callbacks (Webhooks) y creación de un endpoint de simulación interno para correr pruebas E2E deterministas.
