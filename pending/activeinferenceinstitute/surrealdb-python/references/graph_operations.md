# SurrealDB Graph Operations Reference

## Overview

SurrealDB provides native graph database capabilities, allowing efficient relationship traversal without SQL JOINs. Relationships are stored in separate edge tables with mandatory `in` and `out` fields that specify the direction of relationships.

## The RELATE Statement

### Basic Syntax

```sql
RELATE [ ONLY ] @from_record -> @table -> @to_record
    [ CONTENT @value | SET @field = @value ... ]
    [ RETURN NONE | RETURN BEFORE | RETURN AFTER | RETURN DIFF ]
    [ TIMEOUT @duration ];
```

### Creating Simple Relationships

```python
# Create entities first
await db.create("person:aristotle", {"name": "Aristotle"})
await db.create("article:on_sleep", {"title": "On Sleep and Sleeplessness"})

# Create relationship
await db.query("""
    RELATE person:aristotle->wrote->article:on_sleep
""")
```

### Adding Metadata to Relationships

Relationships can store additional data alongside the connection:

```python
await db.query("""
    RELATE person:aristotle->wrote->article:on_sleep
    SET metadata.time_written = time::now(),
        metadata.location = "Ancient Greece"
""")
```

### Array Relationships

When arrays are involved, multiple relationships are automatically created:

```python
# Create multiple people and articles
await db.query("""
    CREATE person:p1 SET name = "Alice";
    CREATE person:p2 SET name = "Bob";
    CREATE article:a1 SET title = "Article 1";
    CREATE article:a2 SET title = "Article 2";
""")

# Create relationships between arrays (creates 4 relationships: p1->a1, p1->a2, p2->a1, p2->a2)
await db.query("""
    RELATE [person:p1, person:p2]->[wrote]->[article:a1, article:a2]
""")
```

## Graph Traversal

### Unidirectional Traversal

```python
# Traverse from person to articles they wrote
result = await db.query("""
    SELECT ->wrote->article FROM person:aristotle
""")

# Multiple hops
result = await db.query("""
    SELECT ->wrote->article->cited_by->article FROM person:aristotle
""")
```

### Bidirectional Traversal

```python
# Find sister cities (both directions)
result = await db.query("""
    SELECT id, <->sister_of<->city AS sister_cities FROM city
""")
```

### Recursive Graph Queries

Introduced in v2.1.0, use `@.{depth}` syntax for recursive traversal:

```python
# Find cities 3 hops away
result = await db.query("""
    SELECT @.{3}->connected_to->city AS cities_3_hops_away
    FROM city:1
""")

# Variable depth traversal
result = await db.query("""
    SELECT @.{1,5}->connected_to->city AS nearby_cities
    FROM city:1
""")
```

## Advanced Graph Features

### Graph Clauses (v2.2.0+)

Apply SELECT clauses within graph queries for sophisticated filtering:

```python
# Filter during traversal
result = await db.query("""
    SELECT ->knows->(person WHERE age > 25)->friend AS adult_friends
    FROM person:john
""")
```

### Range Syntax on Edges (v2.3.0+)

Navigate specific relationship sequences:

```python
# Get 2nd through 4th liked persons
result = await db.query("""
    SELECT ->likes:2..=4->person AS liked_people
    FROM person:john
""")
```

## Edge Tables

### Structure

Edge tables are automatically created and contain:
- `id`: The edge record ID
- `in`: The incoming record ID
- `out`: The outgoing record ID
- Any additional metadata fields

### Querying Edge Tables

```python
# Query the edge table directly
edges = await db.query("""
    SELECT * FROM wrote
    WHERE metadata.time_written > time::now() - 1y
""")
```

### Updating Edge Data

```python
# Update relationship metadata
await db.query("""
    UPDATE wrote:edge_id
    SET metadata.verified = true
""")
```

## Schema Definition for Graphs

### Enforcing Relationship Types

```python
# Define schema for person table
await db.query("""
    DEFINE TABLE person SCHEMAFULL;
    DEFINE FIELD name ON TABLE person TYPE string;
    DEFINE FIELD age ON TABLE person TYPE int;
""")

# Define schema for edge table with constraints
await db.query("""
    DEFINE TABLE wrote SCHEMAFULL;
    DEFINE FIELD in ON TABLE wrote TYPE record<person>;
    DEFINE FIELD out ON TABLE wrote TYPE record<article>;
    DEFINE FIELD metadata ON TABLE wrote TYPE object;
""")
```

### Unique Relationships

Prevent duplicate relationships with unique indexes:

```python
await db.query("""
    DEFINE INDEX unique_wrote ON TABLE wrote COLUMNS in, out UNIQUE;
""")
```

### Referential Integrity (v2.2.0+)

Use assertions to enforce referential integrity:

```python
await db.query("""
    DEFINE TABLE wrote SCHEMAFULL;
    DEFINE FIELD in ON TABLE wrote TYPE record<person>
        ASSERT $value != NONE;
    DEFINE FIELD out ON TABLE wrote TYPE record<article>
        ASSERT $value != NONE;
""")
```

## Common Graph Patterns

### Social Network

```python
# Create social network
await db.query("""
    CREATE person:alice SET name = "Alice";
    CREATE person:bob SET name = "Bob";
    CREATE person:carol SET name = "Carol";

    RELATE person:alice->follows->person:bob;
    RELATE person:bob->follows->person:carol;
    RELATE person:carol->follows->person:alice;
""")

# Find friends of friends
result = await db.query("""
    SELECT ->follows->person->follows->person AS friends_of_friends
    FROM person:alice
""")
```

### Recommendation System

```python
# Users and their liked items
await db.query("""
    RELATE user:u1->likes->item:i1 SET rating = 5;
    RELATE user:u1->likes->item:i2 SET rating = 4;
    RELATE user:u2->likes->item:i2 SET rating = 5;
""")

# Find items liked by users with similar taste
result = await db.query("""
    SELECT ->likes->item<-likes<-user->likes->item AS recommendations
    FROM user:u1
    WHERE recommendations.id NOT IN (
        SELECT ->likes->item.id FROM user:u1
    )
""")
```

### Knowledge Graph

```python
# Create knowledge entities and relationships
await db.query("""
    CREATE concept:ai SET name = "Artificial Intelligence";
    CREATE concept:ml SET name = "Machine Learning";
    CREATE concept:dl SET name = "Deep Learning";

    RELATE concept:dl->is_subset_of->concept:ml;
    RELATE concept:ml->is_subset_of->concept:ai;
""")

# Traverse hierarchy
result = await db.query("""
    SELECT @.{1,}->is_subset_of->concept AS parent_concepts
    FROM concept:dl
""")
```

## Performance Optimization

### Use Indexes

```python
# Index frequently queried relationship fields
await db.query("""
    DEFINE INDEX wrote_time ON TABLE wrote COLUMNS metadata.time_written;
""")
```

### Limit Traversal Depth

```python
# Use timeouts for complex queries
result = await db.query("""
    SELECT @.{1,10}->connected_to->city
    FROM city:1
    TIMEOUT 5s
""")
```

### Fetch Optimization

```python
# Use FETCH to eagerly load related records
result = await db.query("""
    SELECT *, ->wrote->article AS articles
    FROM person
    FETCH articles
""")
```

## Best Practices

1. **Define schemas** for both entity and edge tables to enforce data integrity
2. **Create unique indexes** on edge tables to prevent duplicate relationships
3. **Use assertions** for referential integrity on `in`/`out` fields
4. **Add timeouts** to recursive queries to prevent excessive computation
5. **Leverage graph clauses** for filtering during traversal instead of post-processing
6. **Store metadata** in edge tables when relationships have properties
7. **Use FETCH** to optimize queries that need related record data
8. **Index edge properties** that are frequently queried
