# Performance.getAllTimingInfo

Scope: This method documents LynxView-specific timing data exposed by Lynx DevTool. For WebView targets, use standard Chrome DevTools Protocol Performance APIs instead; this method may return `method not found`.

- `Performance.getAllTimingInfo` - Get all timing metrics from the current page.
- Input: None
- Output: `<timing object>`
- Description: Returns aggregated timing data reported by Lynx runtime (for example FCP and other available metrics).

## Field Meanings

### `metrics` (performance result metrics)

- `fcp`: First Contentful Paint. Elapsed time from `prepare_template_start` to the first meaningful content paint.
- `lynx_fcp`: Lynx First Contentful Paint. Elapsed time from `load_template_start` to the first meaningful content painted by Lynx engine.
- `tti`: Time to Interactive. Computed as `max(draw_end, load_app_end) - prepare_template_start`.
- `lynx_tti`: Lynx Time to Interactive. Computed as `max(draw_end, load_app_end) - load_template_start`.
- `total_fcp`: Total First Contentful Paint. Elapsed time from `open_time` to first meaningful content paint.
- `total_tti`: Total Time to Interactive. Computed as `max(draw_end, load_app_end) - open_time`.

### `setup_timing` (render stage timestamps)

- `pipeline_start`: Pipeline start timestamp.
- `load_template_start`: Template loading start timestamp.
- `load_template_end`: Template loading end timestamp.
- `load_core_start`: Lynx core loading start timestamp.
- `load_core_end`: Lynx core loading end timestamp.
- `verify_tasm_start`: TASM verification start timestamp.
- `verify_tasm_end`: TASM verification end timestamp.
- `ffi_start`: FFI bridge invocation start timestamp.
- `ffi_end`: FFI bridge invocation end timestamp.
- `decode_start`: Template decode/parsing start timestamp.
- `decode_end`: Template decode/parsing end timestamp.
- `lepus_excute_start`: Lepus execution start timestamp.
- `lepus_excute_end`: Lepus execution end timestamp.
- `data_processor_start`: Initial data processing/transformation start timestamp.
- `data_processor_end`: Initial data processing/transformation end timestamp.
- `set_init_data_start`: Initial data injection start timestamp.
- `set_init_data_end`: Initial data injection end timestamp.
- `create_lynx_start`: Lynx instance creation start timestamp.
- `create_lynx_end`: Lynx instance creation end timestamp.
- `load_app_start`: App loading/execution start timestamp.
- `load_app_end`: App loading/execution end timestamp.
- `create_vdom_start`: Virtual DOM creation start timestamp.
- `create_vdom_end`: Virtual DOM creation end timestamp.
- `dispatch_start`: Resolve/dispatch stage start timestamp (legacy polyfill name mapped from `resolveStart`).
- `dispatch_end`: Resolve/dispatch stage end timestamp (legacy polyfill name mapped from `resolveEnd`).
- `layout_start`: Layout calculation start timestamp.
- `layout_end`: Layout calculation end timestamp.
- `ui_operation_flush_start`: UI operation flush start timestamp.
- `ui_operation_flush_end`: UI operation flush end timestamp.
- `layout_ui_operation_flush_start`: Layout-triggered UI operation flush start timestamp.
- `painting_ui_operation_flush_end`: Paint-stage UI operation flush end timestamp.
- `draw_end`: Final drawing/render submission completion timestamp.

## Deriving Stage Durations

All `setup_timing` fields are timestamps. You can derive stage durations by subtraction:

- `load_template_cost = load_template_end - load_template_start`
- `load_core_cost = load_core_end - load_core_start`
- `verify_tasm_cost = verify_tasm_end - verify_tasm_start`
- `ffi_cost = ffi_end - ffi_start`
- `decode_cost = decode_end - decode_start`
- `lepus_execute_cost = lepus_excute_end - lepus_excute_start`
- `data_processor_cost = data_processor_end - data_processor_start`
- `set_init_data_cost = set_init_data_end - set_init_data_start`
- `create_lynx_cost = create_lynx_end - create_lynx_start`
- `load_app_cost = load_app_end - load_app_start`
- `create_vdom_cost = create_vdom_end - create_vdom_start`
- `dispatch_cost = dispatch_end - dispatch_start`
- `layout_cost = layout_end - layout_start`
- `ui_operation_flush_cost = ui_operation_flush_end - ui_operation_flush_start`

You can also derive end-to-end windows:

- `pipeline_total_cost = draw_end - pipeline_start`
- `open_to_draw_cost = draw_end - extra_timing.open_time`
- `open_to_fcp_cost = metrics.total_fcp`
- `open_to_tti_cost = metrics.total_tti`

Notes:

- Keep all arithmetic in the same time unit as source fields.
- Some fields may be missing depending on runtime/platform/version. Guard with existence checks before subtraction.
- `dispatch_*` are legacy-exposed keys mapped to resolve-stage timestamps in engine constants.
- `ui_operation_flush_*` are also legacy polyfill keys. For finer split, prefer `layout_ui_operation_flush_start` and `painting_ui_operation_flush_end` when present.
- `has_reload` is produced as a boolean in engine output (some transports may display it as `0/1`).
- `lepus_excute_*` uses the historical field spelling `excute` in engine constants.

## Practical Stage Analysis

- `load_template_end - load_template_start`: template loading cost. High values often point to large bundles, remote fetch latency, or local I/O bottlenecks.
- `load_core_end - load_core_start`: runtime core init cost. High values can indicate expensive engine/bootstrap initialization on device.
- `load_app_end - load_app_start`: app-side background runtime load cost. This stage affects TTI because `tti`/`total_tti` use `max(draw_end, load_app_end)`.
- `decode_end - decode_start`: template parsing/decoding cost. High values often correlate with heavy/complex template payloads.
- `lepus_excute_end - lepus_excute_start`: Lepus execution cost. High values usually indicate heavy startup script logic or data processing.
- `data_processor_end - data_processor_start`: initial data transform cost. High values often indicate large initial payloads or expensive processors.
- `create_vdom_end - create_vdom_start`: virtual DOM creation cost. High values often map to deep/wide initial component trees.
- `dispatch_end - dispatch_start`: resolve/dispatch stage cost. Treat as pipeline stage overhead rather than a strict cross-thread transport metric.
- `layout_end - layout_start`: layout calculation cost. High values often indicate complex layout trees or expensive constraints.
- `ui_operation_flush_end - ui_operation_flush_start`: legacy flush window. Use together with layout/painting flush keys for more precise attribution.
