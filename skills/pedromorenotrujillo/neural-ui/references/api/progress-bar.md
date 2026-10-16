# @neural-ui/core/progress-bar

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuProgressBarComponent

Selector: `neu-progress-bar`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").InputSignal<number>` |
| tone | no | `import("@angular/core").InputSignal<NeuProgressTone>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| showValue | no | `import("@angular/core").InputSignal<boolean>` |
| indeterminate | no | `import("@angular/core").InputSignal<boolean>` |
| size | no | `import("@angular/core").InputSignal<"sm" \| "md" \| "lg">` |

| Output | Type |
| --- | --- |

## NeuProgressTone

```typescript
export type NeuProgressTone = 'neutral' | 'brand' | 'success' | 'info' | 'warning' | 'danger';
```

