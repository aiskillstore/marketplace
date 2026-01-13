# Block Diagram Reference

Complete guide for Mermaid block diagrams in Obsidian. Block diagrams enable precise control over element positioning for visualizing complex systems, architectures, and networks.

---

## Overview

Block diagrams in Obsidian provide a way to create visual diagrams with labeled blocks arranged in columns and rows. Unlike flowcharts with automatic layout, block diagrams let you specify exact positioning.

**Best for:**
- System architecture with layered components
- Security frameworks and control hierarchies
- Network topology and hardware designs
- System hierarchies with multiple levels
- Multi-column layouts and grids

```mermaid
block-beta
    columns 2
    Frontend["Web App"]
    Backend["API Server"]
    Database["Data Store"]
    Cache["Cache Layer"]
```

---

## Basic Syntax

### Structure

Blocks can be defined in several ways:
```
ID                    Simple block with ID as label
ID["Label"]           Block with custom label
ID:N                  Block spanning N columns
ID["Label"]:N         Block with label spanning N columns
```

### Column Span

The `:N` suffix specifies how many columns the block spans:

```mermaid
block-beta
    columns 3
    A["Narrow"]:1
    B["Medium"]:2
    C["Full Width"]:3
```

### Simple Example

```mermaid
block-beta
    columns 1
    A["Component A"]
    B["Component B"]
    C["Component C"]
```

---

## Block Shapes

Block diagrams support various shapes using different bracket notations:

| Shape | Syntax | Example |
|-------|--------|---------|
| Rectangle | `["text"]` | `A["Server"]` |
| Rounded | `("text")` | `A("Process")` |
| Circle | `(("text"))` | `A(("DB"))` |
| Diamond | `{"text"}` | `A{"Decision"}` |
| Hexagon | `{{"text"}}` | `A{{"Worker"}}` |
| Stadium | `(["text"])` | `A(["Queue"])` |
| Subroutine | `[["text"]]` | `A[["Module"]]` |
| Cylinder | `[("text")]` | `A[("Storage")]` |
| Asymmetric | `>"text"]` | `A>"Flag"]` |

```mermaid
block-beta
    columns 3
    A["Rectangle"]
    B("Rounded")
    C(("Circle"))
    D{"Diamond"}
    E{{"Hexagon"}}
    F(["Stadium"])
```

---

## Block Styling

### Color & Appearance

Use `style` declarations to customize blocks:

```mermaid
block-beta
    columns 2
    A["Frontend"]
    B["Backend"]
    C["Database"]
    D["Cache"]

    style A fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style B fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    style C fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style D fill:#fff3e0,stroke:#ef6c00,color:#e65100
```

### Style Properties

| Property | Example | Description |
|----------|---------|-------------|
| `fill` | `fill:#e3f2fd` | Background color (hex) |
| `stroke` | `stroke:#1565c0` | Border color |
| `color` | `color:#0d47a1` | Text color |
| `stroke-width` | `stroke-width:2px` | Border thickness |

---

## Practical Examples

### Example 1: Security Framework

```mermaid
block-beta
    columns 1
    A["AppArmor / SELinux"]:1
    B["Seccomp"]:1
    C["Linux Capabilities"]:1
    D["Namespaces"]:1
    E["Cgroups"]:1

    style A fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style B fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style C fill:#fff3e0,stroke:#ef6c00,color:#e65100
    style D fill:#fce4ec,stroke:#c2185b,color:#880e4f
    style E fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
```

### Example 2: Three-Tier Architecture

```mermaid
block-beta
    columns 3
    Web1["Web 1"]:1
    Web2["Web 2"]:1
    Web3["Web 3"]:1

    App1["App 1"]:1
    App2["App 2"]:1
    App3["App 3"]:1

    DB["Database"]:3
    Cache["Cache"]:3

    style Web1 fill:#e3f2fd,stroke:#1565c0
    style Web2 fill:#e3f2fd,stroke:#1565c0
    style Web3 fill:#e3f2fd,stroke:#1565c0
    style App1 fill:#f3e5f5,stroke:#7b1fa2
    style App2 fill:#f3e5f5,stroke:#7b1fa2
    style App3 fill:#f3e5f5,stroke:#7b1fa2
    style DB fill:#e8f5e9,stroke:#2e7d32
    style Cache fill:#fff3e0,stroke:#ef6c00
```

### Example 3: Microservices Ecosystem

```mermaid
block-beta
    columns 2
    Frontend["Frontend"]:1
    Admin["Admin Panel"]:1

    Gateway["API Gateway"]:2

    Auth["Auth Service"]:1
    User["User Service"]:1

    Order["Order Service"]:1
    Payment["Payment Service"]:1

    DB["Main Database"]:2
    Queue["Message Queue"]:2

    style Frontend fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style Admin fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style Gateway fill:#fff3e0,stroke:#ef6c00,color:#e65100
    style Auth fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    style User fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    style Order fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    style Payment fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    style DB fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style Queue fill:#fce4ec,stroke:#c2185b,color:#880e4f
```

### Example 4: Cloud Infrastructure

```mermaid
block-beta
    columns 1
    CDN["CDN / CloudFront"]:1
    LB["Load Balancer"]:1
    Compute["Compute Instances"]:1
    Data["Data Layer"]:1
    Storage["Storage Layer"]:1

    style CDN fill:#ffebee,stroke:#b71c1c,color:#fff
    style LB fill:#fff3e0,stroke:#ef6c00,color:#000
    style Compute fill:#e3f2fd,stroke:#1565c0,color:#000
    style Data fill:#e8f5e9,stroke:#2e7d32,color:#000
    style Storage fill:#fce4ec,stroke:#c2185b,color:#000
```

### Example 5: Multi-Column Layout

```mermaid
block-beta
    columns 4
    space:1
    Title["System Architecture"]:2
    space:1

    Frontend["Frontend"]:1
    space:1
    Backend["Backend"]:1
    space:1

    API["API Layer"]:4

    DB1["DB 1"]:1
    DB2["DB 2"]:1
    Cache["Cache"]:1
    Queue["Queue"]:1

    style Title fill:#e1f5ff,stroke:#01579b,color:#000,stroke-width:2px
    style Frontend fill:#e3f2fd,stroke:#1565c0,color:#000
    style Backend fill:#f3e5f5,stroke:#7b1fa2,color:#000
    style API fill:#fff3e0,stroke:#ef6c00,color:#000
    style DB1 fill:#e8f5e9,stroke:#2e7d32,color:#000
    style DB2 fill:#e8f5e9,stroke:#2e7d32,color:#000
    style Cache fill:#ffe0b2,stroke:#e65100,color:#000
    style Queue fill:#fce4ec,stroke:#c2185b,color:#000
```

---

## Advanced Features

### Spanning Multiple Columns

Use larger column values to emphasize important components:

```mermaid
block-beta
    columns 3
    Small1["Small"]:1
    Big["Important Component"]:2
    Small2["Small"]:1
    Wide["Wide Element"]:3

    style Big fill:#ffebee,stroke:#b71c1c,color:#fff
    style Wide fill:#fff3e0,stroke:#ef6c00,color:#000
```

### Color Usage

Apply distinct colors to different component types for visual clarity:

```mermaid
block-beta
    columns 3
    A["Technical"]:1
    B["Infrastructure"]:1
    C["Data"]:1

    style A fill:#e3f2fd,stroke:#1565c0
    style B fill:#f3e5f5,stroke:#7b1fa2
    style C fill:#e8f5e9,stroke:#2e7d32
```

Use `fill` for background and `stroke` for border. Choose contrasting colors for different layers or categories to improve diagram readability.

---

## Arrows and Connections

Block diagrams support connections between blocks using arrow syntax:

### Basic Arrows

```mermaid
block-beta
    columns 3
    A["Input"] space B["Output"]
    A --> B
```

### Arrow Types

| Arrow | Syntax | Description |
|-------|--------|-------------|
| Directed | `-->` | Arrow with head |
| Undirected | `---` | Line without head |
| Labeled | `-- "text" -->` | Arrow with label |

### Labeled Connections

```mermaid
block-beta
    columns 3
    Client space:2 Server
    Client -- "request" --> Server
```

### Multiple Connections

```mermaid
block-beta
    columns 3
    A["Service A"] B["Service B"] C["Service C"]
    A --> B
    B --> C
    A --> C
```

---

## Nested Blocks

Create hierarchical structures using nested block groups:

### Basic Nesting

```mermaid
block-beta
    columns 2
    block:group1
        A["Component A"]
        B["Component B"]
    end
    C["External"]
```

### Nested Block with Span

Use `block:ID:SPAN` to create a nested group spanning multiple columns:

```mermaid
block-beta
    columns 3
    Header["Header"]:3
    block:services:2
        columns 2
        S1["Service 1"]
        S2["Service 2"]
    end
    Sidebar["Side"]
    Footer["Footer"]:3
```

### Complex Hierarchy

```mermaid
block-beta
    columns 4
    Title["System Overview"]:4
    block:frontend:2
        columns 2
        Web["Web App"]
        Mobile["Mobile App"]
    end
    block:backend:2
        columns 2
        API["API Server"]
        Worker["Workers"]
    end
    DB["Database"]:4
```

---

## Obsidian Notes

**Syntax Form**: Uses the `block-beta` keyword to start the diagram.

**Block Format**: Blocks can be defined in multiple ways:
- `ID` - Simple block using ID as label
- `ID["Label"]` - Block with custom label
- `ID:N` - Block spanning N columns
- `ID["Label"]:N` - Block with label and column span

**Shapes**: Use bracket notation for different shapes (see Block Shapes section).

**Styling**: Use `style ID` declarations with CSS-like properties separated by commas.

**Columns**: Define overall layout width with `columns N` at the start.

**Layout**: Blocks flow left-to-right, wrapping based on column count and spans.

**Connections**: Use `-->` for arrows and `---` for lines between blocks.

**Nesting**: Use `block:ID:SPAN ... end` for nested groups.

**Theme Compatibility**: Colors may vary with Obsidian themes. Use explicit hex values for consistent appearance.

**Code Block Format**:
````
```mermaid
block-beta
    columns 2
    A["Element"]:1
    B["Element"]:1
    A --> B
    style A fill:#color,stroke:#color,color:#textcolor
```
````

---

## Quick Reference Table

| Concept | Syntax | Example |
|---------|--------|---------|
| Diagram start | `block-beta` | `block-beta` |
| Columns | `columns N` | `columns 3` |
| Simple block | `ID` | `A` |
| Block with label | `ID["Label"]` | `A["Component"]` |
| Column span | `:N` suffix | `A:2` or `A["Big"]:2` |
| Arrow | `-->` | `A --> B` |
| Line | `---` | `A --- B` |
| Labeled arrow | `-- "text" -->` | `A -- "data" --> B` |
| Nested block | `block:ID:N ... end` | `block:group:2 ... end` |
| Space block | `space:N` | `space:1` |
| Style fill | `fill:#hex` | `fill:#e3f2fd` |
| Style stroke | `stroke:#hex` | `stroke:#1565c0` |
| Style text | `color:#hex` | `color:#0d47a1` |
| Apply style | `style ID prop:val` | `style A fill:#e3f2fd,stroke:#1565c0` |
