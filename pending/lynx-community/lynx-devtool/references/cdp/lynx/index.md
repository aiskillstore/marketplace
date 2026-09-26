# Lynx Specific Methods

Scope: The `Lynx.*` methods are LynxView-specific CDP extensions. For WebView targets, use standard Chrome DevTools Protocol methods instead; these methods may return `method not found`.

## Coordinate Guide

- Use DOM CDP methods for click coordinates: `DOM.getBoxModel`, `DOM.getNodeForLocation`, and then `Input.emulateTouchFromMouseEvent`.
- `Lynx.getRectToWindow` and `Lynx.getViewLocationOnScreen` expose host window geometry and are best treated as diagnostics.
- Do not derive click points from screenshots or Lynx window geometry when a DOM node can be queried directly.
- For coordinate debugging, see [Click Coordinate Troubleshooting](../../troubleshooting/click-coordinates.md).

## Component Inspection

- [Lynx.getComponentId](Lynx.getComponentId.md) - Get a component id for a DevTool node
- [Lynx.getData](Lynx.getData.md) - Get serialized component data
- [Lynx.getProperties](Lynx.getProperties.md) - Get serialized component properties

## Position, Screenshot, and Version

- [Lynx.getRectToWindow](Lynx.getRectToWindow.md) - Get rectangle relative to window
- [Lynx.getScreenshot](Lynx.getScreenshot.md) - Request a Lynx screenshot or card preview
- [Lynx.getVersion](Lynx.getVersion.md) - Get version

## Debug Features

- [Lynx.getViewLocationOnScreen](Lynx.getViewLocationOnScreen.md) - Get view location on screen
- [Lynx.sendVMEvent](Lynx.sendVMEvent.md) - Send VM event
