---
name: mermaid-diagramming
description: Create Mermaid diagrams in Obsidian including flowcharts, sequence diagrams, class diagrams, and more. Use when visualizing processes, system architectures, workflows, or any structured relationships in Obsidian notes.
---

# Mermaid Diagramming in Obsidian

Obsidian has built-in Mermaid support. Use fenced code blocks with `mermaid` language identifier.

For common syntax (styling, comments, themes), see [reference.md](reference.md).

## ⚠️ Obsidian-Specific Constraints

**Rendering Differences**: Obsidian's Mermaid version may lag behind mermaid.js releases. Some cutting-edge features may not work.

**Theme Interaction**: Diagram colors adapt to Obsidian theme. Use explicit styles for consistent appearance across themes.

**Performance**: Very large diagrams (50+ nodes) may slow down rendering. Split into multiple diagrams if needed.

**Export**: PDF export converts diagrams to images. For external sharing, capture as PNG/SVG.

**No JavaScript**: Click events and JavaScript callbacks are disabled for security.

---

## Diagram Selection Guide

| Use Case | Diagram Type | Keyword |
|----------|--------------|---------|
| Process flow, decision trees | Flowchart | `flowchart` |
| API calls, message passing | Sequence | `sequenceDiagram` |
| OOP design, relationships | Class | `classDiagram` |
| Project timeline, scheduling | Gantt | `gantt` |
| State machine, lifecycle | State | `stateDiagram-v2` |
| Git branching strategy | Gitgraph | `gitGraph` |
| Brainstorming, hierarchies | Mindmap | `mindmap` |
| Proportions, percentages | Pie Chart | `pie` |
| Database schema, entities | ER Diagram | `erDiagram` |
| User experience steps, satisfaction | User Journey | `journey` |
| Historical events, milestones | Timeline | `timeline` |
| Priority matrix, 2D positioning | Quadrant Chart | `quadrantChart` |
| Flow visualization, proportional bands | Sankey Diagram | `sankey-beta` |
| Numerical data visualization | XY Chart | `xychart-beta` |
| Precise element positioning, layouts | Block Diagram | `block-beta` |
| Cloud services, service relationships | Architecture | `architecture-beta` |

---

## Quick Start Examples

### Flowchart

```mermaid
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

**Key syntax:**
- Direction: `TD` (top-down), `LR` (left-right), `BT`, `RL`
- Shapes: `[rect]`, `(rounded)`, `{diamond}`, `[(cylinder)]`, `((circle))`
- Arrows: `-->`, `-.->` (dotted), `==>` (thick)
- Labels: `-->|text|` or `-- text -->`

For details: [flowchart.md](flowchart.md)

---

### Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant D as Database

    C->>S: HTTP Request
    activate S
    S->>D: Query
    D-->>S: Result
    S-->>C: Response
    deactivate S
```

**Key syntax:**
- Arrows: `->>` (sync), `-->>` (response), `-)` (async)
- Activation: `activate`/`deactivate` or `+`/`-` suffix
- Control: `loop`, `alt`/`else`, `opt`, `par`/`and`, `critical`
- Notes: `Note right of A: text`, `Note over A,B: text`

For details: [sequence.md](sequence.md)

---

### Class Diagram

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
    class Dog {
        +fetch() void
    }
    Animal <|-- Dog : extends
```

**Key syntax:**
- Visibility: `+` public, `-` private, `#` protected, `~` package
- Relations: `<|--` inheritance, `*--` composition, `o--` aggregation, `-->` association
- Methods: `+method(args) returnType`

For details: [class-diagram.md](class-diagram.md)

---

### Gantt Chart

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD

    section Planning
    Requirements    :a1, 2024-01-01, 7d
    Design          :a2, after a1, 5d

    section Development
    Implementation  :2024-01-15, 14d
    Testing         :7d
```

**Key syntax:**
- `dateFormat`: Date format (YYYY-MM-DD, etc.)
- Tasks: `name :id, start, duration` or `name :after id, duration`
- Modifiers: `done`, `active`, `crit`, `milestone`

For details: [gantt.md](gantt.md)

---

### State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Success : complete
    Processing --> Error : fail
    Success --> [*]
    Error --> Idle : retry
```

**Key syntax:**
- Start/End: `[*]`
- Transition: `State1 --> State2 : event`
- Composite: `state Name { ... }`
- Fork/Join: `state fork_name <<fork>>`, `<<join>>`

For details: [state.md](state.md)

---

### Gitgraph

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "feat-1"
    commit id: "feat-2"
    checkout main
    merge develop id: "v1.0" tag: "release"
```

**Key syntax:**
- `commit`: Add commit, optional `id:`, `tag:`, `type:`
- `branch name`: Create branch
- `checkout name`: Switch branch
- `merge name`: Merge branch

For details: [gitgraph.md](gitgraph.md)

---

### Mindmap

```mermaid
mindmap
    root((Project))
        Frontend
            React
            TypeScript
        Backend
            Node.js
            PostgreSQL
        DevOps
            Docker
            CI/CD
```

**Key syntax:**
- Indentation defines hierarchy
- Shapes: `root((circle))`, `(rounded)`, `[square]`, `))cloud((`
- Use 4-space or tab indentation

For details: [mindmap.md](mindmap.md)

---

### Pie Chart

```mermaid
pie showData
    title Browser Market Share
    "Chrome" : 65
    "Safari" : 19
    "Firefox" : 8
    "Edge" : 5
    "Other" : 3
```

**Key syntax:**
- `title`: Optional chart title
- `showData`: Display values on segments
- Format: `"Label" : value`

For details: [pie.md](pie.md)

---

### ER Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {
        int id PK
        string email UK
        string name
    }
```

**Key syntax:**
- Entities: `ENTITY_NAME`
- Attributes: `type name [PK/FK/UK]`
- Cardinality: `||--o{` (one to many), `||--||` (one to one)
- Relationship: `ENTITY1 REL ENTITY2 : label`

For details: [er-diagram.md](er-diagram.md)

---

### User Journey

```mermaid
journey
    title Customer Support
    section Contact
      Submit ticket: 2: Customer
      Receive notice: 4: Agent
    section Resolution
      Troubleshoot issue: 3: Agent
      Confirm solution: 5: Customer
```

**Key syntax:**
- Sections: `section name`
- Tasks: `Task name: score: actor`
- Score: 1-5 (1 = unsatisfied, 5 = satisfied)
- Actors: User roles involved

For details: [journey.md](journey.md)

---

### Timeline

```mermaid
timeline
    title Product Roadmap
    section 2023
        Q1 2023 : MVP launch
        Q4 2023 : v1.0 release
    section 2024
        Q2 2024 : Major features
        Q4 2024 : v2.0
```

**Key syntax:**
- Time periods: `period : event`
- Sections: Group related periods
- Multiple events: `period : event1 : event2`
- Flexible format: Years, months, quarters, or custom text

For details: [timeline.md](timeline.md)

---

### Quadrant Chart

```mermaid
quadrantChart
    title Feature Prioritization
    x-axis Effort --> Value
    y-axis Complexity --> Impact
    Dark Mode: [0.4, 0.7]
    Search: [0.6, 0.8]
    Export PDF: [0.7, 0.6]
    Fix UI Bug: [0.2, 0.3]
```

**Key syntax:**
- Axes: `x-axis label --> label` and `y-axis label --> label`
- Points: `Name: [x, y]` (coordinates 0.0-1.0)
- Quadrants: Auto-divided at 0.5 on both axes

For details: [quadrant-chart.md](quadrant-chart.md)

---

### Sankey Diagram

```mermaid
sankey-beta

A,B,10
A,C,15
B,D,8
C,D,22
```

**Key syntax:**
- CSV format: `source, target, value`
- Three columns required
- Values are numeric (flow magnitude)
- Nodes auto-created from sources/targets

For details: [sankey.md](sankey.md)

---

### XY Chart

```mermaid
xychart-beta
    title "Sales Data"
    x-axis [Jan, Feb, Mar, Apr, May]
    y-axis "Revenue" 0 --> 100
    line [30, 45, 55, 70, 85]
```

**Key syntax:**
- Chart type: `xychart-beta` or `xychart-beta horizontal`
- X-axis: `[categories]` or `min --> max`
- Y-axis: `"label" min --> max`
- Series: `line [values]` or `bar [values]`

For details: [xychart.md](xychart.md)

---

### Block Diagram

```mermaid
block-beta
    columns 2
    A["Frontend"]:1
    B["Backend"]:1
    C["Database"]:2

    style A fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style B fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    style C fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
```

**Key syntax:**
- Blocks: `ID["Label"]:SPAN` - Each block on new line
- Columns: `columns N` - Define layout width
- Styling: `style ID fill:#hex,stroke:#hex,color:#hex`
- Spans: `:N` suffix - How many columns block occupies

For details: [block.md](block.md)

---

### Architecture Diagram

```mermaid
architecture-beta
    group Cloud(cloud)[Cloud Infrastructure]
    service web(server)[Web Server] in Cloud
    service api(server)[API Server] in Cloud
    service db(database)[Database]

    web:R --> L:api
    api:R --> L:db
```

**Key syntax:**
- Groups: `group {id}({icon})[{label}]` - Organize services
- Services: `service {id}({icon})[{label}] (in {parent})?` - Available icons: server, database, cloud, disk, internet
- Nesting: `in {parent_id}` - Place service/group inside parent group
- Connections: `{id1}:{pos} {arrow} {pos}:{id2}` - Position: L(eft), R(ight), T(op), B(ottom)
- Arrows: `-->` (right), `<--` (left), `--` (both)

For details: [architecture.md](architecture.md)

---


## Common Patterns

### Adding Styles

```mermaid
flowchart LR
    A[Normal] --> B[Styled]
    style B fill:#f96,stroke:#333,stroke-width:2px
```

### Using Classes

```mermaid
flowchart LR
    A:::highlight --> B --> C:::highlight
    classDef highlight fill:#ff0,stroke:#f00,stroke-width:2px
```

### Comments

```mermaid
flowchart TD
    %% This is a comment
    A --> B
```

---

## Reference

For complete documentation on common features:
- [reference.md](reference.md) - Styling, themes, comments, directives

For diagram-specific guides:
- [flowchart.md](flowchart.md) - Node shapes, links, subgraphs
- [sequence.md](sequence.md) - Messages, activation, control flow
- [class-diagram.md](class-diagram.md) - Classes, relationships
- [gantt.md](gantt.md) - Tasks, dependencies, milestones
- [state.md](state.md) - States, transitions, composite states
- [gitgraph.md](gitgraph.md) - Commits, branches, merges
- [mindmap.md](mindmap.md) - Hierarchies, node shapes
- [pie.md](pie.md) - Proportional data
- [er-diagram.md](er-diagram.md) - Entities, attributes, relationships (Session 1)
- [journey.md](journey.md) - User journeys, satisfaction scores (Session 1)
- [timeline.md](timeline.md) - Events, milestones, time periods (Session 1)
- [quadrant-chart.md](quadrant-chart.md) - Priority matrix, 2D positioning (Session 2)
- [sankey.md](sankey.md) - Flow visualization, proportional bands (Session 2)
- [xychart.md](xychart.md) - Numerical data visualization (Session 2)
- [block.md](block.md) - Element positioning, multi-column layouts (Session 3)
- [architecture.md](architecture.md) - Cloud services, service relationships (Session 3)
