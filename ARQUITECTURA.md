# Arquitectura del Sistema: Banco Hexagonal

El proyecto implementa un sistema bancario utilizando un modelo cliente-servidor, donde el frontend es renderizado en el lado de servidor (`flask_app`) y el backend principal se encarga de la lógica de negocio mediante una **Arquitectura Hexagonal** en `fastapi_app`.

## Diagrama de Arquitectura
```mermaid
graph TD
    %% Estilos Globales
    classDef client fill:#f9f9fa,stroke:#333,stroke-width:2px,color:#333;
    classDef frontend fill:#355adf,stroke:#16396b,stroke-width:2px,color:#fff;
    classDef fastapicore fill:#4c8dff,stroke:#355adf,stroke-width:2px,color:#fff;
    classDef hexagonal fill:#e0f0ff,stroke:#4c8dff,stroke-width:2px,color:#333,stroke-dasharray: 5 5;
    classDef database fill:#16a085,stroke:#0e5139,stroke-width:2px,color:#fff;
    classDef external fill:#d0342c,stroke:#900000,stroke-width:2px,color:#fff;

    %% Actores Externos
    User((Usuario/Navegador)):::client
    ExternalPSE[Pasarela de Pagos PSE / Simulación]:::external

    %% Sistema Frontend
    subgraph Frontend [UI Monolítica]
        Flask[Aplicación Web Node - Flask]:::frontend
    end

    %% Sistema Backend
    subgraph Backend [Backend Service - FastAPI]
        %% inbound adapters
        subgraph Inbound [Adaptadores de Entrada HTTP]
            AuthRoutes[Rutas de Auth]:::fastapicore
            CustomerRoutes[Rutas de Cuentas/Transferencias]:::fastapicore
            PSERoutes[Rutas de Pagos PSE]:::fastapicore
        end
        
        %% Core application logic
        subgraph Core [Núcleo Hexagonal]
            direction TB
            subgraph Application [Capa de Casos de Uso]
                AuthService[Auth Services]
                CustomerService[Account/Movements Services]
                PSEService[PSE/Gateway Services]
                PrimaryPorts((Puertos de Entrada/Salida))
            end
            
            subgraph Domain [Capa de Dominio]
                Entities([Entidades: User, Account, Movement, Transaction])
                Exceptions([Excepciones del Dominio])
            end
        end

        %% outbound adapters
        subgraph Outbound [Adaptadores de Salida]
            SQLRep[SQLAlchemy Repositories]:::fastapicore
            UoW[Patrón Unit of Work]:::fastapicore
            SecurityUtils[JWT & Hashing AuthUtils]:::fastapicore
        end
    end

    %% Persistencia
    DB[(Base de Datos PostgreSQL)]:::database

    %% Relaciones
    User -->|Navega e Interactúa| Flask
    Flask -->|Peticiones HTTP REST / JSON| Inbound
    User -.->|Redirección al Pagar| PSERoutes
    ExternalPSE -.->|Webhooks Asíncronos| PSERoutes
    
    Inbound -->|Llaman Casos de Uso| Application
    Application -->|Contienen| Domain
    Application -->|Definen Interfaces| PrimaryPorts
    
    Outbound -.->|Implementan Interfaces| PrimaryPorts
    AuthService -.->|Usa| SecurityUtils
    CustomerService -.->|Usa| UoW
    PSEService -.->|Usa| UoW
    
    UoW -->|Gestionan Entidades BD| SQLRep
    SQLRep -->|Consultas ORM| DB
```

## Resumen de la Arquitectura

1. **Usuario / Navegador (`flask_app`)**:
   - Actúa como la capa de interfaz visual (Views y Templates).
   - No tiene conexión directa con la base de datos.
   - Envía peticiones HTTP al backend en FastAPI enviando el estado de sesión (JWT Headers).
   
2. **Backend Hexagonal (`fastapi_app`)**:
   - Está dividido en capas siguiendo el principio de inversión de dependencias:
     - **Capa de Dominio (`domain/`)**: Representa la "verdad empresarial", contiene entidades de datos (User, Account) que no dependen de la web u ORM.
     - **Capa de Aplicación (`application/`)**: Contiene los "Casos de Uso" o flujos de usuario (autenticarse, listar cuentas, hacer pagos PSE) y los Puertos (Interfaces).
     - **Adaptadores de Entrada (`adapters/inbound/`)**: Entregables de red, como el Router en FastAPI que recibe un JSON y lo pasa al caso de uso correspondiente.
     - **Adaptadores de Salida (`adapters/outbound/`)**: Servicios de infraestructura. Contiene la conexión real a Postgres con el patrón **Repository** y **UnitOfWork**, manteniendo acoplada a SQLAlchemy de forma aislada a las capas internas.

3. **Base de Datos (`app/docker-compose`)**:
   - Base de datos relacional (PostgreSQL) gestionada de forma externa al código fuente y enrutada por Docker.
