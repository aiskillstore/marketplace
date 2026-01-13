# Entity Relationship Diagram Reference

Complete guide for Mermaid ER diagrams in Obsidian.

---

## Entity Definition

### Basic Entity

Define an entity by name only:

```mermaid
erDiagram
    CUSTOMER
    ORDER
```

### Entity with Attributes

Define properties using type-name pairs within braces:

```mermaid
erDiagram
    CUSTOMER {
        int id PK
        string name
        string email UK
        string phone
    }
```

### Attribute Modifiers

| Modifier | Meaning | Example |
|----------|---------|---------|
| `PK` | Primary Key | `int id PK` |
| `FK` | Foreign Key | `int customer_id FK` |
| `UK` | Unique Key | `string email UK` |
| `PK, FK` | Composite Key | `string order_id PK, FK` |
| (none) | Regular attribute | `string phone` |

### Attribute Comments

Add descriptions in double quotes at the end of an attribute:

```mermaid
erDiagram
    PERSON {
        string driversLicense PK "The license number"
        string(99) firstName "Max 99 characters"
        string lastName
        int age
    }
```

### Advanced Attribute Types

| Type | Example | Description |
|------|---------|-------------|
| `string(n)` | `string(99) name` | Length-limited string |
| `type[]` | `string[] tags` | Array type |

### Entity Aliases

Display alternative names in square brackets:

```mermaid
erDiagram
    CUSTOMER [Client] {
        int id PK
        string name
    }
```

---

## Relationships and Cardinality

### Relationship Syntax

Basic format: `ENTITY1 RELATION ENTITY2 : LABEL`

### Cardinality Notation (Crow's Foot)

| Left Symbol | Right Symbol | Meaning |
|-------------|--------------|---------|
| `\|o` | `o\|` | Zero or one |
| `\|\|` | `\|\|` | Exactly one |
| `}o` | `o{` | Zero or more |
| `}\|` | `\|{` | One or more |

**Note:** The outermost character represents the maximum value, and the innermost character represents the minimum value.

### Cardinality Aliases

Mermaid also accepts text-based aliases instead of symbols:

| Alias | Equivalent Symbol |
|-------|-------------------|
| `zero or one`, `one or zero` | `\|o` / `o\|` |
| `only one`, `1` | `\|\|` |
| `zero or more`, `zero or many`, `many(0)`, `0+` | `}o` / `o{` |
| `one or more`, `one or many`, `many(1)`, `1+` | `}\|` / `\|{` |

Example using aliases:

```mermaid
erDiagram
    CAR 1 to zero or more NAMED-DRIVER : allows
    PERSON many(0) optionally to 0+ NAMED-DRIVER : is
```

### Identifying vs. Non-Identifying

- `--` (solid line): Identifying relationship
- `..` (dashed line): Non-identifying relationship

### Relationship Examples

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER ||--o{ INVOICE : receives
```

**Reading examples:**
- `CUSTOMER ||--o{ ORDER` → A customer places zero or more orders
- `ORDER ||--|{ LINE-ITEM` → An order contains one or more line items

---

## Complete Attribute Types

| Type | Example | Use Case |
|------|---------|----------|
| `int` | `int id` | Integer numbers |
| `string` | `string name` | Text |
| `float` | `float price` | Decimal numbers |
| `bool` | `bool active` | True/false values |
| `date` | `date created_at` | Date values |
| `text` | `text description` | Long text |

---

## Direction

Control diagram layout direction:

```mermaid
erDiagram
    direction LR
    CUSTOMER {
        int id PK
        string name
    }
    ORDER {
        int id PK
        int customer_id FK
    }
    CUSTOMER ||--o{ ORDER : places
```

| Direction | Layout |
|-----------|--------|
| `TB` | Top to Bottom (default) |
| `BT` | Bottom to Top |
| `LR` | Left to Right |
| `RL` | Right to Left |

---

## Practical Examples

### Example 1: E-Commerce Database

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER ||--o{ REVIEW : writes
    ORDER ||--|{ LINE-ITEM : contains
    LINE-ITEM }o--|| PRODUCT : contains
    PRODUCT ||--o{ REVIEW : receives
    PRODUCT }o--|| CATEGORY : in

    CUSTOMER {
        int customer_id PK
        string email UK
        string name
        string phone
        string address
        date created_at
    }

    PRODUCT {
        int product_id PK
        string name
        float price
        int stock_qty
        string description
        int category_id FK
    }

    ORDER {
        int order_id PK
        int customer_id FK
        date order_date
        float total_amount
        string status
    }

    LINE-ITEM {
        int line_item_id PK
        int order_id FK
        int product_id FK
        int quantity
        float unit_price
    }

    CATEGORY {
        int category_id PK
        string name
        string description
    }

    REVIEW {
        int review_id PK
        int customer_id FK
        int product_id FK
        int rating
        string comment
        date created_at
    }
```

### Example 2: Social Media Platform

```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    USER ||--o{ LIKE : gives
    POST ||--o{ COMMENT : has
    POST ||--o{ LIKE : receives
    USER }o--o{ USER : follows

    USER {
        int user_id PK
        string username UK
        string email UK
        string display_name
        text bio
        string profile_image_url
        date created_at
        date last_login
    }

    POST {
        int post_id PK
        int user_id FK
        text content
        string image_url
        int like_count
        int comment_count
        date created_at
        date updated_at
    }

    COMMENT {
        int comment_id PK
        int post_id FK
        int user_id FK
        text content
        int like_count
        date created_at
    }

    LIKE {
        int like_id PK
        int user_id FK
        int post_id FK
        date created_at
    }
```

### Example 3: University Management System

```mermaid
erDiagram
    STUDENT ||--o{ ENROLLMENT : takes
    COURSE ||--o{ ENROLLMENT : enrolls
    DEPARTMENT ||--o{ COURSE : offers
    DEPARTMENT ||--o{ STUDENT : has
    INSTRUCTOR ||--o{ COURSE : teaches
    STUDENT }o--|| DEPARTMENT : majors_in

    STUDENT {
        int student_id PK
        string student_number UK
        string first_name
        string last_name
        string email UK
        int department_id FK
        date enrollment_date
        string status
    }

    COURSE {
        int course_id PK
        string course_code UK
        string title
        int credits
        int department_id FK
        int instructor_id FK
        int max_capacity
    }

    INSTRUCTOR {
        int instructor_id PK
        string employee_id UK
        string first_name
        string last_name
        string email
        string office_location
        int department_id FK
    }

    DEPARTMENT {
        int department_id PK
        string name UK
        string code UK
        string building
        string phone
    }

    ENROLLMENT {
        int enrollment_id PK
        int student_id FK
        int course_id FK
        string grade
        int attendance_count
        date enrollment_date
    }
```

---

## Styling

### Using classDef and Style Classes

Define style classes with `classDef` and apply them using the `:::` operator:

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places

    CUSTOMER {
        int id PK
        string name
    }

    ORDER {
        int id PK
        int customer_id FK
    }

    classDef highlight fill:#e3f2fd,stroke:#1565c0
    CUSTOMER:::highlight
```

### Multiple Style Classes

```mermaid
erDiagram
    direction LR
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ INVOICE : generates

    CUSTOMER {
        int id PK
        string name
    }

    ORDER {
        int id PK
        int customer_id FK
    }

    INVOICE {
        int id PK
        int order_id FK
    }

    classDef green fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef blue fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    classDef orange fill:#ffe0b2,stroke:#e65100,stroke-width:2px

    CUSTOMER:::green
    ORDER:::blue
    INVOICE:::orange
```

---

## Advanced Features

### Comments

```mermaid
erDiagram
    %% Core entities
    CUSTOMER ||--o{ ORDER : places

    %% Customer information
    CUSTOMER {
        int id PK
        string name
        string email UK
    }

    %% Order details
    ORDER {
        int id PK
        int customer_id FK
    }
```

### Multiple Relationships

Entities can have multiple relationships:

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER ||--o{ INVOICE : receives
    CUSTOMER ||--o{ SUPPORT-TICKET : creates
    ORDER ||--|{ INVOICE : generates
    SUPPORT-TICKET }o--|| ORDER : references
```

### Circular Relationships

```mermaid
erDiagram
    EMPLOYEE }o--|| EMPLOYEE : "reports to"

    EMPLOYEE {
        int employee_id PK
        string name
        int manager_id FK
    }
```

---

## Obsidian Notes

**Theme Compatibility**: ER diagram colors may vary with Obsidian themes. Use explicit styles for consistent appearance.

**Complex Diagrams**: Large ER diagrams (15+ entities) may slow rendering. Consider splitting by domain or layer.

**Export**: PDF export renders diagrams as images. For external sharing, capture as PNG/SVG.

**Primary Keys**: Always clearly mark primary keys with `PK` for data integrity visualization.

**Code Block Format**:
````
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
```
````

---

## Quick Reference Table

| Concept | Syntax | Example |
|---------|--------|---------|
| Entity | `ENTITY_NAME` | `CUSTOMER` |
| Attribute | `type name [MODIFIER]` | `int id PK` |
| Primary Key | `PK` suffix | `int id PK` |
| Foreign Key | `FK` suffix | `int customer_id FK` |
| Unique Key | `UK` suffix | `string email UK` |
| Composite Key | `PK, FK` suffix | `string id PK, FK` |
| Attribute Comment | `"comment"` suffix | `string name "Required"` |
| Zero or one | `\|o` / `o\|` | `CUSTOMER \|o--\|\| ADDRESS` |
| Exactly one | `\|\|` | `CUSTOMER \|\|--\|\| PROFILE` |
| Zero or more | `}o` / `o{` | `CUSTOMER }o--o{ ORDER` |
| One or more | `}\|` / `\|{` | `ORDER }\|--\|{ LINE-ITEM` |
| Identifying | `--` | `CUSTOMER--ORDER` |
| Non-identifying | `..` | `CUSTOMER..ORDER` |
| Relationship | `ENTITY1 REL ENTITY2 : label` | `CUSTOMER \|\|--o{ ORDER : places` |
| Alias | `[alias]` | `CUSTOMER [Client]` |
| Direction | `direction DIR` | `direction LR` |
| Style Class | `classDef name props` | `classDef highlight fill:#f0f` |
| Apply Style | `ENTITY:::class` | `CUSTOMER:::highlight` |
