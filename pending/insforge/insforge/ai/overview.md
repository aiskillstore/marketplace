# AI Overview

Use OpenRouter as the model gateway for new InsForge AI features. InsForge
provides the project-level OpenRouter key; app code should call OpenRouter from
server-side code and use InsForge for data, storage, auth, and RLS.

Official OpenRouter references:

- [OpenAI SDK with OpenRouter](https://openrouter.ai/docs/guides/community/openai-sdk)
- [Chat completions](https://openrouter.ai/docs/api-reference/chat-completion)
- [Image generation](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
- [Embeddings](https://openrouter.ai/docs/api-reference/embeddings)
- [Video generation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)
- [Models API](https://openrouter.ai/docs/api-reference/models/get-models)

## Setup

Run this from the linked app directory before adding AI code:

```bash
npx -y @insforge/cli ai setup
```

This fetches the active OpenRouter key from the linked InsForge backend and
writes it to `.env.local`:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

For non-standard env files, use `--env-file <path>`. If the command is
unavailable, ask the user to upgrade `@insforge/cli` or copy the key from the
InsForge dashboard Model Gateway.

Keep `OPENROUTER_API_KEY` server-side only. Browser-visible env prefixes such
as `NEXT_PUBLIC_*`, `VITE_*`, `PUBLIC_*`, and `REACT_APP_*` are for non-secret
values.

Use these optional server-side model override names consistently when a project
needs configurable models:

| Variable | Used For |
|----------|----------|
| `OPENROUTER_CHAT_MODEL` | Chat completions and RAG answer generation |
| `OPENROUTER_IMAGE_MODEL` | Image generation |
| `OPENROUTER_EMBEDDING_MODEL` | Embeddings and vector search |

Install the OpenAI SDK when using chat completions or embeddings:

```bash
npm install openai
```

```typescript
import OpenAI from 'openai'

export const openai = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY,
})
```

For browser apps, create a server route, server action, function, or backend
endpoint that calls OpenRouter. Have the browser call your server endpoint.

## Capability Guides

| Capability | Use |
|------------|-----|
| [chat-completions.md](chat-completions.md) | Text generation, structured answers, streaming chat |
| [image-generation.md](image-generation.md) | Generate or edit images, then upload outputs to InsForge Storage |
| [video-generation.md](video-generation.md) | Async video jobs, server-side polling, and storing generated media |
| [audio.md](audio.md) | Speech-to-text, text-to-speech, and audio asset storage patterns |
| [embeddings-and-rag.md](embeddings-and-rag.md) | Generate embeddings, store/search vectors in InsForge pgvector, and build RAG |
| [models-list.md](models-list.md) | Discover model IDs, modalities, pricing, limits, and dimensions |

## InsForge Patterns

1. Run `npx -y @insforge/cli ai setup` before writing OpenRouter code.
2. Store generated files in InsForge Storage; save both `url` and `key` in the
   database.
3. Store embeddings in Postgres `vector(N)` columns; `N` must match the model's
   output dimension.
4. Use `@insforge/sdk` for database, auth, storage, realtime, and payments.
   Use OpenRouter APIs for model calls.
5. Check model capabilities through OpenRouter before using image, video,
   embeddings, or special parameters.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Putting `OPENROUTER_API_KEY` in public frontend env vars | Keep it server-side and proxy through your app backend |
| Querying old `ai.configs` tables for supported models | Use [models-list.md](models-list.md) and OpenRouter model APIs |
| Using `insforge.ai` for new features | Use OpenRouter APIs with the project OpenRouter key |
| Saving generated base64/media directly in Postgres | Upload to InsForge Storage and save `url` plus `key` |
