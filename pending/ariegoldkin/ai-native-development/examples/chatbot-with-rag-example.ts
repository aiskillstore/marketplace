/**
 * Complete Chatbot with RAG Example
 * Demonstrates conversational AI with knowledge retrieval
 */

import OpenAI from 'openai'
import { ragQuery } from '../templates/rag-pipeline-template'

const openai = new OpenAI()

// Next.js API Route Handler
export async function POST(req: Request) {
  const { messages } = await req.json()
  const userMessage = messages[messages.length - 1].content

  // 1. Determine if RAG is needed
  const needsRetrieval = await shouldUseRAG(userMessage, messages)

  if (needsRetrieval) {
    // 2. Perform RAG query
    const ragResult = await ragQuery(userMessage, { topK: 3 })

    // 3. Add context to messages
    messages.push({
      role: 'system',
      content: `Relevant information:\n${ragResult.sources.map((s, i) => `[${i + 1}] ${s.text}`).join('\n\n')}`
    })
  }

  // 4. Generate streaming response
  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages,
    stream: true
  })

  // 5. Stream response
  return new ReadableStream({
    async start(controller) {
      for await (const chunk of response) {
        const content = chunk.choices[0]?.delta?.content
        if (content) {
          controller.enqueue(new TextEncoder().encode(content))
        }
      }
      controller.close()
    }
  })
}

async function shouldUseRAG(message: string, _history: unknown[]): Promise<boolean> {
  // Use a cheap model to determine if RAG is needed
  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [
      {
        role: 'system',
        content: 'Determine if this question needs knowledge retrieval. Answer only "yes" or "no".'
      },
      {
        role: 'user',
        content: message
      }
    ],
    temperature: 0
  })

  return response.choices[0].message.content?.toLowerCase().includes('yes') || false
}
