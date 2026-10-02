---
name: webview2-winui
description: "Embeds web content in WinUI 3 through WebView2. Use for virtual host mapping, native/web messages, lifecycle, and desktop packaging; not generic browser React development."
---

# WebView2 in WinUI 3

Embed Chromium-powered web content in WinUI 3 desktop applications. Use when hosting a React/Vite SPA, dashboard, or rich web panel inside a native Windows app.

## Loading local content

### Virtual host name mapping (preferred)

```csharp
coreWebView2.SetVirtualHostNameToFolderMapping(
    "app.example",                                 // virtual hostname
    distFolderPath,                                // local folder with index.html + assets
    CoreWebView2HostResourceAccessKind.Deny);      // minimal cross-origin access

webView.Source = new Uri("https://app.example/index.html");
```

- Resolution happens in the WebView2 process — faster than `WebResourceRequested` (which routes through host UI thread).
- Use a domain you control or a clearly fake TLD. **Avoid `.local`** — it causes DNS resolution delays.
- Use `Deny` unless other origins genuinely need access to these resources.
- Use distinct virtual hosts for content from different trust levels.
- Relative `folderPath` resolves relative to the exe directory.

### Prefer virtual host mapping for static assets

`WebResourceRequested` routes requests through the host and can add UI-thread work. Use it when request interception or dynamic responses are required; prefer virtual host mapping for ordinary static assets.

### Media caveat

> Due to a current implementation limitation, media files accessed using virtual host name can be very slow to load.

Benchmark media against the deployed Runtime. If mapped files load slowly, consider an HTTPS media endpoint or native playback; HTML5 video is not categorically unsupported.

## Initialization pattern

```csharp
public sealed partial class MyPage : Page
{
    public MyPage()
    {
        InitializeComponent();
        Loaded += OnLoaded;
    }

    private async void OnLoaded(object sender, RoutedEventArgs args)
    {
        Loaded -= OnLoaded;
        try
        {
            await MyWebView.EnsureCoreWebView2Async();
            MyWebView.CoreWebView2.SetVirtualHostNameToFolderMapping(
                "app.example", ResolveDistFolder(),
                CoreWebView2HostResourceAccessKind.Deny);
            MyWebView.Source = new Uri("https://app.example/index.html");
        }
        catch (Exception error)
        {
            ShowInitializationError(error); // app-owned error UI and retry path
        }
    }
}
```

- Observe the initialization task; do not discard its exception. If using `CoreWebView2Initialized`, also check its `Exception` and avoid configuring the control twice.
- Show a loading fallback (ProgressRing); on `NavigationCompleted`, check `IsSuccess` and display an error/retry state when navigation fails.

## XAML

```xml
<Grid>
    <controls:WebView2 x:Name="MyWebView" DefaultBackgroundColor="Transparent" />

    <Border x:Name="Fallback" HorizontalAlignment="Center" VerticalAlignment="Center">
        <StackPanel Spacing="8">
            <ProgressRing IsActive="True" Width="24" Height="24" />
            <TextBlock Text="Loading…" FontSize="12" />
        </StackPanel>
    </Border>
</Grid>
```

- `DefaultBackgroundColor="Transparent"` — native background shows through while loading.
- **Do NOT** set `Source` in XAML when using virtual host mapping — CoreWebView2 isn't initialized yet.

## Native ↔ Web messaging

### C# → JavaScript

```csharp
coreWebView2.PostWebMessageAsJson(json); // synchronous void API
// or
await coreWebView2.ExecuteScriptAsync("window.refreshView?.()"); // trusted code only
```

### JavaScript → C#

```typescript
window.chrome.webview.postMessage({ type: "command", payload });
```

```csharp
coreWebView2.WebMessageReceived += (_, args) =>
{
    if (!Uri.TryCreate(args.Source, UriKind.Absolute, out var source) ||
        source.Scheme != "https" || source.Host != "app.example" ||
        !source.IsDefaultPort) return;
    try
    {
        var msg = JsonSerializer.Deserialize<Message>(args.WebMessageAsJson);
        if (msg is null || !IsAllowedMessage(msg)) return;
        HandleMessage(msg); // validate and authorize each allowed command
    }
    catch (JsonException)
    {
        // Reject malformed input without invoking native capabilities.
    }
};
```

`Message`, `IsAllowedMessage`, and `HandleMessage` are app-defined. Validate payload size, shape, and command permissions before native work. Check the current document origin before sending sensitive data to the web side; restrict top-level/frame navigation and new windows to the intended destinations.

Prefer a small message protocol when it fits. Expose host objects only when needed, with minimal capabilities and explicit cleanup. Neither messaging nor host objects are safe without an origin and authorization boundary.

## Performance

### Startup

- Keep the UDF (User Data Folder) on a fast local drive — never a network share.
- Share one `CoreWebView2Environment` across all WebView2 controls.
- Use the Evergreen Runtime (auto-updates, always current).

### Memory

- Set `MemoryUsageTargetLevel = Low` on hidden/inactive WebViews.
- Restore to `Normal` when active again.

### Communication

- Prefer web messages over host objects.
- Cache data on the web side — don't round-trip to C# for every render.

### Web content for embedded use

- Cap `dpr` to `[1, 1.5]` — WebView2 inherits system DPI which can be 2x+.
- Disable antialiasing for decorative 3D.
- Use `powerPreference: "low-power"` for non-critical rendering.
- Lazy-load heavy libraries (`React.lazy()` + `Suspense`).

## Production bundling

### Build

```bash
npm run build    # Vite/webpack → dist/ with index.html + hashed assets
```

### Include in the WinUI project

**Option A — MSBuild content items (build and publish):**

```xml
<ItemGroup>
  <Content Include="..\MyWebProject\dist\**\*">
    <Link>webview-dist\%(RecursiveDir)%(Filename)%(Extension)</Link>
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    <CopyToPublishDirectory>PreserveNewest</CopyToPublishDirectory>
  </Content>
</ItemGroup>
```

Build the web assets before MSBuild evaluates these items. Verify the packaged/published output contains `webview-dist/index.html`; a missing source glob must not silently produce an empty app. Use clean staging on releases so removed assets do not linger.

**Option B — Manual copy at publish time:**

```bash
robocopy src/MyWebProject/dist dist-output/webview-dist /E
```

### Resolve at runtime

```csharp
static string ResolveDistFolder()
{
    var exe = AppContext.BaseDirectory;
    var prod = Path.Combine(exe, "webview-dist");
    if (Directory.Exists(prod)) return prod;

    // Dev: sibling web project
    var dev = Path.GetFullPath(Path.Combine(exe, "..", "..", "..", "..", "MyWebProject", "dist"));
    return Directory.Exists(dev) ? dev : prod;
}
```

## Theme synchronization

Match your CSS custom properties to the native app's design tokens so the embedded web content feels native:

- Use the same font family (`Segoe UI Variable` on Windows).
- Mirror background, surface, accent, and text colors between XAML resource dictionaries and CSS variables.
- Keep border radii and spacing proportional.

## Anti-patterns

| Don't | Do instead |
|---|---|
| Set `Source` in XAML with virtual host mapping | Set it in code-behind after `CoreWebView2Initialized` |
| Use `.local` TLD for virtual hosts | Use a real domain or clearly fake TLD |
| Use `WebResourceRequested` for static files | Use `SetVirtualHostNameToFolderMapping` |
| Expose large .NET graphs via `AddHostObjectToScript` | Use `PostWebMessageAsJson` |
| Assume virtual-host media performs like ordinary HTTPS | Benchmark; choose HTTPS or native playback if needed |
| Run web assets from a network share | Copy to a local folder |

## Reference

- [Working with local content in WebView2](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/working-with-local-content)
- [WebView2 performance best practices](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/performance)
- [SetVirtualHostNameToFolderMapping API](https://learn.microsoft.com/en-us/dotnet/api/microsoft.web.webview2.core.corewebview2.setvirtualhostnametofoldermapping)
- [PostWebMessageAsJson API](https://learn.microsoft.com/en-us/dotnet/api/microsoft.web.webview2.core.corewebview2.postwebmessageasjson)
- [Develop secure WebView2 apps](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/security)
