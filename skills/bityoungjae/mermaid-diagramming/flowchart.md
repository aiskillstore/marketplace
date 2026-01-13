# Flowchart Reference

Complete guide for Mermaid flowcharts in Obsidian.

---

## Direction

| Keyword | Direction |
|---------|-----------|
| `TD` / `TB` | Top to Bottom |
| `BT` | Bottom to Top |
| `LR` | Left to Right |
| `RL` | Right to Left |

```mermaid
flowchart LR
    A --> B --> C
```

---

## Node Shapes

| Shape | Syntax | Use Case |
|-------|--------|----------|
| Rectangle | `[text]` | Process, action |
| Rounded | `(text)` | Start/end, general |
| Stadium | `([text])` | Terminal, pill shape |
| Subroutine | `[[text]]` | Predefined process |
| Cylinder | `[(text)]` | Database, storage |
| Circle | `((text))` | Connector, event |
| Diamond | `{text}` | Decision, condition |
| Hexagon | `{{text}}` | Preparation |
| Parallelogram | `[/text/]` | Input/output |
| Trapezoid | `[/text\]` | Manual operation |
| Double Circle | `(((text)))` | End state |
| Flag | `>text]` | Async, signal |

### All Shapes Example

```mermaid
flowchart TB
    A[Rectangle] --> B(Rounded)
    B --> C([Stadium])
    C --> D[[Subroutine]]
    D --> E[(Database)]
    E --> F((Circle))
    F --> G{Diamond}
    G --> H{{Hexagon}}
    H --> I[/Parallelogram/]
    I --> J>Flag]
```

---

## Links (Connections)

### Arrow Types

| Style | Syntax | Description |
|-------|--------|-------------|
| Arrow | `-->` | Standard flow |
| Open | `---` | No arrow |
| Dotted arrow | `-.->` | Optional, async |
| Thick arrow | `==>` | Emphasis, main flow |
| Circle end | `--o` | Reference |
| Cross end | `--x` | Termination |
| Bidirectional | `<-->` | Two-way flow |

### With Labels

```mermaid
flowchart LR
    A -->|Yes| B
    A -- No --> C
    B -.->|async| D
    C == main ==> D
```

### Link Length

More dashes = longer link:

```mermaid
flowchart TD
    A --> B
    A ---> C
    A ----> D
```

---

## Subgraphs

Group related nodes together.

### Basic Subgraph

```mermaid
flowchart TB
    subgraph Frontend
        A[React]
        B[Vue]
    end
    subgraph Backend
        C[Node.js]
        D[Python]
    end
    A --> C
    B --> D
```

### Subgraph with ID

```mermaid
flowchart TB
    subgraph sub1 [Client Layer]
        A[Browser]
    end
    subgraph sub2 [Server Layer]
        B[API]
    end
    sub1 --> sub2
```

### Nested Subgraphs

```mermaid
flowchart TB
    subgraph Cloud
        subgraph Region1 [US-East]
            A[Server A]
        end
        subgraph Region2 [EU-West]
            B[Server B]
        end
    end
    A <--> B
```

### Subgraph Direction

Each subgraph can have its own direction:

```mermaid
flowchart LR
    subgraph TOP
        direction TB
        A --> B
    end
    subgraph BOTTOM
        direction BT
        C --> D
    end
    TOP --> BOTTOM
```

---

## Styling

### Inline Style

```mermaid
flowchart LR
    A --> B
    style A fill:#f96,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,color:#fff
```

### Style Properties

| Property | Example | Description |
|----------|---------|-------------|
| `fill` | `fill:#f9f` | Background color |
| `stroke` | `stroke:#333` | Border color |
| `stroke-width` | `stroke-width:2px` | Border thickness |
| `color` | `color:#fff` | Text color |
| `stroke-dasharray` | `stroke-dasharray:5 5` | Dashed border |

### Class Definitions

```mermaid
flowchart LR
    A:::success --> B:::warning --> C:::error

    classDef success fill:#4CAF50,color:white
    classDef warning fill:#FFC107,color:black
    classDef error fill:#F44336,color:white
```

### Apply Class to Multiple Nodes

```mermaid
flowchart TD
    A --> B --> C --> D
    classDef highlight fill:#2196F3,color:white
    class A,C highlight
```

### Default Class

```mermaid
flowchart LR
    A --> B --> C
    classDef default fill:#e3f2fd,stroke:#1565c0
```

### Link Styling

```mermaid
flowchart LR
    A --> B --> C --> D
    linkStyle 0 stroke:red,stroke-width:2px
    linkStyle 1 stroke:green
    linkStyle default stroke:gray
```

---

## Special Features

### Chaining

Connect multiple nodes at once:

```mermaid
flowchart LR
    A --> B & C --> D
```

```mermaid
flowchart TB
    A & B --> C & D
```

### Multiline Text

```mermaid
flowchart LR
    A["Line 1
    Line 2
    Line 3"]
```

### Special Characters

Wrap in quotes for special characters:

```mermaid
flowchart LR
    A["Contains (parens) and {braces}"]
    B["Arrow -> symbol"]
    A --> B
```

### Comments

```mermaid
flowchart TD
    %% This is a comment
    A --> B
    %% Another comment
    B --> C
```

---

## Practical Examples

### Example 1: User Authentication Flow

```mermaid
flowchart TD
    A([Start]) --> B[Login Page]
    B --> C{Valid Credentials?}

    C -->|Yes| D[Generate Token]
    C -->|No| E[Show Error]
    E --> B

    D --> F{2FA Enabled?}
    F -->|Yes| G[Verify 2FA]
    F -->|No| H[Create Session]

    G -->|Success| H
    G -->|Fail| E

    H --> I[Dashboard]
    I --> J([End])

    style A fill:#4CAF50,color:white
    style J fill:#4CAF50,color:white
    style C fill:#FFC107
    style F fill:#FFC107
```

### Example 2: CI/CD Pipeline

```mermaid
flowchart LR
    subgraph Dev [Development]
        A[Code] --> B[Commit]
    end

    subgraph CI [Continuous Integration]
        C[Build] --> D[Unit Test]
        D --> E[Lint]
        E --> F[Integration Test]
    end

    subgraph CD [Continuous Deployment]
        G[Staging] --> H[E2E Test]
        H --> I[Production]
    end

    B --> C
    F --> G
    D -.->|Fail| A
    H -.->|Fail| A

    classDef dev fill:#e3f2fd
    classDef ci fill:#fff3e0
    classDef cd fill:#e8f5e9
    class A,B dev
    class C,D,E,F ci
    class G,H,I cd
```

### Example 3: E-Commerce Order Processing

```mermaid
flowchart TB
    A([Order Received]) --> B{In Stock?}

    B -->|Yes| C[Process Payment]
    B -->|No| D[Backorder]
    D --> E{Restock Available?}
    E -->|Yes| B
    E -->|No| F[Cancel & Refund]

    C --> G{Payment OK?}
    G -->|Yes| H[Prepare Shipment]
    G -->|No| I[Retry Payment]
    I --> C

    H --> J[Ship Order]
    J --> K[Update Tracking]
    K --> L([Delivered])
    F --> M([Cancelled])

    style A fill:#2196F3,color:white
    style L fill:#4CAF50,color:white
    style M fill:#F44336,color:white
    style B fill:#FFC107
    style G fill:#FFC107
    style E fill:#FFC107
```

### Example 4: Microservices Architecture

```mermaid
flowchart TB
    subgraph Client
        A[Web App]
        B[Mobile App]
    end

    subgraph Gateway
        C[API Gateway]
    end

    subgraph Services
        D[Auth Service]
        E[User Service]
        F[Order Service]
        G[Payment Service]
    end

    subgraph Data
        H[(User DB)]
        I[(Order DB)]
        J{{Message Queue}}
    end

    A --> C
    B --> C
    C --> D & E & F & G

    D --> H
    E --> H
    F --> I
    G --> I

    F <-.-> J
    G <-.-> J

    classDef client fill:#e3f2fd
    classDef gateway fill:#fff3e0
    classDef service fill:#e8f5e9
    classDef data fill:#fce4ec

    class A,B client
    class C gateway
    class D,E,F,G service
    class H,I,J data
```

---

## Obsidian Notes

**Theme Compatibility**: Colors may vary with Obsidian themes. Use explicit styles for consistent appearance.

**Performance**: Large diagrams (50+ nodes) may slow rendering. Split into multiple diagrams.

**Export**: PDF export renders diagrams as images. For sharing, capture as PNG/SVG.

**No JavaScript**: Click events and callbacks are disabled for security.

**Code Block Format**:
````
```mermaid
flowchart TD
    A --> B
```
````

---

## Quick Reference Table

| Category | Syntax | Example |
|----------|--------|---------|
| Direction | `flowchart DIR` | `flowchart LR` |
| Rectangle | `id[text]` | `A[Process]` |
| Diamond | `id{text}` | `B{Decision}` |
| Circle | `id((text))` | `C((Event))` |
| Database | `id[(text)]` | `D[(DB)]` |
| Arrow | `-->` | `A --> B` |
| Dotted | `-.->` | `A -.-> B` |
| Thick | `==>` | `A ==> B` |
| Label | `--\|text\|` | `A --\|Yes\| B` |
| Subgraph | `subgraph name` | `subgraph API` |
| Style | `style id prop` | `style A fill:#f96` |
| Class | `classDef name` | `classDef red fill:#f00` |
| Apply | `:::class` | `A:::red` |
| Comment | `%%` | `%% note` |
