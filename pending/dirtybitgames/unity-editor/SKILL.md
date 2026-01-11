---
name: unity-editor
description: Remote control Unity Editor via CLI using unityctl. Use when working with Unity projects to launch/stop editor, enter/exit play mode, compile scripts, view logs, load scenes, run tests, capture screenshots, or execute C# code for debugging. Activate when user mentions Unity, play mode, compilation, or needs to interact with a running Unity Editor.
---

# unityctl - Unity Editor Remote Control

Control a running Unity Editor from the command line without batch mode.

## Instructions

### Setup (Required First)
1. Start the bridge daemon: `unityctl bridge start`
2. Launch Unity: `unityctl editor run` or manually open the project in Unity Editor
3. Verify connection: `unityctl status`

### Refresh Assets After Script Changes

After modifying C# scripts, refresh assets to compile:

```bash
unityctl asset refresh
```

Returns compilation errors directly in the output (non-zero exit code on failure). Fix errors and re-run until compilation succeeds before entering play mode.

### Common Commands

**Status & Bridge:**
```bash
unityctl status           # Check Unity running, bridge, and connection status
unityctl bridge start     # Start bridge daemon (runs in background)
unityctl bridge stop      # Stop bridge
```

**Editor Lifecycle:**
```bash
unityctl editor run         # Launch Unity Editor (auto-detects version)
unityctl editor stop        # Stop running Unity Editor
```

**Play Mode:**
```bash
unityctl play enter       # Enter play mode
unityctl play exit        # Exit play mode
```

**Logs:**
```bash
unityctl logs                 # Show all logs since last clear (auto-clears on play enter and compile)
unityctl logs -n 50           # Limit to last 50 entries
unityctl logs --stack         # Show stack traces for log entries
unityctl logs --full          # Show full history (ignore clear boundary)
```

**Scenes:**
```bash
unityctl scene list                            # List scenes
unityctl scene load Assets/Scenes/Main.unity   # Load scene
```

**Testing:**
```bash
unityctl test run                    # Run edit mode tests
unityctl test run --mode playmode    # Play mode tests
```

**Screenshots:**
```bash
unityctl screenshot capture          # Capture screenshot
```

### Script Execution (Debugging Power Tool)

Execute arbitrary C# in the running editor via Roslyn. Invaluable for debugging and automation.

```cs
// tmp/get-version.cs
using UnityEngine;

public class Script
{
    public static object Main()
    {
        return Application.version;
    }
}
```

```bash
unityctl script execute -f tmp/get-version.cs
```

You can also execute code directly with `-c`:
```bash
unityctl script execute -c "using UnityEngine; public class Script { public static object Main() { return Application.version; } }"
```

Scripts must define a class with a `public static object Main()` method. The return value is JSON-serialized.

### Getting Help

```bash
unityctl --help              # List all commands
unityctl <command> --help    # Command-specific help
```

## Examples

**Workflow: Edit script, compile, and test:**
```bash
# After editing C# files...
unityctl asset refresh       # Returns compilation errors if any
unityctl play enter
unityctl logs                # Check runtime logs (shows all since play enter)
unityctl play exit
```

**Debug: Find all GameObjects in scene:**
```cs
// tmp/find-objects.cs
using UnityEngine;

public class Script
{
    public static object Main()
    {
        return GameObject.FindObjectsOfType<GameObject>().Length;
    }
}
```
```bash
unityctl script execute -f tmp/find-objects.cs
```

**Debug: Inspect Player position:**
```cs
// tmp/find-player.cs
using UnityEngine;

public class Script
{
    public static object Main()
    {
        var go = GameObject.Find("Player");
        return go?.transform.position.ToString() ?? "not found";
    }
}
```
```bash
unityctl script execute -f tmp/find-player.cs
```

**Debug: Log message to Unity console:**
```cs
// tmp/log-message.cs
using UnityEngine;

public class Script
{
    public static object Main()
    {
        Debug.Log("Hello from CLI");
        return "logged";
    }
}
```
```bash
unityctl script execute -f tmp/log-message.cs
```

## Best Practices

- Run `unityctl status` to check overall project status before running commands
- Always run `unityctl asset refresh` after modifying C# files before entering play mode
- For script execution, write scripts to `tmp/<scriptname>.cs` and execute with `-f`

## Troubleshooting

Run `unityctl status` first to diagnose issues.

| Problem | Solution |
|---------|----------|
| Bridge not responding | `unityctl bridge stop` then `unityctl bridge start` |
| Editor not connected to newly started bridge | Normal, editor plugin uses exponential backoff, up to 30 seconds |
| Connection lost after compile | Normal - domain reload. Auto-reconnects. |
| "Project not found" | Run from project directory or use `--project` flag |
| Editor not found | Use `--unity-path` to specify Unity executable |
