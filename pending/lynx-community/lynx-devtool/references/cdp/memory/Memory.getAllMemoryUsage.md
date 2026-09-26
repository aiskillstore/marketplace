# Memory.getAllMemoryUsage

Scope: This is a Lynx global CDP extension. Send it to the global DevTool handler with session ID `-1` unless you have a platform-specific reason to override the session.

- `Memory.getAllMemoryUsage` - Get global Lynx memory usage across live registered Lynx instances.
- Input:
  - `timeoutMs` (integer, optional): Non-negative timeout in milliseconds. `0` or omission lets the platform choose its default wait policy. Maximum accepted value is `300000`; fractional values are rejected.
- Output:
  - `collectionStartMs` (number): Wall-clock collection start time in milliseconds.
  - `collectionStatus` (`"completed"` | `"timeout"`): Whether all expected instance fetchers completed.
  - `collectionDurationMs` (number): Elapsed collection time in milliseconds.
  - `collectionTimeoutMs` (number): Timeout used by the platform query.
  - `expectedInstanceCount` (number): Number of live instance fetchers at request start.
  - `completedInstanceCount` (number): Number of completed instance results.
  - `totalBytes` (number): Global Lynx-attributed bytes, excluding `appBytes` and deduplicating shared background runtime groups.
  - `appBytes` (number): Current app memory footprint sampled by the platform.
  - `ratioToApp` (number): `totalBytes / appBytes`, or `0` when app bytes are unavailable.
  - `elementBytes` (number): Aggregated element tree memory.
  - `elementNodeCount` (number): Aggregated element node count.
  - `viewBytes` (number): Aggregated UI/view memory.
  - `mainThreadRuntimeBytes` (number): Aggregated main-thread runtime bytes.
  - `backgroundThreadRuntimeBytes` (number): Aggregated background runtime bytes with shared groups deduplicated.
  - `instances` (array): Completed instance list, sorted by `totalBytes` descending.
- Description: Queries a global snapshot of Lynx-attributed memory across live registered Lynx instances. This differs from `Runtime.getHeapUsage`, which only reports JavaScript heap usage for one session/thread.

`instances[]` corresponds to registered Lynx instance fetchers, such as live `LynxTemplateRender`/LynxShell instances. It is not a nested child LynxView tree. If a page contains child LynxViews that are not exposed as separate registered instances by the platform collector, their memory is included in the owning instance aggregates rather than reported as separate `instances[]` entries.

Each `instances[]` item contains:

- `instanceId` (number): LynxShell instance id. `-1` means the instance was not fully attached.
- `pageId` (string): Page identity when available.
- `url` (string): Current template URL.
- `totalBytes` (number): Instance-attributed total bytes.
- `elementBytes` (number): Element tree memory.
- `elementNodeCount` (number): Element node count.
- `viewBytes` (number): UI/view bytes.
- `viewDetail` (object): UI view memory records keyed by view category/tag or view key. This is a category aggregation, not a per-child-LynxView breakdown.
- `mainThreadRuntimeBytes` (number): Main-thread runtime bytes.
- `backgroundThreadRuntimeBytes` (number): Background-thread runtime bytes.
- `btsRuntimeGroupId` (string): Background runtime group id used for global deduplication.

## Usage

```bash
agent-lynx cdp -s -1 -m Memory.getAllMemoryUsage
agent-lynx cdp -s -1 -m Memory.getAllMemoryUsage '{"timeoutMs":50000}'
```

The CLI prints the raw `Memory.getAllMemoryUsage` response. Agents using the Lynx DevTool skill should apply the reporting rules in `SKILL.md` when a user asks for a human-readable summary or Top 5 breakdown.

The DevTool MCP server also exposes this method as `Memory_getAllMemoryUsage`.
