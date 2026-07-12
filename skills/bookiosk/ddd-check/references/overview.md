# DDD Architecture Overview

## 1. Hexagonal Architecture — Core Design Principles

### 1.1 Layer Dependency Rules

**Call order** (outside → inside):

```
inAdaptor → Application → Domain → Repository (DB/Cache/Message)
                                 → outAdaptor (external 3rd-party services)
```

> Repository handles intra-domain data operations (DB, cache, messaging). Adaptor handles cross-domain external service calls. Repository does NOT depend on Adaptor.

**Dependency rules** (via dependency inversion):

| Layer | Depends On | Notes |
|-------|-----------|-------|
| **Adaptor** (`inAdaptor`/`outAdaptor`) | `application` interfaces | Implements interfaces defined by Application layer |
| **Application** | `domain`, `client`, `model` | Orchestration layer |
| **Infrastructure** | `domain`, `model` | Implements Repository interfaces defined by Domain layer |
| **Domain** | `model` only | Pure business logic, zero framework dependencies (Spring and static utils excepted) |
| **Client** | nothing internal | External RPC API surface; **forbidden** from depending on `model` layer — DTOs must be self-contained |
| **Model** | nothing | Shared enums, common business concepts; usable by `domain`, `application`, `adaptor`, `infrastructure` |

Key: All internal modules ultimately depend on the Domain layer. Technical details are separated from business logic.

```mermaid
graph TD
    subgraph "External"
        EXT[External Callers]
    end

    subgraph "Adaptor Layer"
        IN[Input Adaptor<br/>Controller / MQ / ScheduleX]
        OUT[Output Adaptor<br/>3rd-party API calls]
        INNER[Inner Adaptor]
    end

    subgraph "Application Layer"
        CMD[AppService<br/>Command / Write]
        QRY[QueryAppService<br/>Query / Read]
    end

    subgraph "Domain Layer"
        AGG[Aggregate + Entity + Value]
        DS[DomainService]
        REPO_INT[Repository Interface]
    end

    subgraph "Infrastructure Layer"
        REPO_IMPL[Repository Impl]
        MAPPER[Mapper]
        PO[PO]
    end

    subgraph "Client Layer"
        API[AppService Interface<br/>RequestDTO / ResponseDTO]
    end

    subgraph "Model Layer"
        M[Shared Enums / Concepts]
    end

    EXT --> IN
    IN --> CMD
    IN --> QRY
    CMD --> OUT
    CMD --> DS
    CMD --> REPO_INT
    QRY --> OUT
    QRY --> DS
    QRY --> REPO_INT
    DS --> AGG
    DS --> REPO_INT
    REPO_INT -.-> REPO_IMPL
    REPO_IMPL --> MAPPER
    MAPPER --> PO
    OUT --> INNER
    API --> CMD
    API --> QRY
    M --> AGG
    M --> DS
    M --> REPO_IMPL
    M --> CMD
    M --> QRY

    style EXT fill:#f9f,stroke:#333
    style IN fill:#bbf,stroke:#333
    style OUT fill:#bbf,stroke:#333
    style CMD fill:#bfb,stroke:#333
    style QRY fill:#bfb,stroke:#333
    style AGG fill:#fbb,stroke:#333
    style DS fill:#fbb,stroke:#333
    style REPO_INT fill:#fbb,stroke:#333
    style REPO_IMPL fill:#feb,stroke:#333
    style MAPPER fill:#feb,stroke:#333
    style PO fill:#feb,stroke:#333
```

### 1.2 Domain Layer Isolation

- Domain layer contains **only pure business code**
- Forbidden: direct framework/library references (Spring and static utility packages excepted)
- Technical implementations (DB, API calls) are abstracted behind interfaces, with concrete implementations in outer layers

---

## 2. Project Structure

```
com.example
├── domain/                          # Domain layer
│   └── {business}/                  # e.g., order, booking, refund
│       ├── model/
│       │   ├── aggregate/           # Aggregate roots
│       │   ├── entity/              # Entities
│       │   ├── value/               # Value objects
│       │   ├── param/               # Parameter objects (extends BaseParam)
│       │   └── result/              # Result objects (extends BaseResult)
│       ├── service/                 # Domain services
│       └── repository/              # Repository interfaces
├── application/                     # Application layer
│   └── {business}/
│       ├── scenario/                # Scene orchestration (AppService impls)
│       └── assembler/               # DTO ↔ Domain object mapping
├── client/                          # External API definitions
│   └── {business}/
│       ├── enums/                   # Client-side enums
│       ├── model/                   # Shared nested DTOs (extends BaseDTO)
│       ├── req/                     # Request DTOs (extends BaseDTO)
│       └── res/                     # Response DTOs (extends BaseDTO)
├── model/                           # Internal shared models
│   └── ...                          # Shared enums, common business concepts
├── infrastructure/                  # Infrastructure layer
│   └── {business}/
│       ├── repository/              # Repository implementations
│       ├── mysql/
│       │   ├── po/                  # Persistent Objects
│       │   └── mapper/              # MyBatis Mapper interfaces
│       └── converter/               # Aggregate ↔ PO converters
└── adaptor/                         # Anti-corruption layer
    └── {business}/
        ├── input/                   # Input adaptors (Controller, MQ consumer, scheduled tasks)
        ├── output/                  # Output adaptors (external service calls)
        └── inner/                   # Internal shared adaptors
```

---

## 3. Four DDD Development Modes

### 3.1 Mode Comparison

| Mode | Aggregate/Entity | Business Logic Location | Mutates State | Typical Scenario |
|------|------------------|------------------------|---------------|------------------|
| **Write** | Yes | Aggregate/Entity methods | Yes | Order creation, status changes |
| **Read** | Yes (data carrier only) | None (data transformation only) | No | Order queries |
| **Rule+Calculate** | Yes | Aggregate/Entity methods | No | Subsidy rule matching & calculation |
| **Pure Calculate** | No | DomainService | No | Fee calculation, search control, view rendering |

### 3.2 Mode Selection Decision Tree

```mermaid
flowchart TD
    A[Business Scenario Analysis] --> B{Modifies data state?}
    B -->|Yes| W[Write Mode]
    B -->|No| C{Has business logic?}
    C -->|No| R[Read Mode]
    C -->|Yes| D{Logic is rule-based?}
    D -->|Yes| RC[Rule+Calculate Mode]
    D -->|No| PC[Pure Calculate Mode]

    W --- W1["Aggregate: Yes<br/>Logic: Aggregate methods<br/>Mutates: Yes<br/>Example: Order creation"]
    R --- R1["Aggregate: Data carrier<br/>Logic: None<br/>Mutates: No<br/>Example: Order query"]
    RC --- RC1["Aggregate: Yes<br/>Logic: Aggregate methods<br/>Mutates: No<br/>Example: Subsidy matching"]
    PC --- PC1["Aggregate: No<br/>Logic: DomainService<br/>Mutates: No<br/>Example: Fee calculation"]
```

### 3.3 Call Chain Sequence Diagrams

**Write Mode (complex — with external pre-validation):**

```mermaid
sequenceDiagram
    participant I as Input Adaptor
    participant A as AppService
    participant O as Output Adaptor
    participant D as DomainService
    participant Agg as Aggregate
    participant R as Repository
    participant DB as Database

    I->>A: RequestDTO
    A->>A: requestDTO.check()
    A->>O: validateInventory(productId, qty)
    O-->>A: ResultDO<InventoryDTO>
    A->>O: checkPrice(productId, price)
    O-->>A: ResultDO<PriceDTO>
    A->>A: Assembler.toParam()
    A->>D: createOrder(param)
    D->>R: buildLock(key)
    D->>D: lock.tryLock()
    D->>R: query(query)
    R->>DB: SELECT
    DB-->>R: PO
    R->>R: Converter.toAggregate()
    R-->>D: ResultDO<Aggregate>
    D->>Agg: confirmPayment(param)
    Agg->>Agg: validate + modify state
    D->>R: save(aggregate)
    R->>R: Converter.toPO()
    R->>DB: INSERT/UPDATE
    R-->>D: ResultDO<Void>
    D->>D: lock.unlock()
    D-->>A: ResultDO<Aggregate>
    A->>A: Assembler.toResponseDTO()
    A-->>I: ResultDO<ResponseDTO>
```

**Read Mode (hybrid — intra-domain + cross-domain):**

```mermaid
sequenceDiagram
    participant I as Input Adaptor
    participant Q as QueryAppService
    participant R as Repository
    participant O as Output Adaptor
    participant DB as Database
    participant Ext as External Service

    I->>Q: RequestDTO
    Q->>Q: requestDTO.check()
    Q->>R: findById(orderId)
    R->>DB: SELECT
    DB-->>R: PO
    R->>R: Converter.toAggregate()
    R-->>Q: ResultDO<Aggregate>
    Q->>O: queryLogistics(logisticsNo)
    O->>Ext: API call
    Ext-->>O: 3rd-party response
    O->>O: Converter (anti-corruption)
    O-->>Q: ResultDO<LogisticsDTO>
    Q->>Q: Assembler.assemble(aggregate, logistics)
    Q-->>I: ResultDO<ResponseDTO>
```

**Pure Calculate Mode:**

```mermaid
sequenceDiagram
    participant I as Input Adaptor
    participant Q as QueryAppService
    participant O as Output Adaptor
    participant D as DomainService
    participant Ext as External Service

    I->>Q: RequestDTO
    Q->>Q: requestDTO.check()
    Q->>O: queryExchangeRate(currency)
    O->>Ext: API call
    Ext-->>O: 3rd-party response
    O-->>Q: ResultDO<RateDTO>
    Q->>Q: Assembler.toParam()
    Q->>D: calculate(param)
    D->>D: pure computation (stateless)
    D-->>Q: ResultDO<CalculateResult>
    Q->>Q: Assembler.toResponseDTO()
    Q-->>I: ResultDO<ResponseDTO>
```

**Rule+Calculate Mode:**

```mermaid
sequenceDiagram
    participant I as Input Adaptor
    participant Q as QueryAppService
    participant D as DomainService
    participant R as Repository
    participant Agg as Rule Aggregate
    participant DB as Database

    I->>Q: RequestDTO
    Q->>Q: requestDTO.check()
    Q->>Q: Assembler.toParam()
    Q->>D: calculateBonus(param)
    D->>R: queryAllRule()
    R->>DB: SELECT
    DB-->>R: PO list
    R->>R: Converter (PO→Aggregate)
    R-->>D: ResultDO<List<RuleAggregate>>
    D->>D: sort by priority
    loop For each rule aggregate
        D->>Agg: matchRule(items, param)
        Agg-->>D: MatchResult (matched + remaining)
        D->>Agg: calculateBonus(matched, param)
        Agg-->>D: List<CalculateResult>
    end
    D-->>Q: ResultDO<List<CalculateResult>>
    Q->>Q: Assembler.toResponseDTO()
    Q-->>I: ResultDO<ResponseDTO>
```

### 3.4 Deprecated (text-only call chains)

---

## 4. Spec File Usage by Mode

### 4.1 Write Mode — Required Specs
1. `ddd-domain-layer.md` → Base + Write mode Domain spec
2. `ddd-application-layer.md` → Base + Write mode Application spec
3. `ddd-adaptor-layer.md` → Base + Write mode Adaptor spec
4. `ddd-infrastructure-layer.md` → Base + Write mode Infrastructure spec
5. `ddd-client-layer.md` → Client layer spec
6. `ddd-model-layer.md` → Model layer spec

### 4.2 Read Mode — Required Specs
1. `ddd-domain-layer.md` → Base + Read mode Domain spec
2. `ddd-application-layer.md` → Base + Read mode Application spec
3. `ddd-adaptor-layer.md` → Base + Read mode Adaptor spec
4. `ddd-infrastructure-layer.md` → Base + Read mode Infrastructure spec
5. `ddd-client-layer.md` → Client layer spec
6. `ddd-model-layer.md` → Model layer spec

### 4.3 Pure Calculate Mode — Required Specs
1. `ddd-domain-layer.md` → Base + Pure Calculate mode Domain spec
2. `ddd-application-layer.md` → Base + Pure Calculate mode Application spec
3. `ddd-adaptor-layer.md` → Base + Pure Calculate mode Adaptor spec
4. `ddd-client-layer.md` → Client layer spec
5. `ddd-model-layer.md` → Model layer spec

> Pure Calculate mode does NOT require Infrastructure layer — no aggregates, no entities, no persistence.

### 4.4 Rule+Calculate Mode — Required Specs
1. `ddd-domain-layer.md` → Base + Rule+Calculate mode Domain spec
2. `ddd-application-layer.md` → Base + Rule+Calculate mode Application spec
3. `ddd-adaptor-layer.md` → Base spec
4. `ddd-infrastructure-layer.md` → Base + Rule+Calculate mode Infrastructure spec
5. `ddd-client-layer.md` → Client layer spec
6. `ddd-model-layer.md` → Model layer spec

---

## 5. Document Index

| Spec | Content |
|------|---------|
| [domain-layer.md](domain-layer.md) | Aggregates, Entities, Value Objects, DomainService, Repository interfaces |
| [application-layer.md](application-layer.md) | CQRS, Scene orchestration, Assembler, AppService |
| [adaptor-layer.md](adaptor-layer.md) | Input/Output Adaptor, Anti-corruption layer |
| [infrastructure-layer.md](infrastructure-layer.md) | Repository impl, PO, Mapper, Converter |
| [client-layer.md](client-layer.md) | External RPC interface definitions, DTOs |
| [model-layer.md](model-layer.md) | Internal shared models, enums |
| [base-classes-reference.md](base-classes-reference.md) | All base classes and core type definitions |
| [anti-patterns.md](anti-patterns.md) | Consolidated anti-patterns — all forbidden patterns by layer |
