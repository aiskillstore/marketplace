# @neural-ui/core/virtual-list

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuVirtualItemContext

```typescript
interface NeuVirtualItemContext<T, K extends NeuVirtualListKey> {
    readonly $implicit: T;
    readonly item: T;
    readonly index: number;
    readonly key: K;
}
```

## NeuVirtualItemDirective

Selector: `ng-template[neuVirtualItem]`

| Input | Required | Type |
| --- | --- | --- |
| neuVirtualItem | no | `import("@angular/core").InputSignal<readonly T[] \| undefined>` |
| neuVirtualItemKey | no | `import("@angular/core").InputSignal<((item: T) => K) \| undefined>` |

| Output | Type |
| --- | --- |

## NeuVirtualListComponent

Selector: `neu-virtual-list`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<readonly T[]>` |
| itemSize | no | `import("@angular/core").InputSignal<number>` |
| visibleRows | no | `import("@angular/core").InputSignal<number>` |
| itemKey | yes | `import("@angular/core").InputSignal<(item: T) => K>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| rangeChange | `import("@angular/core").OutputEmitterRef<NeuVirtualListRange>` |

## NeuVirtualListKey

```typescript
type NeuVirtualListKey = string | number;
```

## NeuVirtualListRange

```typescript
interface NeuVirtualListRange {
    readonly start: number;
    readonly end: number;
}
```

## NeuVirtualListScrollTarget

```typescript
type NeuVirtualListScrollTarget<K extends NeuVirtualListKey> = {
    readonly index: number;
    readonly align?: 'nearest' | 'start' | 'center' | 'end';
} | {
    readonly key: K;
    readonly align?: 'nearest' | 'start' | 'center' | 'end';
};
```

