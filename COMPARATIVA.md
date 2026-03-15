# Comparativa: Proyecto Monolítico vs Arquitectura Hexagonal

A continuación se presenta la tabla comparativa entre la implementación monolítica original (`Banco_monolitico`) y la nueva implementación basada en Arquitectura Hexagonal (`BankService`).

| Métrica | Proyecto Monolítico (`Banco_monolitico`) | Arquitectura Hexagonal (`BankService`) |
| --- | --- | --- |
| **Líneas de Código (LOC) por Módulo** | - `main.py` (Routing/Lógica/Interfaces): **444 LOC**<br>- `models.py` (Base de Datos): **245 LOC**<br>- `security.py` (Utilidades Auth): **40 LOC**<br>- `database.py` (Conexión BD): **26 LOC** | - `domain/` (Capa de Dominio): **31 LOC**<br>- `application/` (Casos de Uso/Puertos): **516 LOC**<br>- `adapters/` (Controladores/Repositorios): **1115 LOC**<br>- `main.py` (Configuración e Inyección): **22 LOC** |
| **Tiempo de Ejecución de Pruebas** | N/A / Muy lento debido a un alto acoplamiento con la Base de datos (requiere SQLite físico) y sin posibilidad fácil de aislar la capa lógica | **~1210 milisegundos (1.21s)** para 38 pruebas (Totalmente aisladas gracias a los mocks de puertos y repositorios, sin tocar la base de datos) |
| **Número de Dependencias por Capa** | **~1 capa principal interactuando como un todo:**<br>- `Routers/Services` dependen de FastAPI puro, de Pydantic, de SQLAlchemy directamente y de Seguridad al mismo tiempo. | **Niveles desacoplados claramente:**<br>1. **Domain:** 0 Dependencias externas<br>2. **Application:** Depende exclusivamente del Dominio y Puertos.<br>3. **Adapters:** Dependen de Application, Entidades y Librerías Externas (FastAPI/SQLalchemy).<br>4. **Config/Infra:** Interrelaciona los adaptadores con los puertos. |

### Conclusiones Principales
1. **Separación de Responsabilidades:** Aunque el proyecto hexagonal incrementa la cantidad de código puro ("boilerplate" inicial del patrón Ports & Adapters en la capa *Adapters* y *Application*), el bloque principal centralizado del monolito (donde solo `main.py` hacía de controlador, servicio y gestionaba la base de datos) pasó de ser un archivo de más de 400 líneas a apenas 22 líneas de inyección de configuración en la nueva aproximación.
2. **Testabilidad:** Gracias a la creación de abstracciones (Puertos e Inyección de Dependencias), las pruebas de la lógica de negocio ahora se ejecutan de manera instantánea en cuestión de milisegundos, ya que podemos emplear `MockUnitOfWork` que actúa enteramente en memoria, reemplazando a la base de datos real.
3. **Desacoplamiento (Regla de dependencia):** En la nueva arquitectura, la lógica central de negocio ubicada en el *Domain* e incluso la *Application* no tienen rastros de FastAPI, SQLAlchemy u otras tecnologías de infraestructura. En el monolito, si se cambiaba el ORM, se colapsaba toda la aplicación.

---

### Explicación en Detalle de las Métricas

#### 1. Líneas de Código (LOC)
- **Monolito:** Tenía un diseño altamente acoplado. El archivo `main.py` contaba con más de **400 líneas**, ya que se encargaba de hacer el enrutamiento (Routing), la lógica de negocio y las consultas directas a la base de datos, todo mezclado.
- **Arquitectura Hexagonal:** El código está repartido de forma clara. La mayor carga de líneas se encuentra ahora en los adaptadores (`adapters/`), ya que agrupan los controladores y repositorios. Sin embargo, el archivo `main.py` (el punto de entrada) ha bajado a **solo 22 líneas**, las cuales se dedican exclusivamente a inyectar las dependencias (configuración inicial o wiring).

#### 2. Tiempo de Ejecución
- **Monolito:** Era complicado probar la capa lógica porque todo estaba atado fuertemente a SQLite (base de datos física). Las pruebas debían arrancar la BD real, haciéndolas lentas o difíciles de mantener puras sin efectos secundarios.
- **Arquitectura Hexagonal:** Las **38 Unit Tests corren en tan solo ~1.21 segundos**. Esto es posible porque, mediante los puertos (interfaces), se crearon implementaciones falsas ("Mocks") para los repositorios. Esto permite probar el 100% de la lógica de negocio (Application / Domain) en la memoria principal (RAM) sin tocar nunca un disco físico o base de datos real.

#### 3. Dependencias por Capa
- **Monolito:** Era básicamente un código "Spaghetti". En una misma función se validaba HTTP mediante FastAPI, transacciones con SQLAlchemy y reglas de negocio. Una dependencia directa entre todas las áreas.
- **Arquitectura Hexagonal:** Se han aislado las responsabilidades para mantener el núcleo intacto:
  - El **Dominio** (Reglas core de negocio) posee **0 dependencias externas** (Ni FastAPI ni SQLAlchemy).
  - La **Aplicación** (Casos de uso) depende netamente del Dominio.
  - Los **Adaptadores** son los únicos que tienen "permiso" para depender de librerías externas o frameworks como FastAPI o HTTP/Bases de Datos.
