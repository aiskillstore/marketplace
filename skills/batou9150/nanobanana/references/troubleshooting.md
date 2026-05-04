# Troubleshooting

## API key resolution order

The CLI checks these env vars in order; first non-empty wins:

1. `NANOBANANA_API_KEY` (preferred)
2. `NANOBANANA_GEMINI_API_KEY`
3. `NANOBANANA_GOOGLE_API_KEY`
4. `GEMINI_API_KEY`
5. `GOOGLE_API_KEY`

Get a key at <https://aistudio.google.com/apikey>.

## Model selection

Default: `gemini-3.1-flash-image-preview` (Nano Banana 2). Override:

```bash
export NANOBANANA_MODEL=gemini-3-pro-image-preview   # Nano Banana Pro
export NANOBANANA_MODEL=gemini-2.5-flash-image       # Nano Banana v1
```

## Input file search paths (`edit` / `restore`)

Resolved against, in order:

1. cwd
2. `./images/`
3. `./input/`
4. `./nanobanana-output/`
5. `~/Downloads/`
6. `~/Desktop/`

Absolute paths bypass search.

## Output

All images saved to `./nanobanana-output/` (created if missing). Filename slug rules: lowercase, special chars stripped, spaces → `_`, max 32 chars. Duplicates get `_1`, `_2`, … appended.

## Common errors

| Error fragment | Cause | Fix |
|---|---|---|
| `api key not valid` | bad key | regenerate at AI Studio |
| `permission denied` / 403 | key lacks Gemini API access | enable in Google Cloud / check project |
| `quota exceeded` | rate limit | wait or upgrade tier |
| `400 ... safety` | safety filter or unsupported content | reword prompt |
| `Input image '...' not found` | file not in any search path | move to cwd or pass an absolute path |
