# REST API and Docker deployment

Loaded on demand from the `anti-detect-browser` skill. All credentials come from the environment.

## REST API

Base URL: `https://antibrow.com/api/v1/` - all endpoints require an `Authorization: Bearer $ANTIBROW_API_KEY` header, supplied from the environment.

### Fingerprints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/fingerprints/fetch` | Fetch a fingerprint matching filter criteria. Returns `{ dataUrl }` - download the presigned URL for full fingerprint data. |
| `GET` | `/fingerprints/versions` | List available browser versions |

Query parameters for `/fingerprints/fetch`: `tags`, `id`, `minBrowserVersion`, `maxBrowserVersion`, `minWidth`, `maxWidth`, `minHeight`, `maxHeight`

### Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/profiles` | List all profiles |
| `POST` | `/profiles` | Create a new profile (server assigns a random fingerprint). Returns profile info including `dataUrl` for immediate fingerprint data download. |
| `GET` | `/profiles/:name` | Get profile details with `dataUrl` for fingerprint data download |
| `DELETE` | `/profiles/:name` | Delete a profile |

**POST `/profiles` request body:**
```json
{ "name": "my-profile", "tags": ["Windows 10", "Chrome"] }
```

**POST `/profiles` response (201):**
```json
{
  "name": "my-profile",
  "tags": ["Windows 10", "Chrome"],
  "ua": "Mozilla/5.0 ...",
  "browserVersion": 131,
  "width": 1920,
  "height": 1080,
  "createdAt": "2025-01-01T00:00:00.000Z",
  "dataUrl": "https://cdn.example.com/fingerprints/..."
}
```

The `dataUrl` is a short-lived presigned link to the profile's **fingerprint data as JSON** - screen geometry, UA, GPU strings, seeds. It is data, not an executable, and nothing on the machine runs it. Fetch it promptly; no additional API call is needed.

## Docker

The Linux kernel runs **headful under Xvfb** - real headless Chromium has its own fingerprint, so the image renders to a virtual display. The same image works on `linux/amd64` and `linux/arm64`; the matching kernel build is chosen from the container's CPU.

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      xvfb libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
      libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
      libgbm1 libasound2 libpango-1.0-0 libcairo2 fonts-liberation ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir antibrow==0.3.0
RUN python -m antibrow install          # prefetch the kernel at build time, not at run time
COPY script.py .
CMD ["xvfb-run", "-a", "python", "script.py"]
```

```bash
docker run --rm -e ANTIBROW_API_KEY=$ANTIBROW_API_KEY \
  -v antibrow-cache:/root/.anti-detect-browser my-scraper
```

Mount the cache volume so the kernel and profiles survive between runs.

