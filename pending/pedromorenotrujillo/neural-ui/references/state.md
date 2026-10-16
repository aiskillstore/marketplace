# State ownership, tables, navigation and overlays

Determine ownership from the real contract, never from a Change suffix alone.

| Contract | Meaning | Example |
| --- | --- | --- |
| Input | Application supplies a value | Button.disabled |
| Model | Component can edit the documented value | Input.value/valueChange |
| Proposal | Application accepts or rejects a request | Dialog.closeRequested |
| Domain event | Reports an action and its payload | Button.neuClick |
| Lifecycle | Reports an applied transition | Dialog.opened/closed |
| Derived internals | No consumer state ownership implied | Internal disabled activation guard |

## Tables

Use the compiled [table.ts](../examples/table.ts) and [table API](api/table.md). Provide a stable rowKey accessor returning domain keys; do not use row indices for mutable datasets. Supply readonly data and typed columns. The application owns query and selection. queryChange supplies the next query; selectionChange supplies an event whose next property is the proposed selection. Write each into the corresponding input signal. Never mutate rows, selection arrays or query objects in place.

The canonical query includes page (zero-based), pageSize, search, sort and filters. Do not revive fragmented v1 paging/sort inputs. Read the exported query and selection types before adding a feature; all-matching selection is a separate discriminated variant, not a list of loaded rows.

Remote mode is application-owned orchestration. Inspect NeuTableDataRequest and NeuTableMetadata: requestId, queryRevision and appliedRequestId describe which data belongs to which request. Preserve this provenance, ignore stale responses and update metadata consistently with applied data. Do not label the client-only example as a tested remote implementation. This repository adds no backend or network data source.

## Navigation

The compiled [navigation.ts](../examples/navigation.ts) uses controlled Tabs: activeId comes from one signal and activeIdChange proposes a tab ID or null. Keep tabId values aligned with tab IDs. An initialActiveId seed belongs to an uncontrolled setup; do not switch ownership mid-lifecycle. Check each other navigation component's own state contract; Tabs is not automatically a router. Angular Router owns application URLs and routes.

## Overlays

The compiled [overlays.ts](../examples/overlays.ts) uses /modal's NeuDialogComponent. Application open is an input. closeRequested carries a NeuCloseRequest and does not close the dialog until the application updates open. It can be rejected. Do not invent openChange or [(open)] for Dialog. opened and closed report applied lifecycle transitions, not permission to mutate state.

Keep an accessible title, keyboard dismissal, focus containment and return focus. Update the owner signal through the handler rather than imperatively manipulating the DOM. Public services and imperative methods are documented separately in [modal](api/modal.md), [popover](api/popover.md) and [foundation](api/foundation.md). Select's open/openChange pair is a different contract; do not copy Dialog event names into it. A global dismissal guard is synchronous and uses the public foundation provider if the application needs one.

Source: [official v2 state ownership](https://ui.neuralui.org/v2/en/foundations/state-ownership).
