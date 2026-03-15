# Diagrama de Dependencias - Banco Monolítico

A continuación se presenta el diagrama de dependencias del proyecto, separando la interfaz de usuario en Flask y la lógica de negocio y acceso a datos en FastAPI.

```mermaid
graph TD
    classDef frontend fill:#dcebff,stroke:#4c8dff,stroke-width:2px;
    classDef backend fill:#e8f4f8,stroke:#17a2b8,stroke-width:2px;
    classDef external fill:#fcf3cf,stroke:#f1c40f,stroke-width:2px;
    classDef violation fill:#f8d7da,stroke:#dc3545,stroke-width:2px,color:#721c24,stroke-dasharray: 5 5;

    subgraph Frontend ["Frontend (Flask)"]
        flask[Flask App<br><code>app.py</code>]:::frontend
    end

    subgraph Backend ["Backend (FastAPI)"]
        main[FastAPI Endpoints<br><code>main.py</code>]:::backend
        models[DB Models & Pydantic<br><code>models.py</code>]:::backend
        security[Auth / JWT<br><code>security.py</code>]:::backend
        db_conn[Configuración DB<br><code>database.py</code>]:::backend
        init_db[Inicialización DB<br><code>init_db.py</code>]:::backend
    end

    subgraph Infrastructura ["Infrastructura"]
        pg[(PostgreSQL Database)]:::external
    end

    %% Relaciones Principales
    flask -- "HTTP Requests (REST)" --> main

    %% Dependencias Internas FastAPI
    main -- "Verificación / Creación JWT" --> security
    main -- "Modelos y Consultas" --> models
    main -- "Dependencia (get_db)" --> db_conn

    %% Dependencias init_db
    init_db -- "Creación Tablas e Instancias" --> models
    init_db -- "Conexión a BD" --> db_conn
    init_db -- "Contraseñas Seguras" --> security

    %% DB y ORM
    db_conn -- "Conexión psycopg2" --> pg
    models -. "SQLAlchemy ORM" .-> db_conn

    %% ----------------------------------------------------
    %% Anotaciones de Violaciones de Arquitectura Hexagonal
    %% ----------------------------------------------------
    note right of main : ❌ Violación Hexagonal:\nmain.py mezcla enrutamiento HTTP (Adaptador) con\nlógica de negocio (Casos de Uso).
    note bottom of models : ❌ Violación Hexagonal:\nmodels.py mezcla el Dominio (Pydantic)\ncon la Infraestructura ORM (SQLAlchemy).
    note left of main : ❌ Violación de Inversión de Dependencias:\nmain.py depende directamente de infraestructura\n(db_conn y queries ORM) en vez de abstraerse con Puertos.
```

## Descripción de Componentes

### Frontend
- **`app.py`**: Interfaz de usuario renderizada en el lado del servidor con Jinja2 (vistas HTML/CSS incrustadas) que interactúa con el API utilizando peticiones internas (`requests`).

### Backend (FastAPI)
- **`main.py`**: Punto de entrada de la API. Define los endpoints, la autenticación (OAuth2) e inyección de dependencias.
- **`models.py`**: Contiene los modelos SQLAlchemy para interactuar con la base de datos (tablas `accounts`, `users`, `movements`, etc.), esquemas de validación con Pydantic y métodos auxiliares de consultas (helpers).
- **`security.py`**: Responsable de la creación y verificación de contraseñas usando `passlib`, así como la generación y decodificación de tokens JWT.
- **`database.py`**: Establece la conexión con la base de datos PostgreSQL utilizando SQLAlchemy y gestiona la inyección de sesiones DB (`SessionLocal`).
- **`init_db.py`**: Script pre-despliegue usado para generar las tablas y poblar la base de datos con usuarios y cuentas iniciales de prueba.

### Infraestructura
- **PostgreSQL**: Base de datos gestionada, referenciada en el host `db` dentro del entorno dockerizado.
