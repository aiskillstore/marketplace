# SurrealDB Vector Search Reference

## Overview

SurrealDB provides native vector search capabilities, enabling semantic similarity searches, embeddings storage, and k-nearest neighbors (KNN) queries. This is particularly useful for AI applications, recommendation systems, and semantic search.

## Core Concepts

### Vector Similarity
Vector similarity measures how close two vectors are in multi-dimensional space. SurrealDB uses distance/similarity functions to find the most relevant vectors:
- **Smaller distance** = more similar
- **Larger cosine similarity** (closer to 1) = more similar

### KNN (K-Nearest Neighbors)
The KNN algorithm finds the k most similar vectors to a query vector. SurrealDB uses the `<|k|>` operator for KNN searches.

## Vector Storage

### Defining Vector Fields

```python
# Define a table with a vector field
await db.query("""
    DEFINE TABLE documents SCHEMAFULL;
    DEFINE FIELD content ON TABLE documents TYPE string;
    DEFINE FIELD embedding ON TABLE documents TYPE array;
    DEFINE FIELD metadata ON TABLE documents TYPE object;
""")
```

### Storing Vectors

```python
# Store document with embedding
await db.create("documents", {
    "content": "SurrealDB is a multi-model database",
    "embedding": [0.1, 0.2, 0.3, ...],  # Your embedding vector
    "metadata": {
        "source": "documentation",
        "created_at": "2024-01-01"
    }
})
```

## Generating Embeddings with Python

### Using Sentence Transformers

```python
from sentence_transformers import SentenceTransformer

# Initialize model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embedding
text = "SurrealDB is a multi-model database"
embedding = model.encode(text).tolist()

# Store in SurrealDB
await db.create("documents", {
    "content": text,
    "embedding": embedding
})
```

### Using OpenAI Embeddings

```python
import openai

# Generate embedding
response = openai.embeddings.create(
    model="text-embedding-3-small",
    input="SurrealDB is a multi-model database"
)
embedding = response.data[0].embedding

# Store in SurrealDB
await db.create("documents", {
    "content": text,
    "embedding": embedding
})
```

### Using HuggingFace Transformers

```python
from transformers import AutoTokenizer, AutoModel
import torch

# Load model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding(text):
    # Tokenize
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    # Generate embedding
    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    return embedding

# Use it
embedding = generate_embedding("SurrealDB is a multi-model database")
await db.create("documents", {"content": text, "embedding": embedding})
```

## Vector Search Queries

### Basic KNN Search

```python
# Query embedding
query_text = "database features"
query_embedding = model.encode(query_text).tolist()

# Find 5 most similar documents
result = await db.query("""
    SELECT *, vector::similarity::cosine(embedding, $query_vector) AS similarity
    FROM documents
    WHERE embedding <|5|> $query_vector
    ORDER BY similarity DESC
""", {
    "query_vector": query_embedding
})
```

### Using Different Distance Metrics

```python
# Cosine similarity (range -1 to 1, higher is more similar)
result = await db.query("""
    SELECT *, vector::similarity::cosine(embedding, $query_vector) AS score
    FROM documents
    WHERE embedding <|5|> $query_vector
    ORDER BY score DESC
""", {"query_vector": query_embedding})

# Euclidean distance (lower is more similar)
result = await db.query("""
    SELECT *, vector::distance::euclidean(embedding, $query_vector) AS distance
    FROM documents
    WHERE embedding <|5|> $query_vector
    ORDER BY distance ASC
""", {"query_vector": query_embedding})

# Manhattan distance
result = await db.query("""
    SELECT *, vector::distance::manhattan(embedding, $query_vector) AS distance
    FROM documents
    WHERE embedding <|5|> $query_vector
    ORDER BY distance ASC
""", {"query_vector": query_embedding})
```

### Filtering Vector Search Results

```python
# Search with metadata filtering
result = await db.query("""
    SELECT *, vector::similarity::cosine(embedding, $query_vector) AS similarity
    FROM documents
    WHERE embedding <|10|> $query_vector
      AND metadata.source = "documentation"
      AND metadata.created_at > "2024-01-01"
    ORDER BY similarity DESC
""", {"query_vector": query_embedding})
```

## Complete RAG (Retrieval-Augmented Generation) Example

```python
from sentence_transformers import SentenceTransformer
from surrealdb import Surreal

# Initialize
model = SentenceTransformer("all-MiniLM-L6-v2")

async def setup_database():
    """Initialize SurrealDB with documents"""
    async with Surreal("ws://localhost:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")

        # Define schema
        await db.query("""
            DEFINE TABLE documents SCHEMAFULL;
            DEFINE FIELD content ON TABLE documents TYPE string;
            DEFINE FIELD embedding ON TABLE documents TYPE array;
            DEFINE FIELD metadata ON TABLE documents TYPE object;
        """)

        return db

async def index_documents(db, documents):
    """Index documents with embeddings"""
    for doc in documents:
        embedding = model.encode(doc["content"]).tolist()
        await db.create("documents", {
            "content": doc["content"],
            "embedding": embedding,
            "metadata": doc.get("metadata", {})
        })

async def semantic_search(db, query, k=5):
    """Perform semantic search"""
    # Generate query embedding
    query_embedding = model.encode(query).tolist()

    # Search
    result = await db.query("""
        SELECT content, metadata,
               vector::similarity::cosine(embedding, $query_vector) AS similarity
        FROM documents
        WHERE embedding <|$k|> $query_vector
        ORDER BY similarity DESC
    """, {
        "query_vector": query_embedding,
        "k": k
    })

    return result[0]["result"]

# Usage
async def main():
    db = await setup_database()

    # Index documents
    docs = [
        {"content": "SurrealDB is a multi-model database", "metadata": {"category": "database"}},
        {"content": "Python is a programming language", "metadata": {"category": "programming"}},
        {"content": "Machine learning uses neural networks", "metadata": {"category": "ai"}},
    ]
    await index_documents(db, docs)

    # Search
    results = await semantic_search(db, "What is SurrealDB?", k=3)
    for result in results:
        print(f"Content: {result['content']}")
        print(f"Similarity: {result['similarity']}")
        print()
```

## Vector Indexes

### Creating Vector Indexes

```python
# Create an index on the embedding field for faster searches
await db.query("""
    DEFINE INDEX embedding_idx ON TABLE documents FIELDS embedding
""")
```

## Multi-Vector Search

### Searching Multiple Vector Fields

```python
# Define table with multiple embeddings
await db.query("""
    DEFINE TABLE products SCHEMAFULL;
    DEFINE FIELD name ON TABLE products TYPE string;
    DEFINE FIELD description ON TABLE products TYPE string;
    DEFINE FIELD name_embedding ON TABLE products TYPE array;
    DEFINE FIELD description_embedding ON TABLE products TYPE array;
""")

# Search across multiple embeddings
result = await db.query("""
    SELECT *,
           vector::similarity::cosine(name_embedding, $query_vector) AS name_sim,
           vector::similarity::cosine(description_embedding, $query_vector) AS desc_sim,
           (name_sim * 0.3 + desc_sim * 0.7) AS combined_score
    FROM products
    WHERE name_embedding <|10|> $query_vector
       OR description_embedding <|10|> $query_vector
    ORDER BY combined_score DESC
    LIMIT 5
""", {"query_vector": query_embedding})
```

## Hybrid Search (Vector + Full-Text)

```python
# Combine vector search with full-text filtering
await db.query("""
    DEFINE TABLE articles SCHEMAFULL;
    DEFINE FIELD title ON TABLE articles TYPE string;
    DEFINE FIELD content ON TABLE articles TYPE string;
    DEFINE FIELD embedding ON TABLE articles TYPE array;
    DEFINE INDEX title_idx ON TABLE articles FIELDS title SEARCH ANALYZER ascii BM25;
""")

# Hybrid search
result = await db.query("""
    SELECT *,
           vector::similarity::cosine(embedding, $query_vector) AS vec_score,
           search::score(1) AS text_score,
           (vec_score * 0.7 + text_score * 0.3) AS hybrid_score
    FROM articles
    WHERE title @1@ $search_term
       OR embedding <|10|> $query_vector
    ORDER BY hybrid_score DESC
    LIMIT 5
""", {
    "query_vector": query_embedding,
    "search_term": "database"
})
```

## LangChain Integration

### Using SurrealDBStore

```python
from langchain_community.vectorstores import SurrealDBStore
from langchain.embeddings import OpenAIEmbeddings

# Initialize
embeddings = OpenAIEmbeddings()
vector_store = SurrealDBStore(
    embedding_function=embeddings,
    db_url="ws://localhost:8000/rpc",
    db_user="root",
    db_pass="root",
    namespace="test",
    database="test",
    collection="documents"
)

# Add documents
texts = ["SurrealDB is great", "Vector search is powerful"]
vector_store.add_texts(texts)

# Similarity search
results = vector_store.similarity_search("database features", k=5)

# Similarity search with scores
results_with_scores = vector_store.similarity_search_with_score("database features", k=5)
```

## Best Practices

1. **Choose appropriate embedding models**:
   - `all-MiniLM-L6-v2`: Fast, good for general text (384 dimensions)
   - `all-mpnet-base-v2`: Better quality, slower (768 dimensions)
   - OpenAI `text-embedding-3-small`: High quality, requires API key (1536 dimensions)

2. **Normalize embeddings** when using cosine similarity for consistent results

3. **Index your vectors** for production workloads to improve search performance

4. **Batch embed documents** for better performance when indexing large datasets

5. **Cache embeddings** to avoid regenerating them for the same content

6. **Use appropriate k values**:
   - Smaller k (3-5) for precise results
   - Larger k (10-20) when you need more candidates

7. **Combine with filtering** to narrow results based on metadata

8. **Monitor embedding dimensions** - ensure consistency across all documents

9. **Consider hybrid search** combining vector similarity with keyword search for better results

10. **Store raw content** alongside embeddings for result display and reranking

## Common Patterns

### Document Chunking for Long Texts

```python
def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

# Index chunked document
async def index_long_document(db, model, document_id, text, metadata):
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        await db.create("document_chunks", {
            "document_id": document_id,
            "chunk_index": i,
            "content": chunk,
            "embedding": embedding,
            "metadata": metadata
        })
```

### Semantic Deduplication

```python
# Find near-duplicate documents
async def find_duplicates(db, threshold=0.95):
    all_docs = await db.select("documents")

    duplicates = []
    for doc in all_docs:
        similar = await db.query("""
            SELECT id, content,
                   vector::similarity::cosine(embedding, $embedding) AS similarity
            FROM documents
            WHERE id != $doc_id
              AND embedding <|5|> $embedding
              AND vector::similarity::cosine(embedding, $embedding) > $threshold
        """, {
            "embedding": doc["embedding"],
            "doc_id": doc["id"],
            "threshold": threshold
        })

        if similar[0]["result"]:
            duplicates.append({
                "original": doc["id"],
                "duplicates": similar[0]["result"]
            })

    return duplicates
```
