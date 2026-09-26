# Lynx.getScreenshot

Scope: This is a LynxView-specific CDP extension. For WebView targets, use
standard Chrome DevTools Protocol screenshot APIs instead; this method may
return `method not found`.

- `Lynx.getScreenshot` - Request a Lynx screenshot or card preview
- Input: None
- Output: None
- Description: Asks the platform to send a Lynx screenshot or card preview.

## Notes

- The native handler does not read request parameters.
- Android and Darwin delegate the request to their card-preview platform hook.
- The current native handler does not send a CDP response after invoking that
  platform hook.
- If the UI task runner or platform facade is unavailable, the current handler
  does not send an explicit CDP response.

## Example

```bash
agent-lynx cdp -m Lynx.getScreenshot
```
