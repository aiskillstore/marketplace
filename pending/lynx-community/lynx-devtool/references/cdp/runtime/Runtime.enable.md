# Runtime.enable

- `Runtime.enable` - Enables reporting of execution contexts creation by means of `executionContextCreated` event.
- Input: None
- Output: `{}`
- Description: Enables the Runtime domain event dispatching (e.g., reporting console logs to DevTools frontend, execution context creation/destruction events).

## Main-thread usage

Use `--thread main` to enable Runtime events from the main-thread VM, for example when pairing `Runtime.enable` with `get-console --thread main`.
