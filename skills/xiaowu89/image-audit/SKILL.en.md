---
name: image-audit
description: >-
  Automated image content moderation workflow. Batch audit images for adult/political/violent content,
  auto-compress large images via sharp, call MCP audit service, and output results as a table.
  Requires nx-mcp-audit MCP service configured.
license: MIT
compatibility: Claude Code, Cursor, Windsurf, Copilot, any SKILL.md-compatible agent
metadata:
  author: bai9707
  version: "1.0.1"
  tags: image-audit content-moderation nsfw-detection batch-processing
---

# Image Content Moderation Expert

You are an image content moderation expert, responsible for detecting adult, political, and violent content in images.

## Prerequisites: MCP Service Setup

Configure the MCP server in Claude Code `settings.json` before using this skill:

```json
{
  "mcpServers": {
    "nx-mcp-audit": {
      "type": "url",
      "url": "https://mcp.api-inference.modelscope.net/274be9de7fd649/mcp"
    }
  }
}
```

Restart Claude Code or refresh MCP connections after configuration.

## Audit Workflow

Follow these steps strictly when the user requests image auditing:

### Step 1: Collect Images

Determine the image source:
- **Folder path** (e.g., `E:/images/`): use `ls` to list all `png/jpg/jpeg/webp/bmp` files
- **Network URL**: download via `curl` to a temp directory, then convert to dataUrl
- **Single image path**: convert directly to dataUrl

> Convert all images to dataUrl and pass via the `files` parameter to avoid server-side network failures.

After collection, report to the user: X images total, estimated Y–Z seconds (~3–8s per image).

### Step 2: Compress Images

All images must be compressed before submitting — the MCP gateway has a ~4MB payload limit.

First, ensure `sharp` is available (auto-installs on first run, ~11s):

```bash
node -e "require('sharp')" 2>/dev/null || npm install sharp --no-save
```

Then compress each image: max edge 500px, JPEG Q40:

```bash
node -e "
const fs=require('fs');
const sharp=require('sharp');
(async()=>{
  const path='IMAGE_PATH';
  const raw=fs.readFileSync(path);
  const compressed=await sharp(raw)
    .resize(500,500,{fit:'inside',withoutEnlargement:true})
    .jpeg({quality:40})
    .toBuffer();
  const b64=compressed.toString('base64');
  console.log('data:image/jpeg;base64,'+b64);
  console.error(path+': '+(raw.length/1024).toFixed(0)+'KB → '+(compressed.length/1024).toFixed(0)+'KB');
})();
"
```

> Compressed dataUrl is typically < 100KB, safely within gateway limits. Accuracy is not affected.

### Step 3: Audit Each Image

Call the `nx_img_audit` tool from the `nx-mcp-audit` MCP service.

**Parameters:**
| Parameter | Type | Usage |
|-----------|------|-------|
| `files` | `string[]` | **Recommended** — compressed dataUrls (`data:image/jpeg;base64,...`) |
| `urls` | `string[]` | HTTP(S) image URLs (requires server network access) |
| `apiKey` | `string` | **Required** — MCP service API key |

> **Note:** `apiKey` must be explicitly passed each call.

**Batch strategy:**
- Pass all dataUrls in a single `files` array call
- Recommended max 20 images per batch

### Step 4: Summarize Results

Present all audit results in a table:

| File | Size | Result | Details |
|------|------|--------|---------|
| photo1.png | 909KB | ✅ Pass | - |
| photo2.png | 2.8MB | ⛔ Blocked | Contains violation |
| photo3.png | 156KB | ❌ Failed | HTTP 404 |

**Response fields:**
| Field | Type | Description |
|-------|------|-------------|
| `safe` | `boolean` | `true`=pass, `false`=blocked |
| `message` | `string` | Audit result description |
| `source` | `string` | Audit engine (e.g., `"wechat"`) |
| `errcode` | `number` | Engine error code, `0`=ok |
| `errmsg` | `string` | Engine error message |
| `error` | `string` | Request-level failure (download failed, etc.) |
| `summary` | `object` | Aggregate stats `{total, pass, block, error}` |
| `auditVersion` | `string` | Audit service version |

### Step 5: Provide Recommendations

- Blocked images (`safe: false`): delete or manually review
- Failed images (`error` field present): check accessibility, retry once
- Passed images (`safe: true`): safe to use

## Error Handling

| Scenario | Action |
|----------|--------|
| Single image audit failure (`error` field) | Mark ❌ in table, don't block other images |
| File not found | Skip, mark "File not found" |
| Unsupported format | Skip, mark "Format not supported" |
| MCP service timeout | Prompt "Service temporarily unavailable", retry after 5s |
| Invalid API Key (`errcode != 0`) | Prompt user to check `apiKey` |
| All images failed | Check network and API Key, suggest retry |

## Notes

- ~3–8s per image; inform user of estimated time for batch jobs
- `safe=true`: pass, `safe=false`: blocked, `error` field: request failure
- `summary.block`: blocked count, `summary.error`: failure count
- `auditVersion`: service version identifier
- No hard size limit, but dataUrl encoding adds ~33% overhead; single images over 10MB should be compressed first
- Prioritize `files` over `urls` to avoid server-side network issues
