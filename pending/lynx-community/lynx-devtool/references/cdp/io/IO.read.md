# IO.read

- `IO.read` - Reads a chunk from a Lynx `FileStream` handle.
- Input:
  - `handle` (string, required): Non-empty numeric stream handle, such as the `stream` value from `Tracing.tracingComplete`.
  - `size` (integer, required in practice): Positive number of bytes to read.
  - `offset` (integer, optional in CDP): Ignored by the current Lynx implementation.
- Output:
  - `base64Encoded` (boolean): Always `true`.
  - `data` (string, optional): Base64-encoded bytes read from the stream. It is absent when no bytes are read.
  - `eof` (boolean): `true` when fewer than `size` bytes are available or no bytes are read.

## Notes

- Although upstream CDP makes `size` optional, the Lynx handler treats omission or a non-positive value as an immediate EOF response. Always supply a positive integer.
- Reads continue from the stream's current position; `offset` does not seek.
- A handle whose first character is not a digit returns the CDP error `Get invalid stream handle`.
- Use `IO.close` after reading the stream. `Tracing.getStartupTracingFile` emits a `Tracing.tracingComplete` event that supplies a compatible stream handle.
