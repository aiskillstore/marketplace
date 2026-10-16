# @neural-ui/core/empty-state

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuEmptyStateComponent

Selector: `neu-empty-state`

| Input | Required | Type |
| --- | --- | --- |
| icon | no | `import("@angular/core").InputSignal<string \| null>` |
| iconSize | no | `import("@angular/core").InputSignal<string>` |
| title | no | `import("@angular/core").InputSignal<string>` |
| description | no | `import("@angular/core").InputSignal<string>` |
| actionLabel | no | `import("@angular/core").InputSignal<string>` |
| size | no | `import("@angular/core").InputSignal<NeuEmptyStateSize>` |
| tone | no | `import("@angular/core").InputSignal<NeuEmptyStateTone>` |
| density | no | `import("@angular/core").InputSignal<NeuDensity>` |

| Output | Type |
| --- | --- |
| action | `import("@angular/core").OutputEmitterRef<void>` |

## NeuEmptyStateSize

```typescript
export type NeuEmptyStateSize = 'sm' | 'md' | 'lg';
```

## NeuEmptyStateTone

```typescript
export type NeuEmptyStateTone = 'neutral' | 'info' | 'warning' | 'danger' | 'success';
```

