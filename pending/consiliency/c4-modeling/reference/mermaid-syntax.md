# Mermaid C4 Syntax Reference

Complete syntax reference for C4 diagrams in Mermaid.

## Diagram Types

```mermaid
C4Context    %% Level 1: Context
C4Container  %% Level 2: Container
C4Component  %% Level 3: Component
C4Dynamic    %% Sequence-style interactions
C4Deployment %% Deployment view
```

## Elements

### People

```mermaid
Person(id, "Label", "Description")
Person_Ext(id, "Label", "Description")  %% External person
```

### Systems

```mermaid
System(id, "Label", "Description")
System_Ext(id, "Label", "Description")  %% External system
System_Boundary(id, "Label") {
    %% Nested elements
}
```

### Containers

```mermaid
Container(id, "Label", "Technology", "Description")
ContainerDb(id, "Label", "Technology", "Description")     %% Database
ContainerQueue(id, "Label", "Technology", "Description")  %% Queue
Container_Ext(id, "Label", "Technology", "Description")   %% External
Container_Boundary(id, "Label") {
    %% Nested elements
}
```

### Components

```mermaid
Component(id, "Label", "Technology", "Description")
Component_Ext(id, "Label", "Technology", "Description")
```

### Boundaries

```mermaid
Enterprise_Boundary(id, "Label") {
    %% Group systems
}
System_Boundary(id, "Label") {
    %% Group containers
}
Container_Boundary(id, "Label") {
    %% Group components
}
```

## Relationships

### Basic Relationships

```mermaid
Rel(from, to, "Label")
Rel(from, to, "Label", "Technology")
```

### Directional

```mermaid
Rel(from, to, "Label")       %% Default: left to right
Rel_Back(from, to, "Label")  %% Right to left
Rel_Up(from, to, "Label")    %% Bottom to top
Rel_Down(from, to, "Label")  %% Top to bottom
```

### Bidirectional

```mermaid
BiRel(a, b, "Label")
```

## Complete Examples

### Context Diagram

```mermaid
C4Context
    title System Context Diagram - E-Commerce Platform

    Person(customer, "Customer", "A person who buys products")
    Person(admin, "Admin", "Manages products and orders")

    System(ecommerce, "E-Commerce Platform", "Allows customers to browse and purchase products")

    System_Ext(payment, "Payment Gateway", "Processes credit card payments")
    System_Ext(shipping, "Shipping Provider", "Handles delivery logistics")
    System_Ext(email, "Email Service", "Sends transactional emails")

    Rel(customer, ecommerce, "Browses, purchases", "HTTPS")
    Rel(admin, ecommerce, "Manages", "HTTPS")
    Rel(ecommerce, payment, "Processes payments", "HTTPS/API")
    Rel(ecommerce, shipping, "Creates shipments", "HTTPS/API")
    Rel(ecommerce, email, "Sends emails", "SMTP")
```

### Container Diagram

```mermaid
C4Container
    title Container Diagram - E-Commerce Platform

    Person(customer, "Customer", "Buys products")

    System_Boundary(ecommerce, "E-Commerce Platform") {
        Container(web, "Web Application", "React, TypeScript", "Product browsing and checkout UI")
        Container(mobile, "Mobile App", "React Native", "Mobile shopping experience")
        Container(api, "API Server", "Node.js, Express", "Business logic and REST API")
        Container(worker, "Background Worker", "Node.js", "Async job processing")
        ContainerDb(db, "Database", "PostgreSQL", "Product, order, user data")
        ContainerDb(cache, "Cache", "Redis", "Session and product cache")
        ContainerQueue(queue, "Message Queue", "RabbitMQ", "Job queue")
    }

    System_Ext(payment, "Payment Gateway", "Stripe")

    Rel(customer, web, "Uses", "HTTPS")
    Rel(customer, mobile, "Uses", "HTTPS")
    Rel(web, api, "Calls", "REST/JSON")
    Rel(mobile, api, "Calls", "REST/JSON")
    Rel(api, db, "Reads/Writes", "SQL")
    Rel(api, cache, "Reads/Writes", "Redis Protocol")
    Rel(api, queue, "Publishes", "AMQP")
    Rel(worker, queue, "Consumes", "AMQP")
    Rel(worker, db, "Reads/Writes", "SQL")
    Rel(api, payment, "Processes payments", "HTTPS")
```

### Component Diagram

```mermaid
C4Component
    title Component Diagram - API Server

    Container_Boundary(api, "API Server") {
        Component(routes, "Route Handlers", "Express Router", "HTTP request routing")
        Component(auth, "Auth Middleware", "Passport.js", "Authentication and authorization")
        Component(validation, "Validators", "Joi", "Request validation")
        Component(products, "Product Service", "TypeScript", "Product business logic")
        Component(orders, "Order Service", "TypeScript", "Order processing logic")
        Component(users, "User Service", "TypeScript", "User management")
        Component(productRepo, "Product Repository", "TypeScript", "Product data access")
        Component(orderRepo, "Order Repository", "TypeScript", "Order data access")
        Component(userRepo, "User Repository", "TypeScript", "User data access")
        Component(paymentClient, "Payment Client", "TypeScript", "Stripe integration")
    }

    ContainerDb(db, "Database", "PostgreSQL")
    System_Ext(payment, "Stripe", "Payment processing")

    Rel(routes, auth, "Uses")
    Rel(routes, validation, "Uses")
    Rel(routes, products, "Calls")
    Rel(routes, orders, "Calls")
    Rel(routes, users, "Calls")
    Rel(products, productRepo, "Uses")
    Rel(orders, orderRepo, "Uses")
    Rel(orders, paymentClient, "Calls")
    Rel(users, userRepo, "Uses")
    Rel(productRepo, db, "Queries")
    Rel(orderRepo, db, "Queries")
    Rel(userRepo, db, "Queries")
    Rel(paymentClient, payment, "HTTPS")
```

## Styling (Optional)

```mermaid
UpdateElementStyle(id, $bgColor="blue", $fontColor="white")
UpdateRelStyle(from, to, $textColor="red", $lineColor="red")
```

## Tips

1. **Use meaningful IDs**: `api` not `c1`
2. **Include technology**: `"Node.js, Express"` not just `"API"`
3. **Label relationships**: `"Calls"`, `"Reads/Writes"`, `"Publishes"`
4. **Group with boundaries**: Use `System_Boundary`, `Container_Boundary`
5. **Keep it simple**: If diagram is too complex, split into multiple

## Resources

- [Mermaid C4 Docs](https://mermaid.js.org/syntax/c4.html)
- [C4 Model](https://c4model.com/)
- [Structurizr](https://structurizr.com/)
