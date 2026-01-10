# Mermaid Diagram Examples

This reference provides ready-to-use Mermaid diagram templates for common documentation scenarios.

## Flowcharts (graph)

### System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        UI[React UI]
        API[API Client]
    end

    subgraph "Backend"
        DRF[Django REST]
        Celery[Celery Workers]
    end

    subgraph "Storage"
        DB[(PostgreSQL)]
        Redis[(Redis)]
    end

    UI --> API
    API --> DRF
    DRF --> DB
    DRF --> Celery
    Celery --> Redis
```

### Data Processing Flow

```mermaid
graph LR
    A[CSV Upload] --> B{Valid?}
    B -->|Yes| C[Process]
    B -->|No| D[Show Errors]
    C --> E[Save Results]
    E --> F[Notify User]
```

### Decision Tree

```mermaid
graph TD
    Start[User Upload] --> Q1{File Size?}
    Q1 -->|<10MB| Q2{Valid CSV?}
    Q1 -->|>10MB| Error1[Too Large]
    Q2 -->|Yes| Process[Start Processing]
    Q2 -->|No| Error2[Invalid Format]
```

## Sequence Diagrams

### API Call Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant C as Celery
    participant DB as Database

    U->>F: Upload CSV
    F->>B: POST /uploads
    B->>DB: Save upload
    B->>C: Queue task
    B-->>F: Return job_id
    F-->>U: Show progress
    C->>C: Process data
    C->>DB: Save results
    C-->>F: Progress updates
    F-->>U: Completed!
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant JWT

    User->>Frontend: Login credentials
    Frontend->>API: POST /auth/login
    API->>JWT: Verify credentials
    JWT-->>API: Generate token
    API-->>Frontend: Return token
    Frontend->>Frontend: Store token
    Frontend-->>User: Logged in
```

## Entity Relationship Diagrams

### Database Schema

```mermaid
erDiagram
    COMPANY ||--o{ USER : has
    COMPANY ||--o{ DATA_UPLOAD : owns
    USER ||--o{ DATA_UPLOAD : creates
    DATA_UPLOAD ||--|| PROCESSING_JOB : triggers
    PROCESSING_JOB ||--o{ MODEL_RESULT : produces

    COMPANY {
        int id PK
        string name
        string rut
    }

    USER {
        int id PK
        int company_id FK
        string email
    }

    DATA_UPLOAD {
        uuid id PK
        int company_id FK
        string file_path
        string status
    }
```

## State Diagrams

### Job Status States

```mermaid
stateDiagram-v2
    [*] --> Pending: File Uploaded
    Pending --> Validating: Start
    Validating --> Processing: Valid
    Validating --> Failed: Invalid
    Processing --> Completed: Success
    Processing --> Failed: Error
    Completed --> [*]
    Failed --> [*]
```

### User Journey

```mermaid
journey
    title CSV Upload Journey
    section Upload
      Select File: 5: User
      Validate: 3: System
    section Process
      Queue Job: 5: User
      Wait: 3: User
    section Results
      View Data: 5: User
      Export: 5: User
```

## Gantt Charts

### Project Timeline

```mermaid
gantt
    title Development Phases
    dateFormat  YYYY-MM-DD
    section Phase 1
    Infrastructure      :a1, 2025-11-01, 3d
    Backend Models      :a2, after a1, 2d
    section Phase 2
    API Endpoints       :b1, after a2, 3d
    Frontend UI         :b2, after a2, 4d
    section Phase 3
    Integration         :c1, after b1, 2d
    Testing             :c2, after c1, 2d
```

## Tips for Effective Diagrams

### Keep it Simple
- Maximum 7-10 nodes per diagram
- Split complex flows into multiple diagrams
- Use subgraphs for grouping

### Use Descriptive Labels
- Clear, concise text
- Action verbs for processes
- Questions for decisions

### Color Coding (Optional)
```mermaid
graph LR
    A[Normal] --> B[Normal]
    C[Important]:::important --> D[Important]:::important
    E[Warning]:::warning

    classDef important fill:#9f6,stroke:#333
    classDef warning fill:#f96,stroke:#333
```

### Direction Matters
- `TB` (Top to Bottom) - Hierarchies, workflows
- `LR` (Left to Right) - Timelines, processes
- `RL` (Right to Left) - Reverse flows
- `BT` (Bottom to Top) - Rare, specific cases

## Common Patterns

### Multi-Step Process
```mermaid
graph LR
    A[Step 1] --> B[Step 2]
    B --> C[Step 3]
    C --> D[Step 4]
    D --> E[Complete]

    B -.->|Optional| F[Alternative]
    F -.-> C
```

### System Components
```mermaid
graph TB
    subgraph "User Layer"
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph "Application Layer"
        API[API Gateway]
        Auth[Auth Service]
    end

    subgraph "Data Layer"
        DB[(Database)]
        Cache[(Cache)]
    end

    Web --> API
    Mobile --> API
    API --> Auth
    API --> DB
    API --> Cache
```

### Error Handling
```mermaid
graph TD
    Start[Request] --> Try{Execute}
    Try -->|Success| Success[Return Data]
    Try -->|Error| Log[Log Error]
    Log --> Retry{Retry?}
    Retry -->|Yes| Try
    Retry -->|No| Fail[Return Error]
```

## Mermaid Resources

- **Official Docs:** https://mermaid.js.org/
- **Live Editor:** https://mermaid.live/
- **GitHub Support:** Renders automatically in .md files
- **VS Code:** Install "Markdown Preview Mermaid Support" extension