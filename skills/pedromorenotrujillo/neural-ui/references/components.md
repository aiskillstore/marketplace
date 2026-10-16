# Components and public imports

Read the [API index](api/index.md), then only the relevant entrypoint. Those files are generated from published 2.0.1 declarations, with support exclusions from the reviewed upstream policy. They include exact selectors, required inputs, output types and exported domain types.

| Task | Start with |
| --- | --- |
| Actions | [button](api/button.md), [split-button](api/split-button.md) |
| Input and validation | [input](api/input.md), [select](api/select.md), [form-field](api/form-field.md) |
| Data | [table](api/table.md), [tree-table](api/tree-table.md), [data-view](api/data-view.md) |
| Navigation | [tabs](api/tabs.md), [nav](api/nav.md), [breadcrumb](api/breadcrumb.md), [menu](api/menu.md) |
| Overlays and feedback | [modal](api/modal.md), [popover](api/popover.md), [toast](api/toast.md) |
| Layout | [card](api/card.md), [panel](api/panel.md), [splitter](api/splitter.md), [dashboard-grid](api/dashboard-grid.md) |

Naming traps verified in the package:

- NeuButtonComponent selects a native button with the neu-button attribute. Its domain output is neuClick.
- The /modal entrypoint exports NeuDialogComponent with selector neu-dialog. Never infer the exported name or selector from the entrypoint filename.
- The Angular FormField directive belongs to @angular/forms/signals. Neural's NeuFormFieldComponent is a layout shell and label/hint/error association API.
- Select mode determines whether value is scalar/null or an immutable array. Give mode an explicit literal when Angular must infer a narrow event type.
- A table's selectionChange event carries next plus source and key deltas. Its queryChange event carries the query itself. Read each payload independently.

The root entrypoint intentionally does not re-export the whole component catalog. Entry points marked internal by the source policy are excluded even if package.json physically lists them. Generated declarations can reference private dependency types; that is not authorization to import those types from implementation files. Use only an exported type from an admitted public entrypoint.

The API catalog is a structural inventory. Runtime behavior, accessibility and state ownership still need the relevant reference and an integration check. It is not a certification of every component.

Source: [official v2 catalog](https://ui.neuralui.org/v2/en/components).
