# Embeddings and RAG

Use OpenRouter embeddings through the OpenAI SDK, then store vectors in
InsForge Postgres with pgvector. InsForge remains the database/vector store;
OpenRouter provides the embedding model gateway.

Official references:

- [OpenRouter embeddings](https://openrouter.ai/docs/api-reference/embeddings)
- [OpenAI SDK with OpenRouter](https://openrouter.ai/docs/guides/community/openai-sdk)
- [InsForge CLI pgvector setup](../../insforge-cli/references/database/vector.md)

## Setup

Bring up the `vector` extension, vector tables, indexes, and match RPCs through
an InsForge CLI database migration; see
[database/vector.md](../../insforge-cli/references/database/vector.md).

Run the AI key setup from the linked app directory:

```bash
npx -y @insforge/cli ai setup
```

Initialize the OpenAI SDK with OpenRouter as shown in [overview.md](overview.md).
Do not expose `OPENROUTER_API_KEY` to the browser. Generate embeddings through a
server route, server action, function, or backend.

## Model and Schema

Check current embedding models before shipping:

```bash
curl https://openrouter.ai/api/v1/embeddings/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

Common dimensions:

| Model | Dimensions |
|-------|------------|
| `openai/text-embedding-3-small` | 1536 |
| `openai/text-embedding-3-large` | 3072 |
| `google/gemini-embedding-001` | 3072 |

The Postgres column must match the embedding dimension, for example
`embedding vector(1536)`. Store the embedding model next to ingested content if
you expect to re-embed or migrate later.

## Store Documents

Use InsForge for the durable content row and vector. Keep one embedding model
per vector column.

```typescript
async function storeDocument(content: string) {
  const response = await openai.embeddings.create({
    model: process.env.OPENROUTER_EMBEDDING_MODEL ?? 'openai/text-embedding-3-small',
    input: content,
  })

  const { data, error } = await insforge.database.from('documents').insert([{
    content,
    embedding: response.data[0].embedding,
  }]).select()

  if (error) {
    throw error
  }

  return data
}
```

For batch ingestion, pass an array to `input` and insert rows in the same order
as `response.data`.

## Search and Answer

Embed the user query, retrieve matching rows through the `match_documents` RPC,
then pass retrieved content into a chat completion. Store the final answer in
your app's own table if the product has conversation history.

```typescript
async function askQuestion(sessionId: string, question: string) {
  const embeddingResponse = await openai.embeddings.create({
    model: process.env.OPENROUTER_EMBEDDING_MODEL ?? 'openai/text-embedding-3-small',
    input: question,
  })

  const { data: documents, error: searchError } = await insforge.database.rpc('match_documents', {
    query_embedding: embeddingResponse.data[0].embedding,
    match_count: 5,
    match_threshold: 0.78,
  })

  if (searchError) {
    throw searchError
  }

  const context = (documents ?? [])
    .map((doc: { content: string }) => doc.content)
    .join('\n\n')

  const completion = await openai.chat.completions.create({
    model: process.env.OPENROUTER_CHAT_MODEL ?? 'openai/gpt-4o',
    messages: [
      { role: 'system', content: `Answer using this context:\n\n${context}` },
      { role: 'user', content: question },
    ],
  })

  const answer = completion.choices[0]?.message?.content ?? ''

  const { error: insertError } = await insforge.database.from('chat_messages').insert([
    { session_id: sessionId, role: 'user', content: question },
    {
      session_id: sessionId,
      role: 'assistant',
      content: answer,
      model: completion.model,
      retrieval_count: documents?.length ?? 0,
    },
  ])

  if (insertError) {
    throw insertError
  }

  return answer
}
```

## Best Practices

1. Design the InsForge tables first: source documents, vector column dimension,
   match RPC, and optional chat history table.
2. If your schema includes an `embedding_model` column, store the model ID with
   embedded rows so future migrations can identify which vectors need
   re-embedding.
3. Use one embedding model per vector column. Re-embed when changing models.
4. Add chunking, query rewriting, re-ranking, context truncation, and retrieval
   evaluation before treating a RAG prototype as production-ready.
5. Use RLS on source documents and chat history. If a `SECURITY DEFINER` RPC
   bypasses RLS, re-filter inside the function by `auth.uid()` or tenant ID.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Asking the user to enable an embedding model in old AI Settings | Use OpenRouter embedding models and `OPENROUTER_API_KEY` |
| Querying `ai.configs` for embedding models | Use `/api/v1/embeddings/models` |
| Putting `OPENROUTER_API_KEY` in browser env vars | Keep it server-side |
| Column dimension does not match model dimension | Match `vector(N)` to the model output |
| `encoding_format: 'base64'` into pgvector | Use float arrays |
| Mixing embedding models in one column | Pick one; mixed vectors give meaningless search results |
