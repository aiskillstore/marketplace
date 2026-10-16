# @neural-ui/core/spinner

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuSpinnerComponent

Selector: `neu-spinner`

| Input | Required | Type |
| --- | --- | --- |
| tone | no | `import("@angular/core").InputSignal<NeuSpinnerTone>` |
| color | no | `import("@angular/core").InputSignal<string>` |
| strokeWidth | no | `import("@angular/core").InputSignal<string>` |
| size | no | `import("@angular/core").InputSignal<string>` |
| animationDuration | no | `import("@angular/core").InputSignal<string>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuSpinnerTone

```typescript
export type NeuSpinnerTone = 'neutral' | 'brand' | 'success' | 'info' | 'warning' | 'danger';
```

