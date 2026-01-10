---
name: surrealdb-python
description: Master SurrealDB 2.3.x with Python for multi-model database operations including CRUD, graph relationships, vector search, and real-time queries. Use when working with SurrealDB databases, implementing graph traversal, semantic search with embeddings, or building RAG applications.
---

# SurrealDB Python

## Overview

SurrealDB is a multi-model database that combines document, graph, and vector search capabilities in a single system. This skill provides comprehensive guidance for working with SurrealDB 2.3.x using the Python SDK, covering standard database operations, graph relationships, vector similarity search, and real-time data subscriptions.

## When to Use This Skill

Apply this skill when:
- Setting up SurrealDB connections and performing CRUD operations
- Implementing graph databases with the RELATE statement and traversal queries
- Building semantic search or RAG (Retrieval-Augmented Generation) applications with vector embeddings
- Creating real-time applications with live queries
- Designing multi-model schemas that combine documents, graphs, and vectors

## Core Capabilities

### 1. Connection and Authentication

Establish connections to SurrealDB using the Python SDK with proper authentication:

```python
from surrealdb import AsyncSurreal

async with AsyncSurreal("ws://localhost:8000/rpc") as db:
    await db.signin({"user": "root", "pass": "root"})
    await db.use("namespace", "database")
    # Perform operations
```

### 2. CRUD Operations

Perform standard database operations using intuitive Python methods:

- **create()** - Insert new records with specific or auto-generated IDs
- **select()** - Retrieve single records or entire tables
- **update()** - Replace entire record contents
- **merge()** - Partially update records by merging new fields
- **patch()** - Apply JSON Patch operations for precise modifications
- **upsert()** - Create if absent, update if present
- **delete()** - Remove records or entire tables
- **query()** - Execute raw SurrealQL for complex operations

Example workflow:
```python
# Create
user = await db.create("user", {
    "name": "Alice",
    "email": "alice@example.com"
})

# Update specific fields
await db.merge("user:alice", {"age": 30})


# Query with parameters
results = await db.query(
    "SELECT * FROM user WHERE age > $min_age",
    {"min_age": 25}
)
```

### 3. Graph Database Operations

Leverage SurrealDB's native graph capabilities to model and traverse relationships without JOINs:

**Creating Relationships:**
```python
# Create entities
await db.create("person:alice", {"name": "Alice"})
await db.create("person:bob", {"name": "Bob"})

# Create relationship with metadata
await db.query("""
    RELATE person:alice->knows->person:bob
    SET since = "2024-01-01", strength = "close"
""")
```

**Traversing Graphs:**
```python
# Find friends of friends
result = await db.query("""
    SELECT ->knows->person->knows->person AS friends_of_friends
    FROM person:alice
""")

# Bidirectional traversal
result = await db.query("""
    SELECT <->connected_to<->city AS connected_cities
    FROM city:nyc
""")

# Recursive queries (variable depth)
result = await db.query("""
    SELECT @.{1,5}->manages->person AS management_chain
    FROM person:ceo
""")
```

**Key Graph Features:**
- RELATE statement for creating edges between nodes
- Arrow syntax (`->`, `<->`) for intuitive traversal
- Recursive patterns with `@.{depth}` notation
- Graph clauses for filtering during traversal
- Edge tables that store relationship metadata

For comprehensive graph patterns, schema definitions, and best practices, see `references/graph_operations.md`.

### 4. Vector Search and Embeddings

Implement semantic search and similarity-based retrieval using vector embeddings:

**Storing Vectors:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate and store embedding
text = "SurrealDB is a multi-model database"
embedding = model.encode(text).tolist()

await db.create("documents", {
    "content": text,
    "embedding": embedding,
    "metadata": {"source": "docs"}
})
```

**Semantic Search with KNN:**
```python
# Generate query embedding
query_text = "database features"
query_embedding = model.encode(query_text).tolist()

# Find 5 most similar documents
result = await db.query("""
    SELECT content,
           vector::similarity::cosine(embedding, $query_vector) AS similarity
    FROM documents
    WHERE embedding <|5|> $query_vector
    ORDER BY similarity DESC
""", {"query_vector": query_embedding})
```

**Key Vector Features:**
- KNN operator `<|k|>` for k-nearest neighbor search
- Multiple distance metrics (cosine, euclidean, manhattan)
- Hybrid search combining vector and full-text search
- Integration with popular embedding models (OpenAI, HuggingFace, Sentence Transformers)

For complete RAG implementations, embedding model comparisons, and optimization techniques, reference `references/vector_search.md`.

### 5. Real-Time Queries

Subscribe to live data changes for real-time applications:

```python
# Start live query
live_id = await db.live("user")

# Subscribe to changes
async for notification in db.subscribe_live(live_id):
    action = notification['action']  # 'CREATE', 'UPDATE', 'DELETE'
    data = notification['result']
    print(f"Change detected: {action} - {data}")

# Stop live query when done
await db.kill(live_id)
```

## Workflow Patterns

### Building a RAG Application

1. **Define Schema:**
   ```python
   await db.query("""
       DEFINE TABLE documents SCHEMAFULL;
       DEFINE FIELD content ON TABLE documents TYPE string;
       DEFINE FIELD embedding ON TABLE documents TYPE array;
       DEFINE FIELD metadata ON TABLE documents TYPE object;
   """)
   ```

2. **Index Documents:**
   ```python
   for doc in documents:
       embedding = model.encode(doc["content"]).tolist()
       await db.create("documents", {
           "content": doc["content"],
           "embedding": embedding,
           "metadata": doc.get("metadata", {})
       })
   ```

3. **Semantic Search:**
   ```python
   query_embedding = model.encode("user query").tolist()
   results = await db.query("""
       SELECT content, metadata,
              vector::similarity::cosine(embedding, $query_vector) AS score
       FROM documents
       WHERE embedding <|5|> $query_vector
       ORDER BY score DESC
   """, {"query_vector": query_embedding})
   ```

4. **Pass to LLM:** Use retrieved context with language model for generation

### Implementing a Knowledge Graph

1. **Create Entities:**
   ```python
   await db.create("concept:ai", {"name": "Artificial Intelligence"})
   await db.create("concept:ml", {"name": "Machine Learning"})
   ```

2. **Define Relationships:**
   ```python
   await db.query("""
       RELATE concept:ml->is_subset_of->concept:ai
       SET confidence = 0.95
   """)
   ```

3. **Traverse and Query:**
   ```python
   # Find all parent concepts recursively
   result = await db.query("""
       SELECT @.{1,}->is_subset_of->concept AS parents
       FROM concept:ml
   """)
   ```

### Combining Graph and Vector Search

Leverage both graph relationships and semantic similarity:

```python
# Find semantically similar documents connected through graph relationships
result = await db.query("""
    SELECT *,
           vector::similarity::cosine(embedding, $query_vector) AS vec_score
    FROM documents
    WHERE embedding <|10|> $query_vector
      AND ->cited_by->document<-authored_by<-person = $author_id
    ORDER BY vec_score DESC
""", {
    "query_vector": query_embedding,
    "author_id": "person:researcher1"
})
```

## Best Practices

### Connection Management
- Use context managers (`async with`) for automatic cleanup
- Handle `SurrealException` for proper error handling
- Set appropriate timeouts for long-running queries

### Schema Design
- Define schemas with `SCHEMAFULL` for data integrity
- Create indexes on frequently queried fields
- Use assertions for validation and referential integrity

### Graph Operations
- Define unique indexes on edge tables to prevent duplicate relationships
- Add timeouts to recursive queries (`TIMEOUT 5s`)
- Use `FETCH` to optimize queries that need related data
- Store metadata in edge tables when relationships have properties

### Vector Search
- Choose embedding models appropriate for your domain and latency requirements
- Normalize embeddings when using cosine similarity
- Create indexes on vector fields for production workloads
- Chunk long documents (500-1000 tokens) with overlap for better retrieval
- Combine vector search with metadata filtering for precision

### Query Optimization
- Parameterize queries to prevent injection attacks
- Batch operations when inserting multiple records
- Use appropriate k values for KNN (3-5 for precision, 10-20 for recall)
- Leverage hybrid search (vector + full-text) for best results

## Common Use Cases

**Semantic Search & RAG:**
Store document embeddings and perform similarity searches to retrieve relevant context for language models.

**Knowledge Graphs:**
Model complex relationships between entities with typed edges and metadata, enabling sophisticated graph traversal queries.

**Social Networks:**
Represent users and their connections, traverse friend relationships, and find mutual connections or recommendations.

**Recommendation Systems:**
Combine collaborative filtering (graph relationships) with content-based filtering (vector similarity) for hybrid recommendations.

**Real-Time Applications:**
Subscribe to data changes for live dashboards, chat applications, or notification systems.

## Reference Documentation

This skill includes comprehensive reference documentation:

- **`references/graph_operations.md`** - In-depth guide to graph database operations, RELATE syntax, traversal patterns, and schema design
- **`references/vector_search.md`** - Vector search implementation details, embedding model comparisons, RAG patterns, and LangChain integration

Load these references when implementing specific features or troubleshooting issues.

## Additional Resources

- **Repository:** [github.com/surrealdb/surrealdb.py](https://github.com/surrealdb/surrealdb.py)
- **PyPI Package:** [pypi.org/project/surrealdb](https://pypi.org/project/surrealdb/)
- **Official Documentation:** [surrealdb.com/docs](https://surrealdb.com/docs)
- **SurrealQL Reference:** [surrealdb.com/docs/surrealql](https://surrealdb.com/docs/surrealql)
