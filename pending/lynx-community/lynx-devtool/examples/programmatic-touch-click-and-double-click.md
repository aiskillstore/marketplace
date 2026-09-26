# Programmatic Touch: Click and Double Click

This example uses the Connector API directly (no CLI command chaining) and sends multiple `Input.emulateTouchFromMouseEvent` messages via `connector.sendCDPStream`.

It demonstrates:

- Single click (press + release)
- Double click via two rapid clicks in one stream
- Multi-step gesture sequencing in one stream

```js
import { createDefaultConnector } from "agent-lynx/connector";
import { ReadableStream } from "node:stream/web";

const connector = createDefaultConnector();

const clients = await connector.listClients();
if (clients.length === 0) {
  throw new Error("No Lynx clients found");
}

const client = clients[0];
const sessions = await connector.sendListSessionMessage(client.id);
const session = sessions.at(-1);
if (!session) {
  throw new Error("No Lynx sessions found");
}

const clientId = client.id;
const sessionId = session.session_id;

async function sendInputStream(messages) {
  await using outputStream = await connector.sendCDPStream(
    clientId,
    sessionId,
    ReadableStream.from(messages),
  );

  // Drain stream to ensure requests are delivered and responses/events are consumed.
  for await (const _ of outputStream) {
    // No-op
  }
}

function centerOfQuad(quad) {
  const xs = [quad[0], quad[2], quad[4], quad[6]];
  const ys = [quad[1], quad[3], quad[5], quad[7]];

  return {
    x: (Math.min(...xs) + Math.max(...xs)) / 2,
    y: (Math.min(...ys) + Math.max(...ys)) / 2,
  };
}

async function getPointFromDom(selector) {
  const document = await connector.sendCDPMessage(
    clientId,
    sessionId,
    "DOM.getDocument",
    { depth: 0 },
  );
  const rootNodeId = document.result.root.nodeId;

  const query = await connector.sendCDPMessage(
    clientId,
    sessionId,
    "DOM.querySelector",
    { nodeId: rootNodeId, selector },
  );
  const nodeId = query.result.nodeId;
  if (!nodeId) {
    throw new Error(`No node matched selector: ${selector}`);
  }

  await connector.sendCDPMessage(
    clientId,
    sessionId,
    "DOM.scrollIntoViewIfNeeded",
    { nodeId },
  );

  const box = await connector.sendCDPMessage(
    clientId,
    sessionId,
    "DOM.getBoxModel",
    { nodeId },
  );
  const point = centerOfQuad(box.result.model.content);

  const hit = await connector.sendCDPMessage(
    clientId,
    sessionId,
    "DOM.getNodeForLocation",
    point,
  );
  if (!hit.result.nodeId) {
    throw new Error(
      `Computed point did not hit a node: ${JSON.stringify(point)}`,
    );
  }
  console.log("tap target", { selector, nodeId, point, hit: hit.result });

  return point;
}

async function run() {
  // Replace the selector with a stable target in your page.
  // The returned point is already in the CDP logical coordinate space used by Input.
  const { x, y } = await getPointFromDom("[lynx-test-tag='target']");

  // Single click: 2 Input CDP messages in one stream
  await sendInputStream([
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mousePressed",
        x,
        y,
        button: "left",
        clickCount: 1,
        timestamp: Date.now(),
      },
    },
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mouseReleased",
        x,
        y,
        button: "left",
        clickCount: 1,
        timestamp: Date.now() + 1,
      },
    },
  ]);

  // Double click: 4 Input CDP messages in one stream
  await sendInputStream([
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mousePressed",
        x,
        y,
        button: "left",
        clickCount: 1,
        timestamp: Date.now(),
      },
    },
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mouseReleased",
        x,
        y,
        button: "left",
        clickCount: 1,
        timestamp: Date.now() + 1,
      },
    },
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mousePressed",
        x,
        y,
        button: "left",
        clickCount: 2,
        timestamp: Date.now() + 80,
      },
    },
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mouseReleased",
        x,
        y,
        button: "left",
        clickCount: 2,
        timestamp: Date.now() + 81,
      },
    },
  ]);

  // Multi-event sequence example (press -> move -> release) in one stream
  await sendInputStream([
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mousePressed",
        x,
        y,
        button: "left",
        clickCount: 1,
        timestamp: Date.now(),
      },
    },
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mouseMoved",
        x: x + 20,
        y: y + 20,
        button: "left",
        clickCount: 1,
        timestamp: Date.now() + 1,
      },
    },
    {
      method: "Input.emulateTouchFromMouseEvent",
      params: {
        type: "mouseReleased",
        x: x + 20,
        y: y + 20,
        button: "left",
        clickCount: 1,
        timestamp: Date.now() + 2,
      },
    },
  ]);
}

await run();
```

## Notes

- `sendCDPStream` is useful when you want to enqueue multiple CDP input messages as one operation.
- Message order in the stream controls gesture order.
- Use CDP DOM methods for click coordinates; do not pick points from screenshots.
- Points computed from `DOM.getBoxModel` can be passed directly to `Input.emulateTouchFromMouseEvent`.
- If double-click behavior is not recognized by a target component, adjust timestamp gaps and `clickCount`.
