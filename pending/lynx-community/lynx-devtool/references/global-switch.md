# Global Switch Commands

`global-switch` provides first-class commands for DevTool global switches.

## Supported Keys

- `enable_devtool`
- `enable_logbox`
- `enable_debug_mode`
- `enable_dom_tree`
- `enable_quickjs_debug`
- `enable_quickjs_cache`
- `enable_v8`
- `enable_cdp_domain_dom`
- `enable_cdp_domain_css`
- `enable_cdp_domain_page`
- `enable_long_press_menu`
- `enable_highlight_touch`
- `enable_preview_screen_shot`
- `enable_pixel_copy`
- `enable_fsp_screenshot`

## Key Meanings

The descriptions below are based on Lynx Engine reference code in `.reference-repos/template-assembler`, mainly:

- `lynx/platform/android/lynx_android/src/main/java/com/lynx/devtoolwrapper/DevToolSettings.java`
- `lynx/platform/android/lynx_devtool/src/main/java/com/lynx/devtool/LynxInspectorOwner.java`
- `lynx/platform/android/lynx_devtool/src/main/java/com/lynx/devtool/LynxDevtoolEnv.java`
- `lynx/platform/darwin/common/lynx_devtool/LynxDebugBridge.mm`

- `enable_devtool`: master switch for enabling DevTool capability in app/runtime settings.
- `enable_logbox`: enable/disable LogBox panel and logbox-related debugging UI.
- `enable_debug_mode`: enable debug-mode behavior (debug library path and related debug runtime behavior).
- `enable_dom_tree`: enable DOM tree inspection support in DevTool.
- `enable_quickjs_debug`: enable QuickJS debugging bridge/capability.
- `enable_quickjs_cache`: enable QuickJS bytecode/cache-related optimization path.
- `enable_v8`: control V8 usage for JS runtime selection in DevTool scenarios.
- `enable_cdp_domain_dom`: activate CDP DOM domain via grouped env (`activated_cdp_domains`).
- `enable_cdp_domain_css`: activate CDP CSS domain via grouped env (`activated_cdp_domains`).
- `enable_cdp_domain_page`: activate CDP Page domain via grouped env (`activated_cdp_domains`).
- `enable_long_press_menu`: enable long-press developer menu behavior.
- `enable_highlight_touch`: enable touch highlight visualization in DevTool interaction.
- `enable_preview_screen_shot`: enable screenshot preview behavior used by DevTool UI flow.
- `enable_pixel_copy`: enable pixel-copy path for screenshot/capture related behavior.
- `enable_fsp_screenshot`: enable FSP screenshot collection behavior.

## Platform Notes

- Support is not perfectly symmetric across platforms.
- In current Darwin bridge code, only a subset of keys is handled directly (`enable_devtool`, `enable_logbox`, `enable_quickjs_debug`, `enable_dom_tree`, `enable_long_press_menu`, `enable_perf_metrics`).
- For unsupported keys on some platforms, `getGlobalSwitch` may return fallback values (for example `false`) instead of throwing.

## Usage

```bash
# List all keys and current values
agent-lynx global-switch list -c <clientId>

# Keep going even if some keys fail (default behavior)
agent-lynx global-switch list -c <clientId>

# Abort immediately on first read failure
agent-lynx global-switch list -c <clientId> --fail-fast

# Get one key
agent-lynx global-switch get --key enable_devtool -c <clientId>

# Set one key on
agent-lynx global-switch set --key enable_devtool --status on -c <clientId>

# Set one key off
agent-lynx global-switch set --key enable_devtool --status off -c <clientId>
```

## Output Shape

### `global-switch list`

```json
{
  "switches": [
    { "key": "enable_devtool", "value": true },
    { "key": "enable_v8", "error": "transport timeout" }
  ]
}
```

### `global-switch get`

```json
{
  "key": "enable_devtool",
  "value": true
}
```

### `global-switch set`

```json
{
  "key": "enable_devtool",
  "value": false
}
```

## Notes

- `list` reads each key by calling connector `getGlobalSwitch` one by one.
- Without `--fail-fast`, one key failure does not stop other keys from being read.
- Some hosts do not respond to global switch requests. In that case `get` may throw `No response found`, and `list` can block while waiting for a switch response.
- Use `list-clients` first if you need to determine a concrete `clientId`.
