# Page.canScreencast

Scope: This method documents a LynxView-specific Page extension. For WebView targets, use the target browser's Chrome DevTools Protocol support instead.

- `Page.canScreencast` - Check screencast support
- Input: None
- Output: `{result: boolean}`
- Description: Reports whether the target supports screencast commands.

## LynxView behavior

- The current native handler always returns `{result: true}`.
- It does not inspect the page, platform, or request parameters, so this result is not a guarantee that every screencast command is implemented.
