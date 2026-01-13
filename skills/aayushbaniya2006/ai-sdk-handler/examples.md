# AI SDK Examples

This document provides comprehensive examples for using the Vercel AI SDK in Next.js App Router.

## 1. Basic Chat (Streaming Text)

**Route**: `src/app/api/app/chat/route.ts`
**Client**: `src/components/chat.tsx`

### Server
```typescript
import { openai } from '@/lib/ai';
import { streamText, convertToCoreMessages } from 'ai';

export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4o'),
    messages: convertToCoreMessages(messages),
    system: 'You are a helpful assistant.',
  });

  return result.toDataStreamResponse();
}
```

### Client
```typescript
'use client';
import { useChat } from '@ai-sdk/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();
  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>{m.role}: {m.content}</div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
      </form>
    </div>
  );
}
```

## 2. Generative UI (RSC)

Dynamically render React components from the server based on LLM decisions.

**Route**: `src/app/api/app/chat/generative/route.ts`

```typescript
import { openai } from '@/lib/ai';
import { streamUI } from "@ai-sdk/rsc"  
import { z } from 'zod';
import { WeatherCard } from '@/components/weather-card';
import { LoadingSpinner } from '@/components/ui/loading';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamUI({
    model: openai('gpt-4o'),
    messages,
    text: ({ content, done }) => {
      if (done) return <div>{content}</div>;
      return <div>{content}...</div>;
    },
    tools: {
      getWeather: {
        description: 'Get weather for a location',
        parameters: z.object({ location: z.string() }),
        generate: async ({ location }) => {
          // Fetch data...
          const weather = { temp: 72, condition: 'Sunny' }; 
          return <WeatherCard location={location} data={weather} />;
        },
      },
    },
  });

  return result.value;
}
```

## 3. Structured Object Generation

Extract typed data (JSON) from text. Perfect for form filling or data extraction.

**Route**: `src/app/api/app/generate/object/route.ts`

```typescript
import { openai } from '@/lib/ai';
import { generateObject } from 'ai';
import { z } from 'zod';

export async function POST(req: Request) {
  const { prompt } = await req.json();

  const { object } = await generateObject({
    model: openai('gpt-4o'),
    schema: z.object({
      recipe: z.object({
        name: z.string(),
        ingredients: z.array(z.object({ name: z.string(), amount: z.string() })),
        steps: z.array(z.string()),
      }),
    }),
    prompt,
  });

  return Response.json(object);
}
```

## 4. Agents & Workflows (with Inngest)

Handle long-running, multi-step agent workflows that might exceed serverless timeouts.

**File**: `src/inngest/functions/agents/researcher.ts`

```typescript
import { inngest } from "@/lib/inngest/client";
import { openai } from "@/lib/ai";
import { generateText } from "ai";

export const researchAgent = inngest.createFunction(
  { id: "research-agent" },
  { event: "agent/research.start" },
  async ({ event, step }) => {
    const { topic } = event.data;

    // Step 1: Plan
    const plan = await step.run("create-plan", async () => {
      const { text } = await generateText({
        model: openai("gpt-4o"),
        prompt: `Create a step-by-step research plan for: ${topic}`,
      });
      return text;
    });

    // Step 2: Loop Control (Iterative Research)
    // Example of a fixed loop. For dynamic loops, handle carefully with step IDs.
    const findings = [];
    const steps = plan.split('\n').filter(s => s.trim().length > 0).slice(0, 3); // Limit to 3 steps

    for (let i = 0; i < steps.length; i++) {
      const finding = await step.run(`execute-step-${i}`, async () => {
        const { text } = await generateText({
          model: openai("gpt-4o"),
          prompt: `Execute research step: ${steps[i]}`,
        });
        return text;
      });
      findings.push(finding);
    }

    // Step 3: Synthesize
    const summary = await step.run("synthesize", async () => {
      const { text } = await generateText({
        model: openai("gpt-4o"),
        prompt: `Synthesize these findings into a report:\n${findings.join('\n\n')}`,
      });
      return text;
    });

    return { summary };
  }
);
```

## 5. Caching Responses

Cache LLM responses to save costs and improve speed for identical queries.

```typescript
import { unstable_cache } from 'next/cache';
import { generateText } from 'ai';
import { openai } from '@/lib/ai';

const getCachedResponse = unstable_cache(
  async (prompt: string) => {
    const { text } = await generateText({
      model: openai('gpt-4o'),
      prompt,
    });
    return text;
  },
  ['llm-response'],
  { revalidate: 3600 } // Cache for 1 hour
);
```

## 6. Streaming Data (Server to Client)

Send custom data alongside the text stream.

**Route**: `src/app/api/app/chat/route.ts`

```typescript
import { openai } from '@/lib/ai';
import { streamText, StreamData } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const data = new StreamData();

  const result = await streamText({
    model: openai('gpt-4o'),
    messages,
    onFinish() {
      data.append({ type: 'usage', value: '100 tokens' });
      data.close();
    },
  });

  return result.toDataStreamResponse({ data });
}
```

**Client**: `useChat` automatically handles this via the `data` property.

```typescript
const { data } = useChat();
// data is an array of the appended objects
```

## 7. Reading UI Message Streams (Advanced)

If you need to manually read the stream on the client (e.g., without `useChat`).

```typescript
import { readStreamableValue } from 'ai/rsc';

// Client Component
export function StreamReader({ stream }: { stream: any }) {
  const [content, setContent] = useState('');

  useEffect(() => {
    (async () => {
      for await (const value of readStreamableValue(stream)) {
        setContent(value);
      }
    })();
  }, [stream]);

  return <div>{content}</div>;
}
```

## 8. Handling Backpressure

The `streamText` and `streamUI` functions automatically handle backpressure when using `toDataStreamResponse()`.
However, if manually processing streams, ensure you respect the controller's desired size.

```typescript
// Manual stream handling example (usually not needed with AI SDK helpers)
const stream = new ReadableStream({
  async start(controller) {
    // ... generate chunks ...
    if (controller.desiredSize && controller.desiredSize <= 0) {
       // pause generation if consumer is slow
    }
    controller.enqueue(chunk);
  }
});
```

## 9. Multimodal Chat (Images)

Sending images with `useChat`.

```typescript
// Client
const { input, handleInputChange, handleSubmit } = useChat();
const [files, setFiles] = useState<FileList | undefined>(undefined);

return (
  <form onSubmit={e => handleSubmit(e, { experimental_attachments: files })}>
    <input type="file" onChange={e => setFiles(e.target.files)} />
    <input value={input} onChange={handleInputChange} />
    <button type="submit">Send</button>
  </form>
);
```

