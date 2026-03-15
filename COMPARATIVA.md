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

---

### Decisiones de Diseño Core: ¿POR QUÉ se diseñó así? (Frente al Monolito)

En el proyecto monolítico original (`Banco_monolitico`), las decisiones solían tomarse alrededor del framework principal (FastAPI y SQLAlchemy). Aquí explicamos **por qué** la Arquitectura Hexagonal introduce y moldea sus componentes de otra manera.

#### 1. Entidades (Domain Entities)
*En el monolito, las "entidades" eran los mismos modelos de SQLAlchemy (ej. `class User(Base)`), combinando reglas de negocio con detalles de cómo guardar en base de datos. Si se reestructuraba la tabla, se rompía la regla de negocio.*

**¿POR QUÉ el nuevo diseño?**
- **Para proteger la ignorancia de persistencia:** Nuestras nuevas Entidades de Dominio (`User`, `Account`, etc.) se diseñaron como clases puras (`@dataclass` de Python). La decisión de remover la herencia de `Base` (SQLAlchemy) en el dominio fue **obligada** para garantizar que un cambio de base de datos (Ej: migrar a MongoDB o PostgreSQL) jamás te obligue a reescribir la lógica de cómo se crea una cuenta o se valida un saldo insuficiente. 
- **Para encapsular invariantes:** Al no depender de Pydantic ni FastAPI en el dominio, pudimos crear métodos limpios (`account.withdraw(amount)`) que contienen el 100% de la regla de la transferencia (por qué y cuándo es válida), impidiendo que otra capa modifique el saldo directamente como ocurría en el `main.py` monolítico.

#### 2. Objetos de Valor (Value Objects)
*En el monolito, conceptos dependientes (como `Currency`, o un `Amount` con su divisa) simplemente flotaban como `string` o `float` por todo el enrutador. Un error tipográfico (`"COP "` vs `"COP"`) o un float negativo provocaban un IF gigante en el controller.*

**¿POR QUÉ el nuevo diseño?**
- **Para eliminar la Validación Condicional Dispersa (Defensive Programming):** Los objetos de valor (conceptos inmutables como `Amount = -100` que jamás deberían existir sin validarse solos) se modelan en el dominio. Se diseñan así para que al construir, por ejemplo, un "Dinero" o "Divisa", se valide y congele (`frozen`) automáticamente.
- **Por qué son inmutables:** Decidimos hacerlos inmutables para no rastrear su estado de forma incierta (a un billete de $500 no le puedes cambiar el número a $1000 físicamente), si necesitas otro valor, se instancia un objeto nuevo. Esto previene bugs de referencia cruzada.

#### 3. Puertos (Inbound y Outbound Ports)
*En el monolito no existían. El caso de uso HTTP directamente importaba el archivo `models.py` y requería la sesión de SQLAlchemy obligatoriamente para existir.*

**¿POR QUÉ el nuevo diseño de Puertos?**
- **Inversión de Control (Puertos Outbound):** Diseñamos `class UserRepository(ABC):` puramente con firmas abstractas **porque** necesitábamos que la capa de Casos de Uso (Application) nunca conociera SQL o si existe un ORM siquiera. Al forzar que el caso de uso dependa de un contrato (`Interface`) y no de una implementación (`models.py`), creamos la posiblidad de que las **pruebas pasaran de requerir una Base de Datos física (lento) a solo requerir un diccionario en memoria (ultra-rápido en 1ms)**.
- **Mecanismos de Intercambio (Puertos Inbound):** Los casos de uso (ej. `TransferService`) se crearon encapsulando el QUÉ hace el proyecto en vez de usar directamente los *routers* de Pydantic. Tomamos esta decisión **para habilitar múltiples interfaces de usuario**. En el monolito, si querías activar una transferencia por Terminal CLI o Telegram, no podías, porque el código dependía de recibir peticiones web (HTTP Request). Al introducir casos de uso como puertos Inbound, la operación de transferir podría ser disparada tanto vía API Web como desde una tarea `Cron`/Script sin cambiar la regla de negocio.
