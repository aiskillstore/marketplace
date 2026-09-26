# Runtime.discardConsoleEntries

> Note: Call `Runtime.enable` on the same session and thread before invoking this CDP method.

- `Runtime.discardConsoleEntries` - Discards collected exceptions and console API calls.
- Input: None
- Output: No CLI response on current Android Lynx runtime.
- Description: Discards all collected console log messages (commonly used when the frontend DevTools clicks to clear the console).

## Notes

- On the tested Android Lynx runtime, `lynx-devtool cdp -m Runtime.discardConsoleEntries` receives no response and exits with `No response found`.
