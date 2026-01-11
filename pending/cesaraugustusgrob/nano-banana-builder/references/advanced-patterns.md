# Advanced Patterns for Nano Banana Builder

Complete implementations for production-ready Nano Banana web applications.

## Server Actions

### Image Generation with Model Selection

```typescript
// app/actions/generate.ts
'use server'

import { google } from '@ai-sdk/google'
import { generateText } from 'ai'
import { put } from '@vercel/blob'

interface GenerateConfig {
  prompt: string
  model: 'nano' | 'pro'
  aspectRatio?: '1:1' | '16:9' | '21:9'
  storeImage?: boolean
}

export async function generateImage(config: GenerateConfig) {
  const { prompt, model, aspectRatio = '1:1', storeImage = true } = config

  const modelName = model === 'pro'
    ? 'gemini-3-pro-image-preview'
    : 'gemini-2.5-flash-image'

  const result = await generateText({
    model: google(modelName),
    prompt,
    providerOptions: {
      google: {
        responseModalities: ['IMAGE'],
        imageConfig: {
          aspectRatio,
          ...(model === 'pro' && { imageSize: '2K' })
        }
      }
    }
  })

  const imageFile = result.files[0]

  if (storeImage && imageFile?.base64) {
    const buffer = Buffer.from(imageFile.base64, 'base64')
    const blob = await put(`generated/${Date.now()}.png`, buffer, {
      access: 'public'
    })
    return { url: blob.url, base64: imageFile.base64 }
  }

  return { url: `data:${imageFile.mediaType};base64,${imageFile.base64}` }
}
```

### Iterative Editing (Multi-Turn)

```typescript
// app/actions/edit.ts
'use server'

import { google } from '@ai-sdk/google'
import { generateText } from 'ai'

interface EditConfig {
  imageBase64: string
  editPrompt: string
  model: 'nano' | 'pro'
  history?: Array<{role: string; content: any}>
}

export async function editImage(config: EditConfig) {
  const { imageBase64, editPrompt, model, history = [] } = config

  const modelName = model === 'pro'
    ? 'gemini-3-pro-image-preview'
    : 'gemini-2.5-flash-image'

  // Build conversation with image as first message
  const contents = [
    { role: 'user', content: [
      { type: 'image', image: imageBase64 },
      { type: 'text', text: editPrompt }
    ]}
  ]

  const result = await generateText({
    model: google(modelName),
    messages: [...history, ...contents],
    providerOptions: {
      google: {
        responseModalities: ['IMAGE']
      }
    }
  })

  return {
    url: `data:${result.files[0].mediaType};base64,${result.files[0].base64}`,
    newHistory: [...history, ...contents, {
      role: 'assistant',
      content: result.files[0]
    }]
  }
}
```

### API Route with Streaming

```typescript
// app/api/generate/route.ts
import { google } from '@ai-sdk/google'
import { streamText } from 'ai'

export const maxDuration = 30

export async function POST(req: Request) {
  const { prompt, model = 'nano' } = await req.json()

  const result = streamText({
    model: google(model === 'pro' ? 'gemini-3-pro-image-preview' : 'gemini-2.5-flash-image'),
    prompt,
    providerOptions: {
      google: {
        responseModalities: ['IMAGE', 'TEXT']
      }
    }
  })

  return result.toDataStreamResponse()
}
```

---

## Client-Side Components

### Complete Image Generator Component

```typescript
// app/components/ImageGenerator.tsx
'use client'

import { useState } from 'react'
import { useChat } from '@ai-sdk/react'

type Model = 'nano' | 'pro'

export function ImageGenerator() {
  const [selectedModel, setSelectedModel] = useState<Model>('nano')
  const [prompt, setPrompt] = useState('')

  const { messages, append, isLoading } = useChat({
    api: '/api/generate',
    body: { model: selectedModel }
  })

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return

    append({
      role: 'user',
      content: prompt,
      // @ts-ignore - custom body property
      model: selectedModel
    })
    setPrompt('')
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Model Selector */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setSelectedModel('nano')}
          className={`px-4 py-2 rounded ${selectedModel === 'nano'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200'}`}
        >
          Nano (Fast)
        </button>
        <button
          onClick={() => setSelectedModel('pro')}
          className={`px-4 py-2 rounded ${selectedModel === 'pro'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200'}`}
        >
          Pro (Quality)
        </button>
      </div>

      {/* Generated Images Gallery */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {messages.map((m, i) =>
          m.parts?.map((part, j) =>
            part.type === 'image' && (
              <img
                key={`${i}-${j}`}
                src={part.url}
                alt="Generated"
                className="w-full rounded-lg shadow"
              />
            )
          )
        )}
      </div>

      {/* Prompt Input */}
      <form onSubmit={handleGenerate} className="flex gap-2">
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your image..."
          className="flex-1 px-4 py-2 border rounded"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className="px-6 py-2 bg-purple-500 text-white rounded disabled:opacity-50"
        >
          {isLoading ? 'Generating...' : 'Generate'}
        </button>
      </form>
    </div>
  )
}
```

### Iterative Editor Component

```typescript
// app/components/IterativeEditor.tsx
'use client'

import { useState } from 'react'

interface EditHistory {
  role: string
  content: any
}

export function IterativeEditor() {
  const [currentImage, setCurrentImage] = useState<string>('')
  const [editPrompt, setEditPrompt] = useState('')
  const [history, setHistory] = useState<EditHistory[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleEdit = async () => {
    if (!editPrompt.trim() || !currentImage) return

    setIsLoading(true)

    const response = await fetch('/api/edit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        imageBase64: currentImage.split(',')[1],
        editPrompt,
        history
      })
    })

    const data = await response.json()
    setCurrentImage(data.url)
    setHistory(data.newHistory)
    setEditPrompt('')
    setIsLoading(false)
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Image Display */}
      <div className="flex-1">
        {currentImage ? (
          <img src={currentImage} alt="Current" className="w-full rounded" />
        ) : (
          <div className="aspect-square bg-gray-100 rounded flex items-center justify-center">
            Upload or generate an image to start
          </div>
        )}
      </div>

      {/* Edit Controls */}
      <div className="flex-1">
        <textarea
          value={editPrompt}
          onChange={(e) => setEditPrompt(e.target.value)}
          placeholder="Describe your edit..."
          className="w-full h-32 p-3 border rounded mb-4"
        />

        <button
          onClick={handleEdit}
          disabled={isLoading || !editPrompt.trim()}
          className="w-full py-2 bg-green-500 text-white rounded disabled:opacity-50"
        >
          {isLoading ? 'Editing...' : 'Apply Edit'}
        </button>

        {/* History */}
        <div className="mt-4">
          <h3 className="font-bold mb-2">Edit History</h3>
          {history.slice(-5).map((h, i) => (
            <div key={i} className="text-sm text-gray-600 py-1">
              {h.role}: {typeof h.content === 'string'
                ? h.content
                : JSON.stringify(h.content).substring(0, 50)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

---

## Advanced Patterns

### Multi-Image Composition

```typescript
// Combine multiple images into one generation
export async function compositeImages(
  images: string[],
  prompt: string
) {
  const imageParts = images.map(img => ({
    inlineData: {
      mimeType: 'image/png',
      data: img.split(',')[1]
    }
  }))

  const result = await generateText({
    model: google('gemini-3-pro-image-preview'),
    messages: [{
      role: 'user',
      content: [...imageParts, { text: prompt }]
    }],
    providerOptions: {
      google: { responseModalities: ['IMAGE'] }
    }
  })

  return result.files[0]
}
```

### Batch Generation with Progress

```typescript
// app/actions/batch.ts
export async function generateBatch(
  prompts: string[],
  onProgress?: (current: number, total: number) => void
) {
  const results = []

  for (let i = 0; i < prompts.length; i++) {
    const result = await generateImage({
      prompt: prompts[i],
      model: 'nano',
      storeImage: true
    })
    results.push(result)
    onProgress?.(i + 1, prompts.length)
  }

  return results
}
```

### Progressive Loading

```typescript
// Generate low-res first, then high-res
export async function generateProgressive(prompt: string) {
  // Fast preview
  const preview = await generateImage({
    prompt,
    model: 'nano',
    storeImage: false
  })

  // High-res final
  const final = await generateImage({
    prompt,
    model: 'pro',
    storeImage: true
  })

  return { preview, final }
}
```

---

## Usage Patterns

### Gallery with Infinite Scroll

```typescript
// app/components/ImageGallery.tsx
'use client'

import { useState, useEffect } from 'react'
import { useChat } from '@ai-sdk/react'

export function ImageGallery() {
  const { messages, append, isLoading } = useChat({
    api: '/api/generate'
  })

  const images = messages.flatMap(m =>
    m.parts?.filter(p => p.type === 'image') ?? []
  )

  return (
    <div className="grid grid-cols-3 gap-4">
      {images.map((part, i) => (
        <div key={i} className="aspect-square">
          <img src={part.url} alt="" className="w-full h-full object-cover rounded" />
        </div>
      ))}
    </div>
  )
}
```

### Error Handling with Retry

```typescript
// app/actions/generate.ts
export async function generateImageWithRetry(
  config: GenerateConfig,
  maxRetries = 3
) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await generateImage(config)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(r => setTimeout(r, 1000 * (i + 1)))
    }
  }
}
```
