# Mermaid Diagram Patterns

## Diagram Selection

| Diagram | Use When |
|---------|----------|
| C4 Context | System boundaries, external actors, high-level dependencies |
| C4 Container | Deployable units (services, databases, apps) |
| C4 Component | Internal structure of a single container |
| Flowchart | Control flow, pipelines, decision trees |
| Sequence | Request flows, API interactions, multi-step processes |
| ER Diagram | Data models, database schemas, entity relationships |
| Class Diagram | Object hierarchies, interface implementations |

Start minimal (3-5 nodes). Expand only when clarity requires it.

---

## C4 Context Diagram

Shows system scope and external actors.

```mermaid
C4Context
    title System Context

    Person(user, "User", "Primary system user")
    System(system, "System Name", "Core system description")
    System_Ext(external, "External System", "Third-party dependency")

    Rel(user, system, "Uses")
    Rel(system, external, "Calls API")
```

---

## C4 Container Diagram

Shows deployable units within the system.

```mermaid
C4Container
    title Container Diagram

    Person(user, "User")

    Container_Boundary(system, "System Name") {
        Container(app, "Application", "Language/Framework", "Handles requests")
        ContainerDb(db, "Database", "Technology", "Stores data")
        Container(worker, "Background Worker", "Language", "Processes async tasks")
    }

    System_Ext(external, "External API")

    Rel(user, app, "Uses", "HTTPS")
    Rel(app, db, "Reads/Writes")
    Rel(app, worker, "Enqueues jobs")
    Rel(worker, external, "Calls")
```

---

## C4 Component Diagram

Shows internal structure of a container.

```mermaid
C4Component
    title Application Components

    Container_Boundary(app, "Application") {
        Component(api, "API Layer", "Handles HTTP requests")
        Component(service, "Service Layer", "Business logic")
        Component(repo, "Repository", "Data access")
    }

    ContainerDb(db, "Database")

    Rel(api, service, "Calls")
    Rel(service, repo, "Uses")
    Rel(repo, db, "Queries")
```

---

## Flowchart

Shows control flow and decision points.

```mermaid
flowchart TD
    A[Start] --> B{Condition?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

### Pipeline Pattern

```mermaid
flowchart LR
    A[Input] --> B[Stage 1]
    B --> C[Stage 2]
    C --> D[Stage 3]
    D --> E[Output]
```

---

## Sequence Diagram

Shows interactions over time.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant S as Service
    participant D as Database

    C->>A: Request
    A->>S: Process
    S->>D: Query
    D-->>S: Result
    S-->>A: Response
    A-->>C: Result
```

### With Error Handling

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant S as Service

    C->>A: Request
    A->>S: Process

    alt Success
        S-->>A: Result
        A-->>C: 200 OK
    else Error
        S-->>A: Error
        A-->>C: 500 Error
    end
```

---

## ER Diagram

Shows data entities and relationships.

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"

    USER {
        id uuid PK
        email string
        created_at timestamp
    }

    ORDER {
        id uuid PK
        user_id uuid FK
        status string
        created_at timestamp
    }

    ORDER_ITEM {
        id uuid PK
        order_id uuid FK
        product_id uuid FK
        quantity int
    }

    PRODUCT {
        id uuid PK
        name string
        price_cents int
    }
```

---

## Class Diagram

Shows object relationships and hierarchies.

```mermaid
classDiagram
    class BaseHandler {
        <<abstract>>
        +handle(request)
        #validate(request)
    }

    class ConcreteHandler {
        +handle(request)
        -processData(data)
    }

    class Repository {
        <<interface>>
        +find(id)
        +save(entity)
    }

    class SqlRepository {
        -connection
        +find(id)
        +save(entity)
    }

    BaseHandler <|-- ConcreteHandler
    Repository <|.. SqlRepository
    ConcreteHandler --> Repository : uses
```

---

## Tips

- **Labels on arrows**: Use short verb phrases (`Calls`, `Reads`, `Emits`, `Subscribes to`)
- **Color sparingly**: Only to distinguish categories (internal vs external)
- **Group related nodes**: Use subgraphs/boundaries for clarity
- **Consistent naming**: Match names to actual code (class names, service names)
- **Link to code**: Reference the diagram from relevant source files
