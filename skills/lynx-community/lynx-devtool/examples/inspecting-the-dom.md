# Inspecting the DOM

1. List sessions to find the target session ID.
   ```bash
   agent-lynx list-sessions
   ```
2. Request the document.
   ```bash
   agent-lynx cdp -m DOM.getDocument -s <sessionId>
   ```
3. Request details of a node.
   ```bash
   agent-lynx cdp -m DOM.describeNode -s <sessionId> '{"nodeId": 1}'
   ```
