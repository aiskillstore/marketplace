# Class Diagram Reference

Complete guide for Mermaid class diagrams in Obsidian.

---

## Class Definition

### Basic Syntax

```mermaid
classDiagram
    class Animal
    class Dog
    Animal <|-- Dog
```

### Class with Label

```mermaid
classDiagram
    class UserService["User Service"]
    class DB["Database Connection"]
    UserService --> DB
```

---

## Members

### Attributes and Methods

- **Without `()`**: Attribute
- **With `()`**: Method

```mermaid
classDiagram
    class BankAccount {
        +String owner
        +BigDecimal balance
        +deposit(amount)
        +withdraw(amount) bool
    }
```

### Visibility Modifiers

| Symbol | Meaning | Description |
|--------|---------|-------------|
| `+` | Public | Accessible from anywhere |
| `-` | Private | Class internal only |
| `#` | Protected | Subclasses can access |
| `~` | Package | Same package only |

```mermaid
classDiagram
    class User {
        +String name
        -String password
        #int id
        ~String internalCode
        +getName() String
        -hashPassword() String
        #validate() bool
    }
```

### Method Classifiers

| Symbol | Meaning | Position |
|--------|---------|----------|
| `*` | Abstract | After `()` or return type |
| `$` | Static | After `()` or return type |

```mermaid
classDiagram
    class Shape {
        <<abstract>>
        +draw()*
        +getArea()* double
        +getInstance()$ Shape
    }
    class Circle {
        -double radius
        +draw()
        +getArea() double
    }
    Shape <|-- Circle
```

---

## Relationships

### Relationship Types

| Relation | Syntax | Meaning |
|----------|--------|---------|
| Inheritance | `<\|--` | Parent-child (extends) |
| Realization | `<\|..` | Interface implementation |
| Composition | `*--` | Strong containment (lifecycle bound) |
| Aggregation | `o--` | Weak containment (independent lifecycle) |
| Association | `-->` | Reference relationship |
| Dependency | `..>` | Uses relationship |
| Link (solid) | `--` | Simple connection |
| Link (dotted) | `..` | Weak connection |

### Inheritance

```mermaid
classDiagram
    Animal <|-- Dog
    Animal <|-- Cat
    Animal <|-- Bird

    class Animal {
        +String name
        +makeSound()
    }
    class Dog {
        +bark()
    }
    class Cat {
        +meow()
    }
```

### Interface Implementation

```mermaid
classDiagram
    class Flyable {
        <<interface>>
        +fly()
    }
    class Swimmable {
        <<interface>>
        +swim()
    }
    class Duck {
        +fly()
        +swim()
        +quack()
    }

    Flyable <|.. Duck
    Swimmable <|.. Duck
```

### Composition vs Aggregation

```mermaid
classDiagram
    class Car {
        +start()
    }
    class Engine {
        +run()
    }
    class Wheel {
        +rotate()
    }

    Car *-- Engine : contains
    Car o-- Wheel : has

    note for Car "Engine is destroyed with Car (composition)\nWheels can exist independently (aggregation)"
```

### Association and Dependency

```mermaid
classDiagram
    class Student {
        +enroll(Course c)
    }
    class Course {
        +String title
    }
    class Logger {
        +log(String msg)$
    }

    Student --> Course : enrolls in
    Student ..> Logger : uses
```

### With Labels

```mermaid
classDiagram
    Customer --> Order : places
    Order --> Product : contains
    Order ..> PaymentService : uses
```

---

## Multiplicity (Cardinality)

| Notation | Meaning |
|----------|---------|
| `1` | Exactly one |
| `0..1` | Zero or one |
| `1..*` | One or more |
| `*` | Zero or more |
| `n` | Exactly n |
| `0..n` | Zero to n |

```mermaid
classDiagram
    Customer "1" --> "*" Order : places
    Order "1" --> "1..*" OrderItem : contains
    OrderItem "*" --> "1" Product : references
```

```mermaid
classDiagram
    class Library
    class Book
    class Member

    Library "1" *-- "0..*" Book : owns
    Library "1" o-- "0..*" Member : has
    Member "0..*" --> "0..5" Book : borrows
```

---

## Generics

Use tilde `~` for generic types:

```mermaid
classDiagram
    class Stack~T~ {
        -T[] items
        +push(T item)
        +pop() T
        +peek() T
        +isEmpty() bool
    }
```

### Complex Generics

```mermaid
classDiagram
    class Map~K,V~ {
        +put(K key, V value)
        +get(K key) V
        +keys() List~K~
        +values() List~V~
    }
```

```mermaid
classDiagram
    class Repository~T~ {
        <<interface>>
        +save(T entity) T
        +findById(int id) T
        +findAll() List~T~
        +delete(T entity)
    }

    class UserRepository {
        +save(User entity) User
        +findById(int id) User
        +findByEmail(String email) User
    }

    Repository~T~ <|.. UserRepository
```

---

## Annotations

| Annotation | Use Case |
|------------|----------|
| `<<interface>>` | Interface |
| `<<abstract>>` | Abstract class |
| `<<enumeration>>` | Enum type |
| `<<service>>` | Service class |
| `<<entity>>` | Domain entity |
| `<<repository>>` | Data access |
| `<<controller>>` | Request handler |

```mermaid
classDiagram
    class UserService {
        <<service>>
        +createUser(User user) User
        +deleteUser(int id)
    }

    class UserRepository {
        <<repository>>
        +save(User user)
        +findById(int id) User
    }

    class User {
        <<entity>>
        +int id
        +String name
        +String email
    }

    class UserStatus {
        <<enumeration>>
        ACTIVE
        INACTIVE
        PENDING
    }

    UserService --> UserRepository
    UserRepository --> User
    User --> UserStatus
```

---

## Namespaces

Group related classes:

```mermaid
classDiagram
    namespace Domain {
        class User {
            +String name
        }
        class Order {
            +int orderId
        }
    }

    namespace Infrastructure {
        class UserRepository {
            +save(User user)
        }
        class OrderRepository {
            +save(Order order)
        }
    }

    UserRepository --> User
    OrderRepository --> Order
```

---

## Direction

| Value | Direction |
|-------|-----------|
| `TB` | Top to Bottom |
| `BT` | Bottom to Top |
| `LR` | Left to Right |
| `RL` | Right to Left |

```mermaid
classDiagram
    direction LR

    class Client
    class Service
    class Repository
    class Database

    Client --> Service
    Service --> Repository
    Repository --> Database
```

---

## Notes

```mermaid
classDiagram
    class User {
        +String name
        +String email
    }

    note for User "Core domain entity\nContains all user info"
```

---

## Styling

### Class Definition (classDef)

```mermaid
classDiagram
    class Service {
        +execute()
    }
    class Repository {
        +save()
    }
    class Entity {
        +id
    }

    classDef serviceClass fill:#4dabf7,stroke:#1864ab,color:#fff
    classDef repoClass fill:#69db7c,stroke:#2f9e44,color:#fff
    classDef entityClass fill:#ffd43b,stroke:#fab005,color:#000

    class Service:::serviceClass
    class Repository:::repoClass
    class Entity:::entityClass
```

### Inline Style

```mermaid
classDiagram
    class Important {
        +criticalMethod()
    }

    style Important fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
```

---

## Practical Examples

### Example 1: Strategy Pattern

```mermaid
classDiagram
    direction LR

    class PaymentContext {
        -PaymentStrategy strategy
        +setStrategy(PaymentStrategy s)
        +executePayment(amount) bool
    }

    class PaymentStrategy {
        <<interface>>
        +pay(amount) bool
    }

    class CreditCardPayment {
        -String cardNumber
        -String expiry
        +pay(amount) bool
    }

    class PayPalPayment {
        -String email
        +pay(amount) bool
    }

    class BankTransfer {
        -String accountNumber
        +pay(amount) bool
    }

    PaymentContext o-- PaymentStrategy
    PaymentStrategy <|.. CreditCardPayment
    PaymentStrategy <|.. PayPalPayment
    PaymentStrategy <|.. BankTransfer

    note for PaymentStrategy "Strategy pattern allows\nruntime algorithm selection"
```

### Example 2: Repository Pattern with Generics

```mermaid
classDiagram
    class IRepository~T~ {
        <<interface>>
        +save(T entity) T
        +findById(int id) T
        +findAll() List~T~
        +delete(T entity)
    }

    class AbstractRepository~T~ {
        <<abstract>>
        #EntityManager em
        +save(T entity) T
        +findById(int id) T
        +findAll() List~T~
    }

    class UserRepository {
        +save(User) User
        +findById(int id) User
        +findByEmail(String email) User
    }

    class ProductRepository {
        +save(Product) Product
        +findById(int id) Product
        +findByCategory(String cat) List~Product~
    }

    IRepository~T~ <|.. AbstractRepository~T~
    AbstractRepository~T~ <|-- UserRepository
    AbstractRepository~T~ <|-- ProductRepository
```

### Example 3: E-Commerce Domain Model

```mermaid
classDiagram
    class User {
        <<entity>>
        -int id
        -String username
        -String email
        +register()
        +login()
    }

    class Order {
        <<entity>>
        -int orderId
        -Date orderDate
        -OrderStatus status
        +calculateTotal() BigDecimal
        +updateStatus(OrderStatus s)
    }

    class OrderItem {
        <<entity>>
        -int quantity
        -BigDecimal unitPrice
        +getSubtotal() BigDecimal
    }

    class Product {
        <<entity>>
        -int productId
        -String name
        -BigDecimal price
        -int stock
        +updateStock(int qty)
    }

    class OrderStatus {
        <<enumeration>>
        PENDING
        CONFIRMED
        SHIPPED
        DELIVERED
        CANCELLED
    }

    User "1" --> "*" Order : places
    Order "1" *-- "1..*" OrderItem : contains
    OrderItem "*" --> "1" Product : references
    Order --> OrderStatus : has

    classDef entity fill:#e3f2fd,stroke:#1565c0
    class User,Order,OrderItem,Product entity
```

### Example 4: Layered Architecture

```mermaid
classDiagram
    direction TB

    namespace Presentation {
        class UserController {
            <<controller>>
            -UserService userService
            +getUser(int id) Response
            +createUser(UserDTO dto) Response
        }
    }

    namespace Application {
        class UserService {
            <<service>>
            -UserRepository userRepo
            -PasswordEncoder encoder
            +getUser(int id) User
            +createUser(UserDTO dto) User
        }
    }

    namespace Domain {
        class User {
            <<entity>>
            -int id
            -String name
            -String email
        }
    }

    namespace Infrastructure {
        class UserRepositoryImpl {
            <<repository>>
            -EntityManager em
            +save(User user) User
            +findById(int id) User
        }
    }

    UserController --> UserService : uses
    UserService --> UserRepositoryImpl : uses
    UserRepositoryImpl --> User : manages
```

### Example 5: State Pattern

```mermaid
classDiagram
    class Document {
        -DocumentState state
        +publish()
        +archive()
        +restore()
    }

    class DocumentState {
        <<abstract>>
        +publish(Document doc)*
        +archive(Document doc)*
        +restore(Document doc)*
    }

    class DraftState {
        +publish(Document doc)
        +archive(Document doc)
        +restore(Document doc)
    }

    class PublishedState {
        +publish(Document doc)
        +archive(Document doc)
        +restore(Document doc)
    }

    class ArchivedState {
        +publish(Document doc)
        +archive(Document doc)
        +restore(Document doc)
    }

    Document o-- DocumentState
    DocumentState <|-- DraftState
    DocumentState <|-- PublishedState
    DocumentState <|-- ArchivedState

    note for Document "State pattern for\ndocument lifecycle"
```

---

## Obsidian Notes

**Theme Compatibility**: Colors adapt to Obsidian theme. Use explicit `classDef` for consistent appearance.

**Performance**: Large diagrams (30+ classes) may slow rendering. Split into multiple diagrams.

**Export**: PDF export renders as images. Capture as PNG/SVG for external sharing.

**Generics**: Use tilde `~T~`, not angle brackets `<T>`. Generic part is not part of class name when referencing.

**Special Characters**: Wrap labels with special characters in quotes.

**Code Block Format**:
````
```mermaid
classDiagram
    class Animal {
        +name: String
    }
```
````

---

## Quick Reference Table

| Category | Syntax | Example |
|----------|--------|---------|
| Class | `class Name` | `class User` |
| Label | `class Id["Label"]` | `class U["User Service"]` |
| Attribute | `+Type name` | `+String name` |
| Method | `+method() ReturnType` | `+getName() String` |
| Public | `+` | `+name` |
| Private | `-` | `-password` |
| Protected | `#` | `#id` |
| Package | `~` | `~internal` |
| Abstract | `*` | `+draw()*` |
| Static | `$` | `+getInstance()$` |
| Inheritance | `<\|--` | `Animal <\|-- Dog` |
| Implementation | `<\|..` | `Interface <\|.. Class` |
| Composition | `*--` | `Car *-- Engine` |
| Aggregation | `o--` | `Dept o-- Employee` |
| Association | `-->` | `Student --> Course` |
| Dependency | `..>` | `Client ..> Service` |
| Multiplicity | `"1" --> "*"` | `User "1" --> "*" Order` |
| Generic | `~T~` | `class Stack~T~` |
| Interface | `<<interface>>` | `<<interface>>` |
| Abstract class | `<<abstract>>` | `<<abstract>>` |
| Direction | `direction DIR` | `direction LR` |
| Note | `note for Class` | `note for User "text"` |
| Style | `classDef name` | `classDef red fill:#f00` |
| Apply style | `:::class` | `User:::red` |
