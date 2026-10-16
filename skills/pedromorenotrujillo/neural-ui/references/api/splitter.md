# @neural-ui/core/splitter

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuSplitterComponent

Selector: `neu-splitter`

| Input | Required | Type |
| --- | --- | --- |
| orientation | no | `import("@angular/core").InputSignal<NeuSplitterDirection>` |
| panes | no | `import("@angular/core").InputSignal<readonly NeuSplitterPane[]>` |

| Output | Type |
| --- | --- |
| sizesChange | `import("@angular/core").OutputEmitterRef<readonly number[]>` |
| resizeStart | `import("@angular/core").OutputEmitterRef<readonly number[]>` |
| resize | `import("@angular/core").OutputEmitterRef<readonly number[]>` |

## NeuSplitterDirection

```typescript
export type NeuSplitterDirection = 'horizontal' | 'vertical';
```

## NeuSplitterPane

```typescript
export interface NeuSplitterPane {
    size?: number;
    min?: number;
    max?: number;
}
```

