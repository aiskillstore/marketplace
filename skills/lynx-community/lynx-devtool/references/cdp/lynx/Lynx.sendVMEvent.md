# Lynx.sendVMEvent

Scope: This is a LynxView-specific CDP extension. For WebView targets, use standard Chrome DevTools Protocol runtime or page APIs instead; this method may return `method not found`.

- `Lynx.sendVMEvent` - Send VM event
- Input: `{event: string, data?: Object}`
- Output: `{}`
- Description: Sends an event to the Lynx virtual machine
