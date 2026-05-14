# PLAN_ATOMICO.md -- Plan de implementación paso a paso (BankService)

## 1. Reglas del plan
- Un paso debe modificar o construir una sola unidad lógica.
- Cada paso debe referenciar restricciones (INV), casos de uso o un archivo de contexto (`DOMAIN.md`, `ARCHITECTURE.md`).
- Ningún paso debe romper las pruebas unitarias existentes (Modo Memoria).
- Cada paso debe poder revertirse fácilmente desde Git si algo falla.
- Las dependencias de infraestructura solo se implementan después de haber completado las capas de Dominio y Aplicación.
- **Actualización Obligatoria:** Al finalizar y validar cada paso (o tomar una decisión técnica importante), es estrictamente obligatorio documentarlo en el archivo `plan/BITACORA.md` antes de autorizar el siguiente paso.

## 2. Cambios normalizados (Flujo de desarrollo)
| ID | Descripción | Capa primaria | Referencia |
|---|---|---|---|
| CAM-01 | Preparar entorno virtual (`context/TECH_CONSTRAINTS.md`) y estructura de carpetas (`context/ARCHITECTURE.md` Sec. 3) | Configuración | context/ARCHITECTURE.md, context/TECH_CONSTRAINTS.md |
| CAM-02 | Crear entidades de negocio (`User`, `Account`, `Wallet`, `Movement`) | Dominio | context/DOMAIN.md |
| CAM-03 | Crear excepciones financieras (`InsufficientFunds`, `InvalidAmount`) | Dominio | context/DOMAIN.md, INV-01, INV-02 |
| CAM-04 | Definir Puertos (Protocolos de Repositorios, UoW, Security) | Aplicación | context/ARCHITECTURE.md |
| CAM-05 | Implementar casos de uso de Autenticación (`LoginService`) | Aplicación | context/DOMAIN.md |
| CAM-06 | Implementar consultas financieras (Saldos y Movimientos) | Aplicación | context/DOMAIN.md |
| CAM-07 | Implementar servicio de Transferencias con reglas estrictas | Aplicación | INV-01, INV-02, INV-03, INV-04 |
| CAM-08 | Implementar simulador y flujos de webhooks para PSE | Aplicación | context/DOMAIN.md |
| CAM-09 | Implementar modo memoria (`MockRepository`, `MockUoW`) | Infraestructura | context/TECH_CONSTRAINTS.md |
| CAM-10 | Implementar repositorios de SQLAlchemy y PostgreSQL | Infraestructura | context/TECH_CONSTRAINTS.md |
| CAM-11 | Desarrollar utilidades de seguridad (PyJWT, Passlib) | Infraestructura | context/ARCHITECTURE.md |
| CAM-12 | Exponer adaptadores de entrada HTTP (Routers de FastAPI) | Infraestructura | context/ARCHITECTURE.md |
| CAM-13 | Desarrollar aplicación cliente interactiva usando Flask | Presentación | context/TECH_CONSTRAINTS.md |
| CAM-14 | Configurar Docker (creación de Dockerfiles y docker-compose.yml) | Infraestructura | context/TECH_CONSTRAINTS.md |
| CAM-15 | Verificar métricas y lanzar CI (100% Cobertura) | Pruebas | README.md |

## 3. Plantilla por paso
Esta plantilla debe ser utilizada por la IA o el desarrollador antes de ejecutar código:

```text
PASO {N} - {Título corto}
Fase: {Configuración | Dominio | Aplicación | Infraestructura | Presentación | Pruebas}
Cambio normalizado: {CAM-XX}
Referencia: {INV-XX o archivo Markdown}
Archivos autorizados: {archivos que se permiten tocar}
Validación: {Comando de pruebas ej: pytest tests/unit/test_domain.py}
Criterio de aceptación: {Condición requerida para dar el paso por finalizado}
Autorización: pendiente
```
