# FastAPI to Mermaid Diagrams

This directory contains examples of generating Mermaid diagrams from FastAPI applications.

## Diagram Types

### 1. Architecture Diagram (from async structure and dependencies)
### 2. Deployment Diagram (from Docker/K8s configuration)
### 3. Sequence Diagram (from async endpoint handlers)
### 4. Activity Diagram (from async business logic)

## Example Application Structure

```
app/
├── main.py                    # FastAPI app entry point
├── config.py                  # Pydantic settings
├── dependencies.py            # Dependency injection
├── routers/
│   ├── __init__.py
│   ├── contacts.py           # Contact endpoints
│   └── auth.py               # Authentication endpoints
├── services/
│   ├── __init__.py
│   ├── contact_service.py    # Business logic
│   └── auth_service.py       # Auth logic
├── models/
│   ├── __init__.py
│   ├── contact.py            # Pydantic models
│   └── user.py               # User models
├── db/
│   ├── __init__.py
│   ├── database.py           # SQLAlchemy async setup
│   └── repositories/
│       ├── contact_repo.py   # Database operations
│       └── user_repo.py
└── core/
    ├── security.py           # JWT, password hashing
    └── cache.py              # Redis cache
```

## Generated Diagrams

### Architecture Diagram

**From**: Application structure, dependency injection, async patterns

```mermaid
graph TB
    subgraph "FastAPI Application"
        subgraph "API Layer"
            Main[⚙️ FastAPI App<br/>main.py<br/>Async ASGI]
            ContactRouter[🌐 Contact Router<br/>@router.get/post<br/>Async Endpoints]
            AuthRouter[🔐 Auth Router<br/>@router.post<br/>JWT Auth]
        end

        subgraph "Service Layer"
            ContactSvc[⚙️ Contact Service<br/>Async Business Logic<br/>Dependency Injection]
            AuthSvc[🔐 Auth Service<br/>JWT Generation<br/>Password Hashing]
        end

        subgraph "Repository Layer"
            ContactRepo[💾 Contact Repository<br/>SQLAlchemy Async<br/>CRUD Operations]
            UserRepo[💾 User Repository<br/>SQLAlchemy Async]
        end

        subgraph "Dependencies"
            DBDep[🔌 Database Dependency<br/>AsyncSession]
            CacheDep[⚡ Cache Dependency<br/>Redis Client]
            AuthDep[🔐 Auth Dependency<br/>OAuth2PasswordBearer]
        end

        subgraph "Core"
            Security[🔐 Security<br/>bcrypt, JWT]
            Cache[⚡ Redis Cache<br/>aioredis]
        end
    end

    subgraph "External Services"
        PostgreSQL[(💾 PostgreSQL<br/>AsyncPG Driver)]
        Redis[(⚡ Redis<br/>Async Client)]
    end

    Main --> ContactRouter
    Main --> AuthRouter

    ContactRouter --> ContactSvc
    AuthRouter --> AuthSvc

    ContactSvc --> ContactRepo
    AuthSvc --> UserRepo

    ContactSvc --> CacheDep
    ContactRouter --> AuthDep
    ContactRouter --> DBDep

    ContactRepo --> PostgreSQL
    UserRepo --> PostgreSQL
    CacheDep --> Redis
    Cache --> Redis

    Security -.provides.-> AuthSvc
    Security -.provides.-> AuthDep

    classDef api fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef service fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef repository fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef dependency fill:#FFD700,stroke:#333,stroke-width:2px,color:black
    classDef database fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue

    class Main,ContactRouter,AuthRouter api
    class ContactSvc,AuthSvc service
    class ContactRepo,UserRepo repository
    class DBDep,CacheDep,AuthDep,Security,Cache dependency
    class PostgreSQL,Redis database
```

### Deployment Diagram

**From**: Docker Compose, Kubernetes manifests, or cloud configuration

```mermaid
graph TB
    subgraph "Docker Compose Deployment"
        subgraph "Application Services"
            FastAPI1[⚙️ fastapi-app-1<br/>uvicorn --workers 4<br/>Port: 8000<br/>replicas: 3]
            FastAPI2[⚙️ fastapi-app-2<br/>uvicorn --workers 4<br/>Port: 8000]
            FastAPI3[⚙️ fastapi-app-3<br/>uvicorn --workers 4<br/>Port: 8000]
        end

        subgraph "Reverse Proxy"
            Nginx[🌐 nginx:alpine<br/>Port: 80<br/>Load Balancer]
        end

        subgraph "Data Services"
            Postgres[(💾 postgres:15<br/>Port: 5432<br/>volumes: pgdata<br/>env: POSTGRES_DB)]
            Redis[(⚡ redis:7-alpine<br/>Port: 6379<br/>maxmemory: 512mb)]
        end

        subgraph "Background Workers"
            Celery1[⚙️ celery-worker-1<br/>--concurrency 4<br/>-Q default]
            Celery2[⚙️ celery-worker-2<br/>--concurrency 4<br/>-Q high_priority]
        end

        subgraph "Message Broker"
            RabbitMQ[🐰 rabbitmq:3-management<br/>Port: 5672, 15672<br/>env: RABBITMQ_DEFAULT_VHOST]
        end

        subgraph "Monitoring"
            Prometheus[📊 prom/prometheus<br/>Port: 9090]
            Grafana[📈 grafana/grafana<br/>Port: 3000]
        end
    end

    Client[👤 Client] --> Nginx
    Nginx --> FastAPI1
    Nginx --> FastAPI2
    Nginx --> FastAPI3

    FastAPI1 --> Postgres
    FastAPI2 --> Postgres
    FastAPI3 --> Postgres

    FastAPI1 --> Redis
    FastAPI2 --> Redis
    FastAPI3 --> Redis

    FastAPI1 --> RabbitMQ
    FastAPI2 --> RabbitMQ
    FastAPI3 --> RabbitMQ

    RabbitMQ --> Celery1
    RabbitMQ --> Celery2

    Celery1 --> Postgres
    Celery2 --> Postgres

    FastAPI1 --> Prometheus
    FastAPI2 --> Prometheus
    FastAPI3 --> Prometheus
    Prometheus --> Grafana

    classDef client fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef frontend fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef backend fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef database fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef monitoring fill:#F0E68C,stroke:#333,stroke-width:2px,color:black

    class Client client
    class Nginx frontend
    class FastAPI1,FastAPI2,FastAPI3,Celery1,Celery2 backend
    class Postgres,Redis,RabbitMQ database
    class Prometheus,Grafana monitoring
```

### Sequence Diagram (Async Flow)

**From**: FastAPI async endpoint handlers

```python
# routers/contacts.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/contacts", response_model=ContactResponse)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    cache: Redis = Depends(get_cache)
):
    # Create contact with async operations
    service = ContactService(db, cache)
    new_contact = await service.create_contact(contact, current_user.id)
    return new_contact

# services/contact_service.py
class ContactService:
    def __init__(self, db: AsyncSession, cache: Redis):
        self.db = db
        self.cache = cache
        self.repo = ContactRepository(db)

    async def create_contact(self, contact_data: ContactCreate, user_id: int):
        # Check cache
        cached = await self.cache.get(f"user:{user_id}:contacts:count")

        # Create in database
        contact = await self.repo.create(contact_data, user_id)

        # Invalidate cache
        await self.cache.delete(f"user:{user_id}:contacts")

        # Publish event (background task)
        await self._publish_event("contact.created", contact.id)

        return contact
```

**Generated Sequence Diagram:**

```mermaid
sequenceDiagram
    participant Client as 👤 Client
    participant Router as 🌐 Contact Router
    participant Auth as 🔐 Auth Middleware
    participant Service as ⚙️ Contact Service
    participant Cache as ⚡ Redis Cache
    participant Repo as 💾 Contact Repository
    participant DB as 💾 PostgreSQL
    participant Queue as 📬 Message Queue

    Client->>+Router: POST /api/contacts<br/>{ContactCreate}
    Note over Router: @router.post<br/>async def create_contact()

    Router->>+Auth: await get_current_user(token)
    Auth->>Auth: Verify JWT Token
    Auth-->>-Router: User object

    Router->>+Service: await create_contact(data, user_id)
    Note over Service: Async Business Logic

    Service->>+Cache: await cache.get(key)
    Cache-->>-Service: None (cache miss)

    Service->>+Repo: await repo.create(contact)
    Repo->>+DB: async with session.begin():<br/>INSERT INTO contacts
    DB-->>-Repo: Contact created
    Repo-->>-Service: Contact object

    Service->>+Cache: await cache.delete(key)
    Cache-->>-Service: OK

    Service->>+Queue: await publish_event()<br/>(background task)
    Queue-->>-Service: Queued

    Service-->>-Router: Contact object
    Router-->>-Client: 201 Created<br/>{ContactResponse}

    Note over Queue: Async background<br/>processing continues

    classDef client fill:#FFE4B5,stroke:#333,stroke-width:2px,color:black
    classDef api fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef service fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef database fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
```

### Activity Diagram (Async Workflow)

**From**: Async business logic with error handling

```python
# services/contact_service.py
async def update_contact(self, contact_id: int, data: ContactUpdate, user_id: int):
    # Fetch existing contact
    existing = await self.repo.get_by_id(contact_id)

    if not existing:
        raise HTTPException(404, "Contact not found")

    # Check ownership
    if existing.user_id != user_id:
        raise HTTPException(403, "Not authorized")

    # Check email uniqueness if changed
    if data.email and data.email != existing.email:
        email_exists = await self.repo.exists_by_email(data.email, user_id)
        if email_exists:
            raise HTTPException(400, "Email already in use")

    # Update in database (transaction)
    async with self.db.begin():
        updated = await self.repo.update(contact_id, data)

        # Invalidate cache
        await self.cache.delete(f"contact:{contact_id}")

        # Create audit log
        await self.audit_repo.create_log(
            user_id=user_id,
            action="update_contact",
            contact_id=contact_id
        )

    # Publish event (async, non-blocking)
    asyncio.create_task(
        self.event_publisher.publish("contact.updated", updated.id)
    )

    return updated
```

**Generated Activity Diagram:**

```mermaid
flowchart TD
    Start([📥 Update Contact Request]) --> FetchContact[💾 await repo.get_by_id]
    FetchContact --> Exists{Contact Exists?}

    Exists -->|No| NotFound[❌ HTTPException 404<br/>Contact not found]
    NotFound --> End1([End])

    Exists -->|Yes| CheckOwner{Owner Match?}
    CheckOwner -->|No| Forbidden[❌ HTTPException 403<br/>Not authorized]
    Forbidden --> End2([End])

    CheckOwner -->|Yes| EmailChanged{Email Changed?}

    EmailChanged -->|No| BeginTx[🔄 Begin Transaction<br/>async with db.begin]

    EmailChanged -->|Yes| CheckEmail[🔍 await exists_by_email]
    CheckEmail --> EmailExists{Email In Use?}

    EmailExists -->|Yes| BadRequest[❌ HTTPException 400<br/>Email already in use]
    BadRequest --> End3([End])

    EmailExists -->|No| BeginTx

    BeginTx --> UpdateDB[💾 await repo.update]
    UpdateDB --> UpdateSuccess{Update Success?}

    UpdateSuccess -->|No| Rollback[🔄 Rollback Transaction]
    Rollback --> Error[❌ Database Error]
    Error --> End4([End])

    UpdateSuccess -->|Yes| InvalidateCache[⚡ await cache.delete]
    InvalidateCache --> CreateAudit[📝 await audit_repo.create_log]
    CreateAudit --> CommitTx[✅ Commit Transaction]

    CommitTx --> PublishEvent[📨 asyncio.create_task<br/>publish event]
    PublishEvent --> Success([✅ Return Updated Contact])

    classDef startEnd fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef process fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef decision fill:#FFD700,stroke:#333,stroke-width:2px,color:black
    classDef error fill:#FFB6C1,stroke:#DC143C,stroke-width:2px,color:black
    classDef async fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue

    class Start,Success,End1,End2,End3,End4 startEnd
    class FetchContact,UpdateDB,InvalidateCache,CreateAudit,CheckEmail process
    class Exists,CheckOwner,EmailChanged,EmailExists,UpdateSuccess decision
    class NotFound,Forbidden,BadRequest,Rollback,Error error
    class BeginTx,CommitTx,PublishEvent async
```

## Async Patterns

### Dependency Injection with FastAPI

```python
# dependencies.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_cache() -> Redis:
    return await get_redis_client()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Verify JWT and fetch user
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user = await user_repo.get_by_id(payload["user_id"])
    return user
```

**Dependency Injection Diagram:**

```mermaid
graph TB
    subgraph "FastAPI Dependency Injection"
        Endpoint[🌐 Endpoint Handler<br/>async def create_contact()]

        subgraph "Injected Dependencies"
            DB[🔌 get_db()<br/>yields AsyncSession]
            Cache[🔌 get_cache()<br/>returns Redis]
            Auth[🔌 get_current_user()<br/>returns User]
        end

        subgraph "Resolved Dependencies"
            DBSession[(💾 AsyncSession<br/>SQLAlchemy)]
            RedisClient[(⚡ Redis Client<br/>aioredis)]
            UserObj[👤 User Object<br/>from JWT]
        end
    end

    Endpoint --> DB
    Endpoint --> Cache
    Endpoint --> Auth

    DB --> DBSession
    Cache --> RedisClient
    Auth --> DBSession
    Auth --> UserObj

    classDef endpoint fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef dependency fill:#FFD700,stroke:#333,stroke-width:2px,color:black
    classDef resolved fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen

    class Endpoint endpoint
    class DB,Cache,Auth dependency
    class DBSession,RedisClient,UserObj resolved
```

### Background Tasks with Celery

```python
# tasks.py (Celery)
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="amqp://rabbitmq:5672",
    backend="redis://redis:6379/0"
)

@celery_app.task
def send_welcome_email(user_id: int):
    # Send email asynchronously
    user = get_user(user_id)
    send_email(user.email, "Welcome!", template="welcome")

@celery_app.task
def generate_report(contact_ids: list[int]):
    # Long-running report generation
    contacts = get_contacts(contact_ids)
    report = create_pdf_report(contacts)
    store_in_s3(report)

# In FastAPI endpoint
from fastapi import BackgroundTasks

@router.post("/contacts/batch-export")
async def batch_export(
    contact_ids: list[int],
    background_tasks: BackgroundTasks
):
    # Queue background task
    task = generate_report.delay(contact_ids)
    return {"task_id": task.id, "status": "queued"}
```

**Background Task Diagram:**

```mermaid
flowchart TD
    API[🌐 FastAPI Endpoint] --> Queue[📬 RabbitMQ Queue]
    Queue --> Worker1[⚙️ Celery Worker 1]
    Queue --> Worker2[⚙️ Celery Worker 2]

    Worker1 --> Task1[📧 Send Email Task]
    Worker1 --> Task2[📊 Generate Report Task]
    Worker2 --> Task3[📧 Send Email Task]

    Task1 --> SMTP[📨 SMTP Server]
    Task2 --> S3[📦 S3 Storage]
    Task3 --> SMTP

    Result[💾 Redis Backend] -.stores.-> Task1
    Result -.stores.-> Task2
    Result -.stores.-> Task3

    classDef api fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef queue fill:#FFD700,stroke:#333,stroke-width:2px,color:black
    classDef worker fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef storage fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue

    class API api
    class Queue queue
    class Worker1,Worker2,Task1,Task2,Task3 worker
    class Result,S3,SMTP storage
```

## Configuration Mapping

### From Pydantic Settings

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"
    DATABASE_POOL_SIZE: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Celery
    CELERY_BROKER_URL: str = "amqp://rabbitmq:5672"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Monitoring
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
```

**Configuration Diagram:**

```mermaid
graph TB
    subgraph "FastAPI Configuration"
        Settings[⚙️ Pydantic Settings<br/>BaseSettings]

        subgraph "Database Config"
            DBUrl[💾 DATABASE_URL<br/>postgresql+asyncpg://...]
            PoolSize[💾 POOL_SIZE: 10]
        end

        subgraph "Cache Config"
            RedisUrl[⚡ REDIS_URL<br/>redis://localhost:6379]
            MaxConn[⚡ MAX_CONNECTIONS: 50]
        end

        subgraph "Security Config"
            SecretKey[🔐 SECRET_KEY<br/>from env]
            Algorithm[🔐 ALGORITHM: HS256]
            TokenExp[🔐 TOKEN_EXPIRE: 30min]
        end

        subgraph "Worker Config"
            BrokerUrl[📬 CELERY_BROKER<br/>amqp://rabbitmq:5672]
            Backend[💾 RESULT_BACKEND<br/>redis://...]
        end

        subgraph "Monitoring Config"
            PrometheusPort[📊 PROMETHEUS_PORT: 9090]
            LogLevel[📝 LOG_LEVEL: INFO]
        end
    end

    Settings --> DBUrl
    Settings --> PoolSize
    Settings --> RedisUrl
    Settings --> MaxConn
    Settings --> SecretKey
    Settings --> Algorithm
    Settings --> TokenExp
    Settings --> BrokerUrl
    Settings --> Backend
    Settings --> PrometheusPort
    Settings --> LogLevel

    DBUrl --> PostgreSQL[(💾 PostgreSQL)]
    RedisUrl --> Redis[(⚡ Redis)]
    BrokerUrl --> RabbitMQ[🐰 RabbitMQ]

    classDef config fill:#FFD700,stroke:#333,stroke-width:2px,color:black
    classDef database fill:#E6E6FA,stroke:#333,stroke-width:2px,color:darkblue
    classDef security fill:#FFB6C1,stroke:#DC143C,stroke-width:2px,color:black

    class Settings,DBUrl,PoolSize,RedisUrl,MaxConn,BrokerUrl,Backend,PrometheusPort,LogLevel config
    class PostgreSQL,Redis,RabbitMQ database
    class SecretKey,Algorithm,TokenExp security
```

## Async SQLAlchemy Pattern

```python
# db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Usage in repository
class ContactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, contact: ContactCreate) -> Contact:
        async with self.db.begin():
            db_contact = Contact(**contact.dict())
            self.db.add(db_contact)
            await self.db.flush()
            await self.db.refresh(db_contact)
            return db_contact
```

## Kubernetes Deployment (Alternative to Docker Compose)

See `deployment-diagrams.md` for full Kubernetes microservices pattern with FastAPI.

## Generating Diagrams

### Automated Generation

1. **Architecture Diagram**: Analyze file structure, decorators, dependency injection
2. **Deployment Diagram**: Extract from docker-compose.yml or K8s manifests
3. **Sequence Diagram**: Trace async function calls from endpoints
4. **Activity Diagram**: Document business logic flows from service methods

### Manual Creation Guidelines

1. Use `async/await` annotations in diagrams
2. Show dependency injection clearly
3. Indicate background tasks with async symbols
4. Document transaction boundaries

## See Also

- [Spring Boot Example](../spring-boot/) - Java synchronous patterns
- [React Example](../react/) - Frontend component architecture
- [Python ETL Example](../python-etl/) - Data pipeline patterns
