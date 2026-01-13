# Configuration & Operations for Nano Banana Builder

Complete reference for provider options, storage, rate limiting, and cost management.

## Provider Options Reference

### Response Modalities

```typescript
providerOptions: {
  google: {
    responseModalities: ['IMAGE'],      // Images only (saves tokens)
    responseModalities: ['TEXT', 'IMAGE'], // Both (default)
  }
}
```

**When to use each**:
- `['IMAGE']` - When you only need images, saves token costs
- `['TEXT', 'IMAGE']` - When you want both descriptions and images

### Image Configuration

```typescript
providerOptions: {
  google: {
    imageConfig: {
      aspectRatio: '1:1',   // 1:1, 16:9, 21:9, 4:3, 3:4, 9:16, etc.
      imageSize: '2K'      // Pro only: 1K, 2K (default for Pro is 2K)
    }
  }
}
```

### Aspect Ratio Guide

| Ratio | Resolution | Best For | Token Cost |
|-------|-----------|----------|------------|
| 1:1 | 1024×1024 | Icons, squares, Instagram | Lowest |
| 16:9 | 1344×768 | YouTube thumbnails, widescreen | Medium |
| 21:9 | 1536×672 | Cinematic, ultra-wide | Higher |
| 4:3 | 1184×864 | Presentations, standard | Medium |
| 9:16 | 768×1344 | TikTok, Reels, Stories | Medium |

### Thinking Configuration (Pro Only)

```typescript
providerOptions: {
  google: {
    thinkingConfig: {
      thinkingBudget: 8192,      // Controls reasoning depth (tokens)
      includeThoughts: false     // Return thinking process in response
    }
  }
}
```

**Thinking Budget Guidelines**:
- `4096` - Quick generations, simple prompts
- `8192` - Default balance
- `16384` - Complex compositions, detailed edits
- `32768` - Maximum reasoning for challenging requests

---

## Storage Strategy

### Vercel Blob (Recommended for Vercel Deploy)

```typescript
// lib/storage/vercel-blob.ts
import { put } from '@vercel/blob'

export async function storeImage(
  imageBase64: string,
  userId: string
) {
  const buffer = Buffer.from(imageBase64, 'base64')

  const blob = await put(
    `images/${userId}/${Date.now()}.png`,
    buffer,
    {
      access: 'public',
      token: process.env.BLOB_READ_WRITE_TOKEN
    }
  )

  return blob.url
}

export async function storeImageWithMetadata(
  imageBase64: string,
  userId: string,
  metadata: { prompt: string; model: string }
) {
  const buffer = Buffer.from(imageBase64, 'base64')
  const filename = `${Date.now()}-${metadata.model}.png`

  const blob = await put(
    `images/${userId}/${filename}`,
    buffer,
    {
      access: 'public',
      token: process.env.BLOB_READ_WRITE_TOKEN,
      addMetadata: {
        prompt: metadata.prompt,
        model: metadata.model,
        createdAt: new Date().toISOString()
      }
    }
  )

  return { url: blob.url, filename }
}
```

### S3 / R2 (Universal)

```typescript
// lib/storage/s3.ts
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'

const s3 = new S3Client({
  region: 'auto',
  endpoint: process.env.S3_ENDPOINT,
  credentials: {
    accessKeyId: process.env.S3_ACCESS_KEY_ID!,
    secretAccessKey: process.env.S3_SECRET_ACCESS_KEY!
  }
})

export async function storeImageS3(
  imageBase64: string,
  userId: string
) {
  const buffer = Buffer.from(imageBase64, 'base64')
  const key = `${userId}/${Date.now()}.png`

  await s3.send(new PutObjectCommand({
    Bucket: process.env.S3_BUCKET,
    Key: key,
    Body: buffer,
    ContentType: 'image/png',
    Metadata: {
      createdAt: new Date().toISOString()
    }
  }))

  return `${process.env.S3_PUBLIC_URL}/${key}`
}

// With presigned URLs for private access
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'
import { GetObjectCommand } from '@aws-sdk/client-s3'

export async function getPrivateImageURL(key: string) {
  const command = new GetObjectCommand({
    Bucket: process.env.S3_BUCKET,
    Key: key
  })

  return await getSignedUrl(s3, command, { expiresIn: 3600 })
}
```

### Base64 Fallback (Development Only)

```typescript
// Only for development - do not use in production
export function base64DataURL(base64: string, mediaType = 'image/png') {
  return `data:${mediaType};base64,${base64}`
}
```

---

## Rate Limiting & Cost Management

### Understanding Quotas

**Free Tier:**
- Nano Banana: ~100 RPD (requests per day), 15 RPM (requests per minute)
- Nano Banana Pro: ~10 RPD, 5-10 RPM

**Paid Tier (varies by spend):**
- Tier 1: 500+ RPM
- Tier 2: 1,000+ RPM
- Tier 3: 2,000+ RPM

**Cost Estimates:**
- ~1,290 tokens per image (varies by complexity)
- ~$0.039 per image (varies by model and region)

### Rate Limit Handler (Upstash Redis)

```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '1 m'), // 10 requests per minute
  analytics: true,
  prefix: 'nano-banana'
})

export async function checkRateLimit(userId: string) {
  const { success, limit, reset, remaining } = await ratelimit.limit(userId)

  if (!success) {
    throw new Error(
      `Rate limited. Resets at ${new Date(reset).toISOString()}. ` +
      `Please wait before generating more images.`
    )
  }

  return { limit, remaining }
}

// Usage in server action
export async function generateImage(config: GenerateConfig) {
  // Get user ID from session
  const userId = await getUserId()

  // Check rate limit
  await checkRateLimit(userId)

  // Proceed with generation...
}
```

### Rate Limit Handler (In-Memory)

```typescript
// lib/rate-limit-memory.ts
// Simple in-memory rate limiter for development

interface RateLimitEntry {
  count: number
  resetAt: number
}

const limits = new Map<string, RateLimitEntry>()

export function checkRateLimitMemory(
  userId: string,
  maxRequests = 10,
  windowMs = 60000
) {
  const now = Date.now()
  const entry = limits.get(userId)

  if (!entry || now > entry.resetAt) {
    limits.set(userId, { count: 1, resetAt: now + windowMs })
    return { allowed: true, remaining: maxRequests - 1 }
  }

  if (entry.count >= maxRequests) {
    return {
      allowed: false,
      resetAt: entry.resetAt,
      remaining: 0
    }
  }

  entry.count++
  return { allowed: true, remaining: maxRequests - entry.count }
}
```

### Cost Optimization Strategies

1. **Use Nano for iterations, Pro for final output**
   ```typescript
   // Quick iteration
   const draft = await generateImage({ prompt, model: 'nano' })

   // Final quality
   const final = await generateImage({ prompt, model: 'pro' })
   ```

2. **Set `responseModalities: ['IMAGE']`** to save text tokens
   ```typescript
   providerOptions: {
     google: { responseModalities: ['IMAGE'] }
   }
   ```

3. **Cache similar prompts** with deduplication
   ```typescript
   const cacheKey = `img:${hash(prompt + model + aspectRatio)}`
   const cached = await redis.get(cacheKey)

   if (cached) return { url: cached }

   const result = await generateImage(config)
   await redis.setex(cacheKey, 86400, result.url)
   ```

4. **Implement queue system** for high-volume scenarios
   ```typescript
   // Background job queue
   await queue.add('generate-image', { prompt, model, userId })
   ```

5. **Use appropriate aspect ratios** (1:1 = fewest tokens)

---

## Error Handling

### Common Errors and Solutions

```typescript
// lib/errors.ts
export class NanoBananaError extends Error {
  constructor(
    message: string,
    public code: string,
    public retryable: boolean = false
  ) {
    super(message)
    this.name = 'NanoBananaError'
  }
}

export function handleNanoBananaError(error: any) {
  // Rate limit exceeded
  if (error.message?.includes('429')) {
    throw new NanoBananaError(
      'Too many requests. Please wait a moment.',
      'RATE_LIMIT',
      true
    )
  }

  // Invalid API key
  if (error.message?.includes('401')) {
    throw new NanoBananaError(
      'Invalid API key. Check your configuration.',
      'INVALID_KEY',
      false
    )
  }

  // Content policy violation
  if (error.message?.includes('400')) {
    throw new NanoBananaError(
      'Image generation blocked. Please modify your prompt.',
      'CONTENT_POLICY',
      false
    )
  }

  // Network errors
  if (error.code === 'ECONNREFUSED') {
    throw new NanoBananaError(
      'Connection failed. Please check your internet.',
      'NETWORK_ERROR',
      true
    )
  }

  throw error
}
```

### Usage in Server Actions

```typescript
export async function generateImage(config: GenerateConfig) {
  try {
    const result = await generateText({...})
    return result.files[0]
  } catch (error) {
    handleNanoBananaError(error)
  }
}
```

---

## Environment Variables

```bash
# .env.local
# Required
GEMINI_API_KEY=your_api_key_here

# Vercel Blob (if using Vercel Blob storage)
BLOB_READ_WRITE_TOKEN=vercel_blob_xxxxx

# S3 / R2 (if using S3-compatible storage)
S3_BUCKET=your-bucket-name
S3_ENDPOINT=https://your-endpoint.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=your_access_key
S3_SECRET_ACCESS_KEY=your_secret_key
S3_PUBLIC_URL=https://your-public-domain.com

# Upstash Redis (if using rate limiting)
UPSTASH_REDIS_REST_URL=https://your-redis-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_redis_token

# Optional
NEXT_PUBLIC_APP_URL=https://your-app.com
IMAGE_CACHE_TTL=86400
MAX_IMAGE_SIZE=5242880
```
