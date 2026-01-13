/**
 * Server-Sent Events (SSE) Endpoint Template
 * For Next.js App Router or any streaming-capable framework
 */

// Next.js Route Handler (app/api/stream/route.ts)
export async function GET(req: Request) {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Send initial connection message
        controller.enqueue(encoder.encode('data: {"type":"connected"}\n\n'))

        // Example: Stream data source
        const data = await fetchDataSource()

        for (const item of data) {
          // Check if client disconnected
          if (req.signal.aborted) break

          // Send data
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify(item)}\n\n`)
          )

          // Simulate delay
          await new Promise(resolve => setTimeout(resolve, 100))
        }

        // Send completion
        controller.enqueue(encoder.encode('data: [DONE]\n\n'))
      } catch (error) {
        controller.enqueue(
          encoder.encode(`data: {"error":"${error.message}"}\n\n`)
        )
      } finally {
        controller.close()
      }
    }
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no', // Disable nginx buffering
    }
  })
}

// Client Usage
export class StreamClient {
  private eventSource: EventSource | null = null

  connect(url: string, onMessage: (data: any) => void) {
    this.eventSource = new EventSource(url)

    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.close()
        return
      }

      const data = JSON.parse(event.data)
      onMessage(data)
    }

    this.eventSource.onerror = () => {
      console.error('SSE error, reconnecting...')
      // EventSource automatically reconnects
    }
  }

  close() {
    this.eventSource?.close()
  }
}
