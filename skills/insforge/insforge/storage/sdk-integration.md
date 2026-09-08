# Storage SDK Integration

Use InsForge SDK to upload, download, and manage files in your frontend application.

> **Recommended path.** Prefer `@insforge/sdk` for all storage work — it is the supported default for app code (browser and server), handles auth/session scoping, and keeps project-admin credentials in backend/admin tooling. Reach for the [S3-compatible gateway](./s3-gateway.md) only when the consumer is existing S3 tooling (CI pipelines running `aws s3 cp` / `rclone sync`, Terraform, backup/log shippers) where adopting the SDK would be impractical.

## Setup

First, ensure your `.env` file is configured with your InsForge URL and anon key. Get the anon key with `npx -y @insforge/cli secrets get ANON_KEY`. See the main [SKILL.md](../SKILL.md) for framework-specific variable names and full setup steps.

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL,       // adjust prefix for your framework
  anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY   // adjust prefix for your framework
})
```

For Next.js / SSR Client Components, use the SSR browser client so direct browser uploads have the user's access token:

```typescript
import { createBrowserClient } from '@insforge/sdk/ssr'

const insforge = createBrowserClient()
```

Use `createBrowserClient()` for authenticated browser uploads. It reads the browser-readable `insforge_access_token` cookie and refreshes through `/api/auth/refresh`; the refresh token remains httpOnly.

## Upload File

Upload with specific path/key.

```javascript
const { data, error } = await insforge.storage
  .from('images')
  .upload('posts/post-123/cover.jpg', fileObject)

// IMPORTANT: Save BOTH url and key to database
await insforge.database
  .from('posts')
  .update({
    image_url: data.url,
    image_key: data.key  // Required for download/delete
  })
  .eq('id', 'post-123')
```

## Upload with Auto-Generated Key

```javascript
const { data, error } = await insforge.storage
  .from('uploads')
  .uploadAuto(fileObject)

// data.key: "myfile-1705315200000-abc123.jpg"
```

## Download File

```javascript
// Get key from database
const { data: post } = await insforge.database
  .from('posts')
  .select('image_key')
  .eq('id', 'post-123')
  .single()

// Download using key
const { data: blob, error } = await insforge.storage
  .from('images')
  .download(post.image_key)

const url = URL.createObjectURL(blob)
```

## Delete File

```javascript
const { data, error } = await insforge.storage
  .from('images')
  .remove(post.image_key)

// Clear database reference
await insforge.database
  .from('posts')
  .update({ image_url: null, image_key: null })
  .eq('id', 'post-123')
```

## Important Notes

- **Always save both `url` AND `key`**: The URL is for display; the key is required for download/delete operations
- All methods return `{ data, error }` - always check for errors
- Bucket must exist before uploading (create via admin API)
- In Next.js / SSR apps, direct browser uploads should use `createBrowserClient()` from `@insforge/sdk/ssr` so Storage RLS sees the signed-in user

---

## Best Practices

1. **Verify bucket exists before uploading**
   - Check available buckets via CLI: `insforge storage buckets`
   - If no buckets exist, create one first via admin API

2. **Always store both URL and key**
   - The `url` is for displaying/embedding files
   - The `key` is required for download and delete operations

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Uploading before the bucket exists | Verify the bucket via admin API before uploading |
| Saving only the returned URL | Save both `data.url` and `data.key` |
| Using the URL for download/delete operations | Use the stored `key` |
| Creating a plain browser client in SSR Client Components | Use `createBrowserClient()` so access refresh flows through `/api/auth/refresh` and the refresh token remains httpOnly |

## Recommended Workflow

```
1. Check available buckets → insforge storage buckets
2. If no bucket exists     → Create one first
3. Upload file             → Save both url and key to database
4. Display file            → Use url
5. Download/Delete         → Use key
```
