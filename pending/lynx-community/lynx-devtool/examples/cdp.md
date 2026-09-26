# Send CDP Command

Send a Chrome DevTools Protocol (CDP) command to a specific session.

> Note that Lynx only supports a part of the standard CDP command.
> You **MUST** read [Supported CDP Methods](../references/cdp/index.md) before sending a CDP command.

```bash
agent-lynx cdp -m <method> [options] [params]
```

- `-m, --method <method>`: The CDP method name (e.g., `DOM.getDocument`, `Runtime.evaluate`).
- `-c, --client <clientId>`: (Optional) The Client ID. If omitted, uses the first available client.
- `-s, --session <sessionId>`: (Optional) The Session ID. If omitted, uses the latest available session.
- `[params]`: (Optional) JSON string of parameters for the command.

Example:

```bash
# Get the document root
agent-lynx cdp -m DOM.getDocument

# Evaluate JavaScript
agent-lynx cdp -m Runtime.evaluate '{"expression": "2 + 2"}'
```
