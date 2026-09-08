# Database Vector Search

Use this reference when configuring pgvector with the InsForge CLI: vector
extension setup, embedding columns, similarity search functions, HNSW/IVFFlat
indexes, and vector-specific RLS considerations.

For app code that generates embeddings through OpenRouter and inserts vectors
with `@insforge/sdk`, use the `insforge` app-integration skill's AI/RAG guidance after this backend
schema is in place.

## Migration Pattern

DDL belongs in a migration. Create a migration file with
`npx -y @insforge/cli db migrations new <name>`, put SQL like the example below in
that file, then apply it with `npx -y @insforge/cli db migrations up --all`.

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE public.documents (
  id BIGSERIAL PRIMARY KEY,
  owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  embedding vector(1536) NOT NULL,
  embedding_model TEXT NOT NULL DEFAULT 'openai/text-embedding-3-small',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "owners can read documents"
ON public.documents
FOR SELECT TO authenticated
USING (owner_id = (SELECT auth.uid()));

CREATE POLICY "owners can insert documents"
ON public.documents
FOR INSERT TO authenticated
WITH CHECK (owner_id = (SELECT auth.uid()));

GRANT SELECT, INSERT ON public.documents TO authenticated;

CREATE OR REPLACE FUNCTION public.match_documents(
  query_embedding vector(1536),
  match_count INT DEFAULT 5,
  match_threshold DOUBLE PRECISION DEFAULT 0.78
)
RETURNS TABLE (
  id BIGINT,
  content TEXT,
  similarity DOUBLE PRECISION
)
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $$
  SELECT
    public.documents.id,
    public.documents.content,
    1 - (public.documents.embedding <=> query_embedding) AS similarity
  FROM public.documents
  WHERE 1 - (public.documents.embedding <=> query_embedding) >= match_threshold
  ORDER BY public.documents.embedding <=> query_embedding
  LIMIT match_count;
$$;

GRANT EXECUTE ON FUNCTION public.match_documents(vector, INT, DOUBLE PRECISION)
TO authenticated;

CREATE INDEX documents_owner_id_idx ON public.documents (owner_id);
CREATE INDEX documents_embedding_hnsw_idx
ON public.documents
USING hnsw (embedding vector_cosine_ops);
```

## Dimensions

Match `vector(N)` to the embedding model output dimension.

| Model                           | Dimensions |
| ------------------------------- | ---------- |
| `openai/text-embedding-3-small` | 1536       |
| `openai/text-embedding-3-large` | 3072       |
| `openai/text-embedding-ada-002` | 1536       |
| `google/gemini-embedding-001`   | 3072       |

A vector column's dimension cannot be altered in place. To change models with a
different dimension, create a new vector column/table and re-embed data.

## Distance Operators

Pick one distance operator and use the matching index operator class.

| Operator | Distance               | Operator class      | Typical use                       |
| -------- | ---------------------- | ------------------- | --------------------------------- |
| `<=>`    | Cosine                 | `vector_cosine_ops` | Default for normalized embeddings |
| `<->`    | L2                     | `vector_l2_ops`     | Un-normalized embeddings          |
| `<#>`    | Inner product, negated | `vector_ip_ops`     | Advanced ranking patterns         |

For cosine distance, lower distance is closer. If exposing a similarity score,
use `1 - (embedding <=> query_embedding)` and keep ordering by raw distance.

## Indexing

Without an index, pgvector performs exact nearest-neighbor scans. That is
correct but linear. Add an index before production-sized workloads.

HNSW is usually the default choice and is safe to create on empty tables:

```sql
CREATE INDEX documents_embedding_hnsw_idx
ON public.documents
USING hnsw (embedding vector_cosine_ops);
```

IVFFlat uses less memory, but build it only after representative data exists:

```sql
CREATE INDEX documents_embedding_ivfflat_idx
ON public.documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

Index columns used with vector filters, such as `owner_id`, `tenant_id`,
`document_type`, or `created_at`. The vector index helps nearest-neighbor order;
normal B-tree indexes help metadata filters.

## SQL Inserts and Queries

For small SQL fixtures or debugging, cast a JSON-array literal to the exact
vector dimension:

```sql
CREATE TABLE public.vec_demo (
  id BIGSERIAL PRIMARY KEY,
  embedding vector(3) NOT NULL
);

INSERT INTO public.vec_demo (embedding)
VALUES ('[0.12,0.34,0.56]'::vector(3));

SELECT *
FROM public.vec_demo
ORDER BY embedding <=> '[0.10,0.30,0.55]'::vector(3)
LIMIT 5;
```

For real app data, generate embeddings in server-side app code and insert a
`number[]` with the InsForge SDK.

## RLS and RPCs

Standard RLS applies to vector tables. A `SECURITY INVOKER` match function runs
under the caller's role, so table policies still filter rows.

If a vector search function must be `SECURITY DEFINER`, re-check `auth.uid()` or
tenant membership inside the function body. Do not bypass RLS and return vectors
or documents across users/tenants by accident.

## Common Mistakes

| Mistake                                                    | Fix                                                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Creating `pgvector` extension instead of `vector`          | Use `CREATE EXTENSION IF NOT EXISTS vector;`                                                |
| Dimension mismatch between model and column                | Set `vector(N)` to the model's exact output dimension                                       |
| Ordering similarity descending while thresholding distance | Keep distance and similarity semantics explicit                                             |
| Operator class does not match query operator               | Pair `<=>` with `vector_cosine_ops`, `<->` with `vector_l2_ops`, `<#>` with `vector_ip_ops` |
| IVFFlat on an empty table                                  | Use HNSW, or build IVFFlat after representative rows exist                                  |
| Client-side distance math                                  | Put search/ranking in SQL or an RPC                                                         |
| SECURITY DEFINER vector RPC without user/tenant filter     | Re-filter inside the function body                                                          |
