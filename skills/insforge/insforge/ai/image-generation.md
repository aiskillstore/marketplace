# Image Generation

Use OpenRouter image-capable chat models for image generation or image editing,
then store durable outputs in InsForge Storage.

Official OpenRouter references:

- [Image generation](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
- [Chat completions](https://openrouter.ai/docs/api-reference/chat-completion)
- [Models API](https://openrouter.ai/docs/api-reference/models/get-models)

## Setup

Start with [overview.md](overview.md): run `npx -y @insforge/cli ai setup` and keep
`OPENROUTER_API_KEY` server-side. Check image-capable models before use:

```bash
curl "https://openrouter.ai/api/v1/models?output_modalities=image" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

## Generate an Image

OpenRouter image generation uses chat completions with image output
modalities. Direct `fetch` avoids TypeScript friction around OpenRouter-specific
fields such as `modalities`, `image_config`, and `message.images`.

```typescript
const prompt = 'Create a clean product mockup on a white desk.'

const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: process.env.OPENROUTER_IMAGE_MODEL ?? 'google/gemini-2.5-flash-image',
    modalities: ['image', 'text'],
    messages: [
      { role: 'user', content: prompt },
    ],
    image_config: {
      aspect_ratio: '16:9',
    },
  }),
})

if (!response.ok) {
  throw new Error(`OpenRouter image request failed: ${response.status}`)
}

const result = await response.json()
const imageUrl = result.choices?.[0]?.message?.images?.[0]?.image_url?.url

if (!imageUrl) {
  throw new Error('OpenRouter response did not include an image URL')
}
```

## Store the Output

OpenRouter output URLs should be treated as transfer URLs, not your app's
permanent asset store. Upload the generated file to InsForge Storage and save
both `url` and `key` in the database.

Do not store raw base64 image data or large binary blobs in Postgres. Store
metadata and Storage references in the database; keep image bytes in Storage.
Derive owner, tenant, or session fields from the authenticated server-side
context; never accept ownership IDs from the browser.

```typescript
const imageResponse = await fetch(imageUrl)
const imageBlob = await imageResponse.blob()
const storageKey = `generated/${crypto.randomUUID()}.png`

const { data, error } = await insforge.storage
  .from('images')
  .upload(storageKey, imageBlob)

if (error) {
  throw error
}

const { data: userData, error: userError } = await insforge.auth.getCurrentUser()
if (userError || !userData?.user?.id) {
  throw userError ?? new Error('Authentication required')
}

await insforge.database.from('generated_images').insert([{
  user_id: userData.user.id,
  prompt,
  image_url: data.url,
  image_key: data.key,
}])
```

## Best Practices

1. Use [models-list.md](models-list.md) to verify `output_modalities` includes
   `image`.
2. Keep image prompts and model calls on the server.
3. Persist generated images in InsForge Storage before storing database rows.
4. Save the original prompt, model ID, storage `url`, and storage `key` when the
   product needs reproducibility or deletion.
5. Use authenticated owner, session, or tenant fields on generated-image rows so
   RLS can restrict access.
6. Use direct HTTP when OpenAI SDK types reject OpenRouter-specific image
   fields; do not remove those fields to satisfy TypeScript.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using a text-only model for image output | Filter models with `output_modalities=image` |
| Storing raw base64 image data or temporary image URLs in Postgres | Upload to Storage, save `url` and `key` |
| Removing `modalities` because TypeScript complains | Use direct `fetch` or a narrow local type cast |
| Assuming every image model supports the same options | Check the model and image generation docs first |
