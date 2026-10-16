# @neural-ui/core/tree-select

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuOptionAccessor

```typescript
export type NeuOptionAccessor<T, R = unknown> = Exclude<keyof T, string> | NeuOptionPath<T> | ((option: T) => R);
```

## NeuOptionDisabledAccessor

```typescript
export type NeuOptionDisabledAccessor<T> = NeuOptionAccessor<T, boolean>;
```

## NeuOptionLabelAccessor

```typescript
export type NeuOptionLabelAccessor<T> = NeuOptionAccessor<T, string>;
```

## NeuOptionValue

```typescript
export type NeuOptionValue<T> = T extends {
    label: string;
    value: infer V;
} ? V : T;
```

## NeuOptionValueAccessor

```typescript
export type NeuOptionValueAccessor<T, V> = NeuOptionAccessor<T, V>;
```

## NeuTreeSelectChildrenRequest

```typescript
export interface NeuTreeSelectChildrenRequest<K> {
    readonly requestId: number;
    readonly queryRevision: number;
    readonly parentKey: K;
}
```

## NeuTreeSelectComponent

Selector: `neu-tree-select`

| Input | Required | Type |
| --- | --- | --- |
| nodes | no | `import("@angular/core").InputSignal<readonly T[]>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor$1<T> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<NeuOptionValueAccessor$1<T, V> \| null>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor$1<T> \| null>` |
| optionChildren | no | `import("@angular/core").InputSignal<NeuOptionAccessor$1<T, readonly T[]> \| null>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |
| searchPlaceholder | no | `import("@angular/core").InputSignal<string>` |
| searchable | no | `import("@angular/core").InputSignal<boolean>` |
| mode | no | `import("@angular/core").InputSignal<M>` |
| selectionStrategy | no | `import("@angular/core").InputSignal<NeuTreeSelectSelectionStrategy>` |
| expandedKeys | no | `import("@angular/core").InputSignal<readonly V[]>` |
| virtualizationOptions | no | `import("@angular/core").InputSignal<Readonly<NeuTreeSelectVirtualizationOptions>>` |
| clearable | no | `import("@angular/core").InputSignal<boolean>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| clearLabel | no | `import("@angular/core").InputSignal<string>` |
| value | no | `import("@angular/core").ModelSignal<NeuSelectionValue<V, M>>` |

| Output | Type |
| --- | --- |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| expandedKeysChange | `import("@angular/core").OutputEmitterRef<readonly V[]>` |
| nodeExpanded | `import("@angular/core").OutputEmitterRef<T>` |
| nodeCollapsed | `import("@angular/core").OutputEmitterRef<T>` |
| childrenRequest | `import("@angular/core").OutputEmitterRef<NeuTreeSelectChildrenRequest<V>>` |
| rangeChange | `import("@angular/core").OutputEmitterRef<NeuViewportRange>` |
| filter | `import("@angular/core").OutputEmitterRef<{
    query: string;
}>` |
| cleared | `import("@angular/core").OutputEmitterRef<void>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |
| valueChange | `import("@angular/core").ModelSignal<NeuSelectionValue<V, M>>` |

## NeuTreeSelectEmptyDirective

Selector: `ng-template[neuTreeSelectEmpty]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeSelectFooterDirective

Selector: `ng-template[neuTreeSelectFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeSelectHeaderDirective

Selector: `ng-template[neuTreeSelectHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeSelectNode

```typescript
export interface NeuTreeSelectNode {
    value: string;
    label: string;
    disabled?: boolean;
    children?: NeuTreeSelectNode[];
    lazy?: boolean;
    data?: unknown;
}
```

## NeuTreeSelectNodeDirective

Selector: `ng-template[neuTreeSelectNode]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeSelectNodeTemplateContext

```typescript
export interface NeuTreeSelectNodeTemplateContext<T = NeuTreeSelectNode> {
    $implicit: T;
    level: number;
    selected: boolean;
    toggle: () => void;
}
```

## NeuTreeSelectSelectedDirective

Selector: `ng-template[neuTreeSelectSelected]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeSelectSelectionStrategy

```typescript
export type NeuTreeSelectSelectionStrategy = 'independent' | 'propagated';
```

## NeuTreeSelectVirtualizationOptions

```typescript
export interface NeuTreeSelectVirtualizationOptions {
    readonly enabled?: boolean;
    readonly itemSize?: number;
    readonly viewportHeight?: number;
    readonly buffer?: number;
}
```

