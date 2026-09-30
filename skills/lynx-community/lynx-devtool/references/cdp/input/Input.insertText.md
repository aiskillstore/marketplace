# Input.insertText

Scope: This page documents the LynxView implementation of `Input.insertText`. For WebView targets, use the standard Chrome DevTools Protocol `Input.insertText` documentation as the source of truth.

- `Input.insertText` - Insert text into the focused input
- Input: `{text: string}`
- Output: `{}`
- Description: Inserts text into the currently focused native text input, without synthesizing individual key events.

## Usage

Focus the target first, then insert text:

```bash
agent-lynx cdp -m DOM.focus '{"nodeId": 42}'
agent-lynx cdp -m Input.insertText '{"text": "hello"}'
```

The text is committed at the input's current selection. It may replace the selected range rather than always appending to the existing value.

## Platform Support

- Native text insertion is implemented for Android and iOS LynxView targets.
- The method returns `{}` after the request is dispatched. If no compatible text input is focused, the request is acknowledged but has no effect.
- Android requires the focused view to be an `EditText`; iOS requires the first responder to implement `UITextInput`.
- Other LynxView platforms may acknowledge the request without inserting text.

## Notes

- Use `DOM.focus` with the target's `nodeId` before this method. Calling `Input.insertText` without a focused input is a no-op.
- Text is inserted as one commit, so spaces, punctuation, digits, emoji, and IME-style input are supported without sending key events one by one.
