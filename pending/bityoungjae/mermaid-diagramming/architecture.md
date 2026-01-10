# Architecture Diagram Reference

Complete guide for Mermaid architecture diagrams in Obsidian. Architecture diagrams visualize relationships between services and resources commonly found in cloud deployments and distributed systems.

---

## Overview

Architecture diagrams (architecture-beta) show how services connect and interact within logical groups. They excel at depicting cloud infrastructure, microservices systems, and CI/CD pipelines with visual clarity.

**Best for:**
- Cloud architecture and infrastructure
- Microservices and service relationships
- CI/CD pipeline visualization
- Distributed system design

```mermaid
architecture-beta
    group Cloud(cloud)[Cloud Infrastructure]
    service web(server)[Web Server] in Cloud
    service api(server)[API Server] in Cloud
    service db(database)[Database]

    web:R --> L:api
    api:R --> L:db
```

---

## Basic Syntax

### Structure

```
architecture-beta
    group {id}({icon})[{label}]
    service {id}({icon})[{label}] (in {parent})?

    {service1}:{position} {arrow} {position}:{service2}
```

### Groups

Organize related services together using the `in` keyword:

```mermaid
architecture-beta
    group Frontend(server)[Web Tier]
    service ui(server)[User Interface] in Frontend
    service router(server)[Router] in Frontend

    group Backend(server)[API Tier]
    service auth(server)[Auth Service] in Backend
    service api(server)[API Service] in Backend
```

### Services

Individual components, either standalone or within groups:

```mermaid
architecture-beta
    service client(internet)[Client]
    service gateway(server)[API Gateway]
    service database(database)[Database]
```

---

## Available Icons

| Icon | Syntax | Use Case |
|------|--------|----------|
| Server | `server` | General compute |
| Database | `database` | Data storage |
| Cloud | `cloud` | Cloud service |
| Disk | `disk` | Storage volume |
| Internet | `internet` | External/public |

---

## Connections & Edges

### Edge Syntax

```
{serviceId}:{position} {arrow} {position}:{serviceId}
```

### Position Codes

- `L` - Left side
- `R` - Right side
- `T` - Top side
- `B` - Bottom side

### Arrow Types

| Arrow | Description |
|-------|-------------|
| `--` | Bidirectional connection (no arrows) |
| `<-->` | Bidirectional connection with arrows |
| `-->` | Right-pointing arrow |
| `<--` | Left-pointing arrow |

### Edge Labels

Add labels to edges using bracket syntax:

```
{service1}:{position} -[Label]- {position}:{service2}
```

Example:
```mermaid
architecture-beta
    service client(internet)[Client]
    service server(server)[Server]

    client:R -[HTTP]- L:server
```

### Connection Examples

```mermaid
architecture-beta
    service client(internet)[Client]
    service server(server)[Server]
    service db(database)[Database]

    client:R --> L:server
    server:B --> T:db
```

---

## Practical Examples

### Example 1: Three-Tier Architecture

```mermaid
architecture-beta
    group Web(server)[Web Tier]
    service web1(server)[Web Server 1] in Web
    service web2(server)[Web Server 2] in Web

    group App(server)[App Tier]
    service app1(server)[App Server 1] in App
    service app2(server)[App Server 2] in App

    group Data(database)[Data Tier]
    service primary(database)[Primary DB] in Data
    service replica(database)[Replica DB] in Data

    web1:B --> T:app1
    web2:B --> T:app2
    app1:B --> T:primary
    app2:B --> T:replica
    primary:R --> L:replica
```

### Example 2: Microservices Architecture

```mermaid
architecture-beta
    service client(internet)[Client]
    service cdn(cloud)[CDN]

    group Services(server)[Microservices]
    service auth(server)[Auth Service] in Services
    service user(server)[User Service] in Services
    service order(server)[Order Service] in Services
    service payment(server)[Payment Service] in Services

    group Data(database)[Data Layer]
    service authdb(database)[Auth DB] in Data
    service userdb(database)[User DB] in Data
    service orderdb(database)[Order DB] in Data

    service cache(disk)[Redis Cache]
    service queue(disk)[Message Queue]

    client:R --> L:cdn
    cdn:R --> L:auth
    auth:B --> T:authdb
    user:B --> T:userdb
    order:B --> T:orderdb
    auth:R --> L:user
    user:R --> L:order
    order:R --> L:payment
    user:R --> L:cache
    order:R --> L:queue
```

### Example 3: Multi-Environment Deployment

```mermaid
architecture-beta
    group Dev(server)[Development]
    service devweb(server)[Web] in Dev
    service devapi(server)[API] in Dev
    service devdb(database)[Database] in Dev

    group Stage(server)[Staging]
    service stageweb(server)[Web] in Stage
    service stageapi(server)[API] in Stage
    service stagedb(database)[Database] in Stage

    group Prod(server)[Production]
    service prodweb(server)[Web] in Prod
    service prodapi(server)[API] in Prod
    service proddb(database)[Database] in Prod

    devweb:R --> L:devapi
    devapi:B --> T:devdb

    stageweb:R --> L:stageapi
    stageapi:B --> T:stagedb

    prodweb:R --> L:prodapi
    prodapi:B --> T:proddb
```

### Example 4: Event-Driven System

```mermaid
architecture-beta
    service producer(server)[Event Producer]

    group EventInfra(server)[Event Infrastructure]
    service eventbus(disk)[Event Bus] in EventInfra
    service processor(server)[Processor] in EventInfra

    group Consumers(server)[Event Consumers]
    service analytics(server)[Analytics] in Consumers
    service notification(server)[Notification] in Consumers
    service reporting(server)[Reporting] in Consumers

    service storage(database)[Event Store]

    producer:R --> L:eventbus
    eventbus:R --> L:processor
    processor:R --> L:analytics
    processor:R --> L:notification
    processor:R --> L:reporting
    processor:B --> T:storage
```

### Example 5: API Gateway Pattern

```mermaid
architecture-beta
    service client(internet)[Client]
    service lb(cloud)[Load Balancer]

    group Gateway(server)[API Gateway Tier]
    service gw1(server)[Gateway 1] in Gateway
    service gw2(server)[Gateway 2] in Gateway

    group Services(server)[Backend Services]
    service users(server)[User Service] in Services
    service orders(server)[Order Service] in Services
    service products(server)[Product Service] in Services

    group Cache(server)[Cache Layer]
    service redis(disk)[Redis] in Cache

    client:R --> L:lb
    lb:R --> L:gw1
    lb:R --> L:gw2

    gw1:B --> T:users
    gw1:B --> T:orders
    gw1:B --> T:products

    gw2:B --> T:users
    gw2:B --> T:orders
    gw2:B --> T:products

    users:R --> L:redis
    orders:R --> L:redis
    products:R --> L:redis
```

---

## Advanced Features

### Nested Groups

Create hierarchical organization using the `in` keyword:

```mermaid
architecture-beta
    group Cloud(cloud)[Cloud]
    group Compute(server)[Compute Resources] in Cloud
    service web(server)[Web] in Compute
    service app(server)[App] in Compute

    group Storage(database)[Storage] in Cloud
    service db(database)[Database] in Storage
    service cache(disk)[Cache] in Storage

    web:R --> L:app
    app:B --> T:db
    app:R --> L:cache
```

### Group-Level Edges

Connect edges to groups themselves using the `{group}` modifier:

```mermaid
architecture-beta
    group frontend(server)[Frontend]
    service web(server)[Web Server] in frontend

    group backend(server)[Backend]
    service api(server)[API Server] in backend

    frontend{group}:R --> L:backend{group}
```

This creates connections between the group boundaries rather than individual services.

### Direction Flow

Vertical and horizontal arrangement:

```mermaid
architecture-beta
    service top(server)[Top Layer]

    group Middle(server)[Middle Tier]
    service left(server)[Left] in Middle
    service right(server)[Right] in Middle

    service bottom(database)[Bottom Layer]

    top:B --> T:left
    top:B --> T:right
    left:B --> T:bottom
    right:B --> T:bottom
```

---

## Obsidian Notes

**Syntax Form**: Uses `architecture-beta` keyword (not `architecture`). This is the version supported in Obsidian's embedded Mermaid library.

**Format Requirements:**
- Groups: `group {id}({icon})[{label}]`
- Services: `service {id}({icon})[{label}]`
- Nesting: Use `in {parent_id}` to place services/groups inside parent groups
- Connections: `{id1}:{position} {arrow} {position}:{id2}`
- Positions: T (top), B (bottom), L (left), R (right)

**Icons**: Choose from: `server`, `database`, `cloud`, `disk`, `internet`

**Layout**: Services flow based on connection definitions. Parent groups organize visually related components. Order of definition affects layout.

**Theme Compatibility**: Colors adapt to Obsidian theme. Services show with consistent styling.

**Code Block Format**:
````
```mermaid
architecture-beta
    group MyGroup(server)[Group Name]
    service svc1(server)[Service 1] in MyGroup
    service svc2(server)[Service 2]

    svc1:R --> L:svc2
```
````

---

## Quick Reference Table

| Concept | Syntax | Example |
|---------|--------|---------|
| Diagram start | `architecture-beta` | `architecture-beta` |
| Group definition | `group {id}({icon})[{label}]` | `group api(server)[API]` |
| Service definition | `service {id}({icon})[{label}]` | `service web(server)[Web]` |
| Nesting | `in {parent_id}` | `service svc(server)[S] in api` |
| Connection | `{id1}:{pos} {arrow} {pos}:{id2}` | `web:R --> L:api` |
| Left position | `L` | Left side |
| Right position | `R` | Right side |
| Top position | `T` | Top side |
| Bottom position | `B` | Bottom side |
| Arrow right | `-->` | Right-pointing |
| Arrow left | `<--` | Left-pointing |
| Bidirectional (no arrows) | `--` | Connection without arrows |
| Bidirectional (with arrows) | `<-->` | Connection with arrows |
| Edge label | `-[Label]-` | `web:R -[HTTP]- L:api` |
| Group edge modifier | `{group}` | `api{group}:R --> L:db{group}` |
| Server icon | `server` | Compute resource |
| Database icon | `database` | Data storage |
| Cloud icon | `cloud` | Cloud service |
| Disk icon | `disk` | Storage |
| Internet icon | `internet` | External/public |
