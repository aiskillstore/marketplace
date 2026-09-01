# Models List

Use OpenRouter model discovery before choosing model IDs, capabilities, pricing,
or modality-specific parameters.

Official OpenRouter references:

- [Models API](https://openrouter.ai/docs/api-reference/models/get-models)
- [Model routing](https://openrouter.ai/docs/features/model-routing)
- [Parameters](https://openrouter.ai/docs/api-reference/parameters)

## Setup

Start with [overview.md](overview.md): run `npx -y @insforge/cli ai setup` so
`OPENROUTER_API_KEY` is available server-side.

## List Models

```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

Use the returned model metadata to verify:

| Field | Why it matters |
|-------|----------------|
| `id` | Exact string to pass as `model` |
| `input_modalities` | Whether the model accepts text, image, audio, or other inputs |
| `output_modalities` | Whether the model can generate text, image, audio, or video |
| `context_length` | How much prompt/context you can send |
| `pricing` | Cost estimates for user-facing or batch workflows |
| `supported_parameters` | Which request parameters the model accepts |

## Capability Filters

```bash
# Image-output chat models
curl "https://openrouter.ai/api/v1/models?output_modalities=image" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Embedding models
curl https://openrouter.ai/api/v1/embeddings/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Video models
curl https://openrouter.ai/api/v1/videos/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Speech-to-text models
curl "https://openrouter.ai/api/v1/models?output_modalities=transcription" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Text-to-speech models
curl "https://openrouter.ai/api/v1/models?output_modalities=speech" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

The InsForge dashboard Model Gateway model list is also suitable for browsing
model IDs and checking whether the project's OpenRouter key is active.

## Best Practices

1. Do not guess model IDs. Query OpenRouter or use the dashboard model list.
2. Check modalities before using image, video, audio, speech, transcription, or embedding code paths.
3. Check `supported_parameters` before sending advanced options.
4. Keep production model IDs in env/config when product owners may tune them.
5. For embeddings, record model ID and dimension next to the vector schema.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using old `ai.configs` rows as the source of truth | Use OpenRouter model discovery |
| Assuming one model supports all modalities | Check `input_modalities` and `output_modalities` |
| Hard-coding "latest" model assumptions into docs | Query models at implementation time |
| Swapping embedding models without schema planning | Confirm dimension and re-embed existing rows |
