# Lynx DevTool Supported CDP Methods

This document lists all Chrome DevTools Protocol (CDP) methods supported by Lynx DevTool, organized by domain.

WebView note: if the selected session is a WebView (for example `type: "web"` or an HTTP/HTTPS URL), use the standard Chrome DevTools Protocol documentation as the source of truth for CDP method availability and parameters. Lynx-specific extensions documented here are LynxView-only and may return `method not found` on WebView targets.

Use `agent-lynx cdp --thread main ...` to target the main-thread VM. When `--thread main` is used, only `Debugger.*`, `Runtime.*`, `HeapProfiler.*`, and `Profiler.*` methods are supported. If `--thread` is omitted, CDP requests target the background thread.

## Domains

- [DOM Methods](dom/index.md)
- [CSS Methods](css/index.md)
- [Page Methods](page/index.md)
- [Input Methods](input/index.md)
- [Overlay Methods](overlay/index.md)
- [Lynx Specific Methods](lynx/index.md)
- [Debugger Methods](debugger/index.md)
- [Runtime Methods](runtime/index.md)
- [Performance Methods](performance/index.md)
- [Memory Methods](memory/index.md)
- [UITree Methods](uitree/index.md)
- [WhiteBoard (session storage) Methods](whiteboard/index.md)
- [HeapProfiler Methods](heapprofiler/index.md)
- [IO Methods](io/index.md)
- [LayerTree Methods](layertree/index.md)
- [SystemInfo Methods](systeminfo/index.md)
- [Template Methods](template/index.md)
- [Tracing Methods](tracing/index.md)
