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

---

## Diagramas C4

### C4 — Nivel 1: Contexto del Sistema

> Visión de alto nivel: actores externos y el sistema completo.

```mermaid
graph TD
    classDef person fill:#08427b,color:#fff,stroke:#052e56
    classDef system fill:#1168bd,color:#fff,stroke:#0b4884
    classDef external fill:#999,color:#fff,stroke:#666

    User(["👤 Usuario / Cliente"]):::person
    PSE(["🏦 Pasarela PSE"]):::external
    Lambda(["⚡ AWS Lambda"]):::external

    BankSystem["🏛️ BankService - Sistema Bancario Hexagonal"]:::system

    User -->|"Consultar cuentas, transferir, pagar con PSE"| BankSystem
    BankSystem -->|"Redirige al usuario a pasarela real"| PSE
    PSE -->|"Webhook callback resultado del pago"| BankSystem
    BankSystem -->|"Notificar intento de login"| Lambda
```

---

### C4 — Nivel 2: Contenedores

> Qué aplicaciones / servicios componen el sistema.

```mermaid
graph TD
    classDef person fill:#08427b,color:#fff,stroke:#052e56
    classDef container fill:#1168bd,color:#fff,stroke:#0b4884
    classDef db fill:#16a085,color:#fff,stroke:#0e6655
    classDef external fill:#999,color:#fff,stroke:#666

    User(["👤 Usuario"]):::person
    PSE(["🏦 Pasarela PSE"]):::external
    Lambda(["⚡ AWS Lambda - Login Notifier"]):::external

    Flask["🖥️ Flask App - Puerto 80"]:::container
    FastAPI["⚙️ FastAPI App - Puerto 8000"]:::container
    DB[("🗄️ PostgreSQL - Supabase")]:::db

    User -->|"HTTP navegador"| Flask
    Flask -->|"REST/JSON con JWT"| FastAPI
    User --->|"Redirección PSE"| FastAPI
    PSE -->|"POST /callback"| FastAPI
    FastAPI -->|"SQL ORM"| DB
    FastAPI -->|"POST eventos de login"| Lambda
```

---

### C4 — Nivel 3: Componentes (FastAPI App)

> Detalle interno del contenedor `fastapi_app` y sus componentes reales.

```mermaid
graph TD
    classDef inbound fill:#2196F3,color:#fff,stroke:#1565C0
    classDef app fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef domain fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef outbound fill:#FF9800,color:#fff,stroke:#E65100
    classDef port fill:#607D8B,color:#fff,stroke:#37474F,stroke-dasharray: 5 5

    subgraph Inbound ["🔵 Adaptadores de Entrada (adapters/inbound/http/routes/)"]
        AuthR["auth_routes.py — POST /auth/login"]:::inbound
        CustR["customers.py — GET /customers"]:::inbound
        TransR["transfers.py — POST /transfer"]:::inbound
        PSEPay["pse_payments.py — POST /payments"]:::inbound
        PSEGw["pse_gateway.py — GET /pse-gateway"]:::inbound
        PSECb["pse_callback.py — POST /callback"]:::inbound
        PayQ["payments_query.py — GET /payments"]:::inbound
    end

    subgraph Application ["🟢 Capa de Aplicación (application/)"]
        LoginSvc["LoginService"]:::app
        AuthSvc["AuthenticateService"]:::app
        TransSvc["TransferService"]:::app
        GetAccSvc["GetAccountsService"]:::app
        GetMovSvc["GetMovementsService"]:::app
        GetWalSvc["GetWalletService"]:::app
        GetSumSvc["GetSummaryService"]:::app
        CreatePSE["CreatePSEPaymentService"]:::app
        GetPSE["GetPSEPaymentService"]:::app
        ProcGw["ProcessPSEGatewayService"]:::app
        ProcCb["ProcessPSECallbackService"]:::app
    end

    subgraph Ports ["⚙️ Puertos (Interfaces Abstractas)"]
        UserRepo["UserRepository (ABC)"]:::port
        AccRepo["AccountsRepository (Protocol)"]:::port
        MovRepo["MovementsRepository (Protocol)"]:::port
        WalRepo["WalletsRepository (Protocol)"]:::port
        PseRepo["PSETransactionRepository"]:::port
        UoW["UnitOfWork (ABC)"]:::port
        Hasher["PasswordHasher (ABC)"]:::port
        TokenSvc["TokenService (ABC)"]:::port
        Notifier["LoginNotifier (ABC)"]:::port
    end

    subgraph Domain ["🟣 Dominio (domain/)"]
        UserEnt["User (dataclass)"]:::domain
        ExcAuth["InvalidCredentials\nUserNotFound"]:::domain
        ExcBank["InsufficientFunds\nTransferError"]:::domain
        ExcPSE["PSEExceptions"]:::domain
    end

    subgraph Outbound ["🟠 Adaptadores de Salida (adapters/outbound/persistence/sqlalchemy/)"]
        UserRepSQL["UserRepositorySQLAlchemy"]:::outbound
        AccRepSQL["AccountsRepositorySQLAlchemy"]:::outbound
        MovRepSQL["MovementsRepositorySQLAlchemy"]:::outbound
        WalRepSQL["WalletsRepositorySQLAlchemy"]:::outbound
        PseRepSQL["PSETransactionRepositorySQLAlchemy"]:::outbound
        UoWSQL["UnitOfWorkSQLAlchemy"]:::outbound
    end

    AuthR --> LoginSvc & AuthSvc
    CustR --> GetAccSvc & GetMovSvc & GetWalSvc & GetSumSvc
    TransR --> TransSvc
    PSEPay --> CreatePSE
    PSEGw --> ProcGw
    PSECb --> ProcCb
    PayQ --> GetPSE

    LoginSvc --> UserRepo & Hasher & TokenSvc & Notifier
    AuthSvc --> TokenSvc & UserRepo
    TransSvc --> AccRepo & MovRepo & UoW
    GetAccSvc --> AccRepo
    GetMovSvc --> MovRepo
    GetWalSvc --> WalRepo
    GetSumSvc --> AccRepo & WalRepo
    CreatePSE --> PseRepo & AccRepo
    GetPSE --> PseRepo
    ProcGw --> PseRepo & AccRepo & UoW
    ProcCb --> PseRepo & AccRepo & UoW

    Application --> Domain

    UserRepSQL -.->|implementa| UserRepo
    AccRepSQL -.->|implementa| AccRepo
    MovRepSQL -.->|implementa| MovRepo
    WalRepSQL -.->|implementa| WalRepo
    PseRepSQL -.->|implementa| PseRepo
    UoWSQL -.->|implementa| UoW
```

---

## Vista Hexagonal (Ports & Adapters)

> Representación clásica del patrón Hexagonal, mostrando cómo el núcleo se protege del exterior mediante puertos.

```mermaid
graph LR
    classDef outer fill:#f5f5f5,stroke:#bbb,color:#333
    classDef port fill:#607D8B,color:#fff,stroke:#37474F,stroke-dasharray:5 5
    classDef core fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef domain fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef inAdapter fill:#2196F3,color:#fff,stroke:#1565C0
    classDef outAdapter fill:#FF9800,color:#fff,stroke:#E65100

    subgraph Externos_Izq ["Actores Primarios"]
        Browser["🌐 Flask / Browser"]:::outer
        PSEExt["🏦 PSE Gateway"]:::outer
    end

    subgraph InboundAdapters ["Adaptadores de Entrada"]
        AuthRoute["auth_routes.py"]:::inAdapter
        CustRoute["customers.py"]:::inAdapter
        TransRoute["transfers.py"]:::inAdapter
        PSEPayRoute["pse_payments.py"]:::inAdapter
        PSEGwRoute["pse_gateway.py"]:::inAdapter
        PSECbRoute["pse_callback.py"]:::inAdapter
        PayQRoute["payments_query.py"]:::inAdapter
    end

    subgraph HexCore ["NUCLEO HEXAGONAL"]
        subgraph InPorts ["Puertos de Entrada"]
            ILogin["LoginService"]:::port
            IAuth["AuthenticateService"]:::port
            ICustomer["CustomerServices"]:::port
            IPSE["PSE Services"]:::port
        end

        subgraph Domain ["Dominio (domain/)"]
            DomCore["User - Account - InsufficientFunds - InvalidCredentials"]:::domain
        end

        subgraph OutPorts ["Puertos de Salida"]
            PUserRepo["UserRepository"]:::port
            PAccRepo["AccountsRepository"]:::port
            PMovRepo["MovementsRepository"]:::port
            PWalRepo["WalletsRepository"]:::port
            PPseRepo["PSERepository"]:::port
            PUoW["UnitOfWork"]:::port
            PHasher["PasswordHasher"]:::port
            PToken["TokenService"]:::port
            PNotif["LoginNotifier"]:::port
        end
    end

    subgraph OutboundAdapters ["Adaptadores de Salida"]
        SQLRepos["SQLAlchemy Repositories"]:::outAdapter
        JWTUtils["JWT and Hashing"]:::outAdapter
        HTTPNotif["HTTP Notifier - AWS Lambda"]:::outAdapter
    end

    subgraph Externos_Der ["Actores Secundarios"]
        PG[("🗄️ PostgreSQL - Supabase")]:::outer
        Lambda["⚡ AWS Lambda Login Events"]:::outer
    end

    Browser -->|"HTTP REST"| AuthRoute & CustRoute & TransRoute
    PSEExt -->|"Webhook POST"| PSECbRoute

    AuthRoute --> ILogin & IAuth
    CustRoute & TransRoute --> ICustomer
    PSEPayRoute & PSEGwRoute & PSECbRoute & PayQRoute --> IPSE

    ILogin & IAuth & ICustomer & IPSE --> DomCore

    ILogin --> PUserRepo & PHasher & PToken & PNotif
    IAuth --> PToken & PUserRepo
    ICustomer --> PAccRepo & PMovRepo & PWalRepo & PUoW
    IPSE --> PPseRepo & PAccRepo & PUoW

    SQLRepos -.->|implementa| PUserRepo & PAccRepo & PMovRepo & PWalRepo & PPseRepo & PUoW
    JWTUtils -.->|implementa| PHasher & PToken
    HTTPNotif -.->|implementa| PNotif

    SQLRepos -->|SQL ORM| PG
    HTTPNotif -->|POST| Lambda
```
