# HeapProfiler.takeHeapSnapshot

- `HeapProfiler.takeHeapSnapshot` - Captures a JavaScript heap snapshot and streams it in `HeapProfiler.addHeapSnapshotChunk` events.
- Input:
  - `reportProgress` (boolean, optional): Emit `HeapProfiler.reportHeapSnapshotProgress` while the snapshot is captured.
  - `treatGlobalObjectsAsRoots` (boolean, optional, deprecated): Request a raw snapshot without artificial roots. Prefer `exposeInternals` when supported.
  - `captureNumericValue` (boolean, optional): Include numeric values in the snapshot.
  - `exposeInternals` (boolean, optional, experimental): Expose snapshot internals.
- Output: An empty CDP result object. Snapshot data is delivered separately in `HeapProfiler.addHeapSnapshotChunk` events, whose `params.chunk` values must be concatenated in arrival order.

## Notes

- For direct CDP use, mirror the bundled `take-heap-snapshot` CLI and `HeapProfiler_takeHeapSnapshot` MCP tool by first sending `HeapProfiler.enable`.
- Heap snapshots can be large. Persist chunks as they arrive instead of buffering the full result in memory.
- `reportProgress: true` requests `HeapProfiler.reportHeapSnapshotProgress` events; these progress events do not contain snapshot data.
- The selected VM thread determines which heap is captured. The CLI defaults to the background thread; pass `--thread main` for the main-thread VM.
