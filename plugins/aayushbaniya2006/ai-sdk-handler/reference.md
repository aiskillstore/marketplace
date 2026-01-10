# AI SDK Handler Reference (Vercel AI SDK)

## Core Setup
Install dependencies: `npm install ai @ai-sdk/openai @ai-sdk/anthropic zod`

### 1. Provider Configuration
`src/lib/ai/index.ts`
```typescript
import { createOpenAI } from '@ai-sdk/openai';
import { createAnthropic } from '@ai-sdk/anthropic';

export const openai = createOpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export const anthropic = createAnthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});
```

## Streaming Chat API (Route Handler)
`src/app/api/chat/route.ts`

```typescript
import { openai } from '@/lib/ai';
import { streamText, convertToCoreMessages } from 'ai';
import withAuthRequired from "@/lib/auth/withAuthRequired";

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export const POST = withAuthRequired(async (req, { session }) => {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4o'),
    messages: convertToCoreMessages(messages),
    system: "You are a helpful assistant.",
    async onFinish({ text, usage }) {
        // Optional: Log usage or save chat history to DB
        console.log(`User ${session.user.id} used ${usage.totalTokens} tokens.`);
    }
  });

  return result.toDataStreamResponse();
});
```

## Client-Side Chat UI
`src/components/chat-ui/chat-bot.tsx`

```typescript
'use client';

import { useChat } from '@ai-sdk/react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function ChatBot() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat', // defaults to '/api/chat'
    onError: (error) => {
        console.error("Chat error:", error);
    }
  });

  return (
    <div className="flex flex-col h-[500px] border rounded-md">
      <ScrollArea className="flex-1 p-4">
        {messages.map(m => (
          <div key={m.id} className={`mb-4 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block p-2 rounded-lg ${m.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'}`}>
              <span className="font-bold text-xs block mb-1">{m.role === 'user' ? 'You' : 'AI'}</span>
              {m.content}
            </div>
          </div>
        ))}
      </ScrollArea>
      <form onSubmit={handleSubmit} className="p-4 border-t flex gap-2">
        <Input value={input} onChange={handleInputChange} placeholder="Say something..." />
        <Button type="submit" disabled={isLoading}>Send</Button>
      </form>
    </div>
  );
}
```

## Generative UI (Streaming Components)
`src/app/api/chat/generative/route.ts`

```typescript
import { openai } from '@/lib/ai';
import { streamUI } from "@ai-sdk/rsc"  
import { z } from 'zod';
import { WeatherCard } from '@/components/chat-ui/weather-card'; // Example component

export const POST = async (req: Request) => {
  const { messages } = await req.json();

  const result = await streamUI({
    model: openai('gpt-4o'),
    messages,
    text: ({ content }) => <div>{content}</div>,
    tools: {
      getWeather: {
        description: 'Get the weather for a location',
        parameters: z.object({
          location: z.string(),
        }),
        generate: async ({ location }) => {
          const weather = "Sunny"; // Mock data
          return <WeatherCard location={location} weather={weather} />;
        },
      },
    },
  });

  return result.value;
};
```

## Object Generation (Structured JSON)
Useful for extracting data or creating database records.

`src/app/api/app/generate-itinerary/route.ts`

```typescript
import { openai } from '@/lib/ai';
import { generateObject } from 'ai';
import { z } from 'zod';
import withAuthRequired from "@/lib/auth/withAuthRequired";

export const POST = withAuthRequired(async (req) => {
  const { destination } = await req.json();

  const { object } = await generateObject({
    model: openai('gpt-4o'),
    schema: z.object({
      destination: z.string(),
      activities: z.array(z.object({
        name: z.string(),
        duration: z.string(),
      })),
    }),
    prompt: `Create a day trip itinerary for ${destination}`,
  });

  return Response.json(object);
});
```

## Background Agents (Inngest Integration)
For long-running agent workflows that might timeout a standard request.

`src/inngest/functions/agents/researcher.ts`

```typescript
import { inngest } from "@/lib/inngest/client";
import { openai } from "@/lib/ai";
import { generateText } from "ai";

export const researchAgent = inngest.createFunction(
    { id: "research-agent" },
    { event: "app/agent.research" },
    async ({ event, step }) => {
        const { topic, userId } = event.data;

        // Step 1: Generate Research Plan
        const plan = await step.run("generate-plan", async () => {
            const { text } = await generateText({
                model: openai("gpt-4o"),
                prompt: `Create a research plan for: ${topic}`
            });
            return text;
        });

        // Step 2: Execute Research (Simulated loop)
        // See: https://ai-sdk.dev/docs/agents/loop-control
        const summary = await step.run("summarize", async () => {
             const { text } = await generateText({
                model: openai("gpt-4o"),
                prompt: `Summarize this plan: ${plan}`
            });
            return text;
        });

        return { plan, summary };
    }
);
```

