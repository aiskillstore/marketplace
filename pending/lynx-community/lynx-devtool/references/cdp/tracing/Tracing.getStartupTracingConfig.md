# Tracing.getStartupTracingConfig

- `Tracing.getStartupTracingConfig` - Returns the stored startup tracing configuration string.
- Input: None.
- Output: `{config: string}`. `config` is the opaque string stored by the trace controller.

## Notes

- Lynx does not parse or validate the configuration in this CDP method.
- If the trace controller is unavailable, Lynx returns the CDP error `Failed to get trace controller`.
- The command runs on the global DevTool task runner. If that task runner is unavailable, the current handler does not send an explicit CDP response.
