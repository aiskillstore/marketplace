# @neural-ui/core/bottom-sheet

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuBottomSheetComponent

Selector: `neu-bottom-sheet`

| Input | Required | Type |
| --- | --- | --- |
| open | no | `import("@angular/core").InputSignal<boolean>` |
| title | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| closeLabel | no | `import("@angular/core").InputSignal<string>` |
| backdrop | no | `import("@angular/core").InputSignal<boolean>` |
| disableClose | no | `import("@angular/core").InputSignal<boolean>` |
| size | no | `import("@angular/core").InputSignal<NeuBottomSheetSize>` |
| initialFocus | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| closeRequested | `import("@angular/core").OutputEmitterRef<NeuCloseRequest>` |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |

## NeuBottomSheetSize

```typescript
export type NeuBottomSheetSize = 'sm' | 'md' | 'lg' | 'full';
```

