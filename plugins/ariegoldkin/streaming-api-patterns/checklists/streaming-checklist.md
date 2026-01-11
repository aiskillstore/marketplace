# Streaming API Implementation Checklist

## Server-Sent Events (SSE)

### Setup
- [ ] Set correct Content-Type: `text/event-stream`
- [ ] Disable caching with `Cache-Control: no-cache`
- [ ] Set `Connection: keep-alive`
- [ ] Disable nginx buffering with `X-Accel-Buffering: no`

### Data Format
- [ ] Prefix messages with `data: `
- [ ] End messages with `\n\n`
- [ ] Send keepalive comments every 30s (`: keepalive\n\n`)
- [ ] Use JSON for structured data
- [ ] Send `[DONE]` marker when complete

### Error Handling
- [ ] Handle client disconnection (`req.signal.aborted`)
- [ ] Catch and send errors as SSE messages
- [ ] Close stream properly in finally block
- [ ] Implement server-side reconnection logic

### Client
- [ ] Use EventSource API
- [ ] Handle automatic reconnection
- [ ] Implement error handling
- [ ] Close connection when done
- [ ] Handle browser connection limits (max 6 per domain)

## WebSockets

### Server
- [ ] Implement ping/pong heartbeat
- [ ] Handle connection upgrades
- [ ] Validate incoming messages
- [ ] Broadcast to multiple clients efficiently
- [ ] Track active connections

### Client
- [ ] Implement reconnection with exponential backoff
- [ ] Queue messages during disconnection
- [ ] Handle connection states (connecting, open, closing, closed)
- [ ] Implement timeout for slow connections

### Security
- [ ] Validate origin headers
- [ ] Authenticate connections
- [ ] Rate limit messages per client
- [ ] Sanitize message content
- [ ] Implement message size limits

## Backpressure & Performance

- [ ] Monitor buffer sizes
- [ ] Implement flow control
- [ ] Pause stream when consumer is slow
- [ ] Use chunking for large data
- [ ] Compress data (gzip/brotli)
- [ ] Batch small messages
- [ ] Set appropriate timeouts

## LLM Streaming

- [ ] Stream tokens as they arrive
- [ ] Handle partial Unicode characters
- [ ] Implement stop generation
- [ ] Show typing indicator
- [ ] Handle stream interruption
- [ ] Measure time-to-first-token

## Testing

- [ ] Test with slow networks
- [ ] Test reconnection scenarios
- [ ] Test with multiple concurrent clients
- [ ] Load test with expected traffic
- [ ] Test error cases (server crash, network issues)
- [ ] Verify memory doesn't leak over long connections
