# @neural-ui/core/chip

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuChipComponent

Selector: `neu-chip`

| Input | Required | Type |
| --- | --- | --- |
| tone | no | `import("@angular/core").InputSignal<NeuChipTone>` |
| size | no | `import("@angular/core").InputSignal<NeuChipSize>` |
| selected | no | `import("@angular/core").InputSignal<boolean>` |
| removable | no | `import("@angular/core").InputSignal<boolean>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| removeAriaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| selectedChange | `import("@angular/core").OutputEmitterRef<boolean>` |
| removed | `import("@angular/core").OutputEmitterRef<void>` |

## NeuChipSize

```typescript
export type NeuChipSize = 'sm' | 'md';
```

## NeuChipTone

```typescript
export type NeuChipTone = 'neutral' | 'brand' | 'success' | 'info' | 'warning' | 'danger';
```

