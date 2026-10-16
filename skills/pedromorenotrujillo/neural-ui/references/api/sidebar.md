# @neural-ui/core/sidebar

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuSidebarComponent

Selector: `neu-sidebar`

| Input | Required | Type |
| --- | --- | --- |
| side | no | `import("@angular/core").InputSignal<"left" \| "right">` |
| open | no | `import("@angular/core").InputSignal<boolean>` |
| persistent | no | `import("@angular/core").InputSignal<boolean>` |
| hideHeader | no | `import("@angular/core").InputSignal<boolean>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| closeLabel | no | `import("@angular/core").InputSignal<string>` |
| closeOnEscape | no | `import("@angular/core").InputSignal<boolean>` |
| restoreFocus | no | `import("@angular/core").InputSignal<boolean>` |
| collapsed | no | `import("@angular/core").InputSignal<boolean \| undefined>` |
| initialCollapsed | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| closeRequested | `import("@angular/core").OutputEmitterRef<NeuCloseRequest>` |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| collapsedChange | `import("@angular/core").OutputEmitterRef<boolean>` |

