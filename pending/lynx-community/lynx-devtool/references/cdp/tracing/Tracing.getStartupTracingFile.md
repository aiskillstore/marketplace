# Tracing.getStartupTracingFile

- `Tracing.getStartupTracingFile` - Emits a `Tracing.tracingComplete` event for the stored startup tracing file.
- Input: None.
- Output: An empty successful CDP result, followed by a `Tracing.tracingComplete` event when the trace file is available.

## Event payload

- `stream` (string): A `FileStream` handle. Read it with `IO.read` and close it with `IO.close`.
- `dataLossOccurred` (boolean): `true` when the trace file could not be opened as a stream.
- `isStartupTracing` (boolean): Always `true` for this method.

## Notes

- When startup tracing is still running, Lynx returns `Startup Tracing is running` instead of emitting the event.
- When no completed trace file exists, Lynx returns `Failed to get startup tracing file`.
- When the trace controller is unavailable, Lynx returns `Failed to get trace controller`.
- The command runs on the global DevTool task runner. If that task runner is unavailable, the current handler does not send an explicit CDP response.
