---
name: pitfalls-websocket
description: "WebSocket server and client patterns with heartbeat and reconnection. Use when implementing real-time features, debugging connection issues, or reviewing WebSocket code. Triggers on: WebSocket, wss, heartbeat, reconnect, real-time."
---

# WebSocket Pitfalls

Common pitfalls and correct patterns for WebSocket implementations.

## When to Use

- Implementing WebSocket server
- Building WebSocket client with reconnection
- Debugging connection drops
- Adding heartbeat/ping-pong
- Reviewing WebSocket code

## Workflow

### Step 1: Verify Server Setup

Check WebSocket server shares HTTP port.

### Step 2: Check Heartbeat

Ensure ping/pong heartbeat is implemented.

### Step 3: Verify Client Reconnection

Confirm exponential backoff reconnection logic.

---

## Server Pattern

```typescript
const wss = new WebSocketServer({ server: httpServer }); // Same port

wss.on('connection', (ws) => {
  // Heartbeat
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });

  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      // Validate message type
    } catch {
      ws.send(JSON.stringify({ error: 'Invalid message' }));
    }
  });
});

// Heartbeat interval
setInterval(() => {
  wss.clients.forEach((ws) => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);
```

## Client Reconnection

```typescript
// Client - reconnection logic with exponential backoff
let attempt = 0;

function connect() {
  const ws = new WebSocket(url);

  ws.onopen = () => {
    attempt = 0; // Reset on successful connection
  };

  ws.onclose = () => {
    const delay = Math.min(1000 * Math.pow(2, attempt), 30000);
    attempt++;
    setTimeout(connect, delay);
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
}
```

## Message Handling

```typescript
// ✅ Always validate and type messages
interface WsMessage {
  type: 'subscribe' | 'unsubscribe' | 'ping';
  channel?: string;
}

function handleMessage(ws: WebSocket, data: string) {
  try {
    const msg: WsMessage = JSON.parse(data);

    switch (msg.type) {
      case 'subscribe':
        subscribeToChannel(ws, msg.channel);
        break;
      case 'ping':
        ws.send(JSON.stringify({ type: 'pong' }));
        break;
      default:
        ws.send(JSON.stringify({ error: 'Unknown message type' }));
    }
  } catch {
    ws.send(JSON.stringify({ error: 'Invalid JSON' }));
  }
}
```

## Quick Checklist

- [ ] WebSocket server uses same port as HTTP
- [ ] Heartbeat ping/pong every 30 seconds
- [ ] Client has reconnection with exponential backoff
- [ ] Messages validated before processing
- [ ] Connection errors logged
