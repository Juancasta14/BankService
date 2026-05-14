# BITACORA.md -- Registro de implementación de BankService

- Pasos ejecutados: 0 de 15.
- Paso en curso: CAM-01 (Pendiente).
- Última actualización: 2026-05-14
- Rama de trabajo: main.

(Plan detallado en `plan/PLAN_ATOMICO.md`)

## Checklist de Pasos (Pendientes)
- [ ] CAM-01 - Preparar entorno virtual y estructura de carpetas
- [ ] CAM-02 - Crear entidades de negocio (`User`, `Account`, `Wallet`, `Movement`)
- [ ] CAM-03 - Crear excepciones financieras (`InsufficientFunds`, `InvalidAmount`)
- [ ] CAM-04 - Definir Puertos (Protocolos de Repositorios, UoW, Security)
- [ ] CAM-05 - Implementar casos de uso de Autenticación (`LoginService`)
- [ ] CAM-06 - Implementar consultas financieras (Saldos y Movimientos)
- [ ] CAM-07 - Implementar servicio de Transferencias con reglas estrictas
- [ ] CAM-08 - Implementar simulador y flujos de webhooks para PSE
- [ ] CAM-09 - Implementar modo memoria (`MockRepository`, `MockUoW`)
- [ ] CAM-10 - Implementar repositorios de SQLAlchemy y PostgreSQL
- [ ] CAM-11 - Desarrollar utilidades de seguridad (PyJWT, Passlib)
- [ ] CAM-12 - Exponer adaptadores de entrada HTTP (Routers de FastAPI)
- [ ] CAM-13 - Desarrollar aplicación cliente interactiva usando Flask
- [ ] CAM-14 - Configurar Docker (creación de Dockerfiles y docker-compose.yml)
- [ ] CAM-15 - Verificar métricas y lanzar CI (100% Cobertura)

---

## Registro de Pasos Ejecutados

<!-- Plantilla a copiar y rellenar cada vez que se finalice un paso -->
### Paso {N} - {Título corto del paso}
- **Fecha:** YYYY-MM-DD HH:MM
- **Archivos modificados:** `ruta/al/archivo1.py`, `ruta/al/archivo2.py`
- **Validación ejecutada:** `{comando de pytest o verificación estática}`
- **Resultado:** OK
- **Commit:** `hash` o `pendiente`
- **Observación técnica breve:** {Resumen de lo que se implementó en este paso}

---

## Registro de Decisiones Arquitectónicas (DEC)

<!-- Plantilla para registrar decisiones técnicas importantes que se tomen sobre la marcha -->
### DEC-XX (Paso X) - {Título de la decisión}
- **Decisión:** {Qué se decidió implementar de cierta manera}
- **Justificación:** {Por qué se tomó esa decisión (apoyándose en los .md de contexto)}
- **Impacto:** {Qué efecto tiene esta decisión en pasos futuros}

---

## Registro de Bloqueos (BLOQ)

<!-- Plantilla para documentar errores graves, callejones sin salida o fugas en la arquitectura -->
### BLOQ-XX (Paso X) - {Título del bloqueo}
- **Síntoma:** {Qué está fallando exactamente}
- **Causa probable:** {Por qué creemos que falla}
- **Solución aplicada:** {Qué se hizo para salir del bloqueo}
- **Evidencia:** {Comando o test que demuestra que ya está resuelto}
