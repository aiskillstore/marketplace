# @neural-ui/core/pick-list

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuListLocation

```typescript
export type NeuListLocation = 'source' | 'target';
```

## NeuListMove

```typescript
export type NeuListMove = 'up' | 'down' | 'top' | 'bottom';
```

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

## NeuOrderListComponent

Selector: `neu-order-list`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<readonly T[]>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor$1<T> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<NeuOptionValueAccessor$1<T, V> \| null>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor$1<T> \| null>` |
| selectionKeys | no | `import("@angular/core").InputSignal<readonly V[] \| undefined>` |
| filter | no | `import("@angular/core").InputSignal<boolean>` |
| filterValue | no | `import("@angular/core").InputSignal<string \| null>` |
| filterConfig | no | `import("@angular/core").InputSignal<Readonly<NeuOptionFilterConfig<T>>>` |
| filterPlaceholder | no | `import("@angular/core").InputSignal<string>` |
| filterLabel | no | `import("@angular/core").InputSignal<string>` |
| emptyFilterLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| dragDrop | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| orderChange | `import("@angular/core").OutputEmitterRef<T[]>` |
| selectionChange | `import("@angular/core").OutputEmitterRef<T[]>` |
| filterChange | `import("@angular/core").OutputEmitterRef<string>` |
| itemDrop | `import("@angular/core").OutputEmitterRef<NeuPickListDropEvent<T>>` |

## NeuOrderListItemContext

```typescript
export interface NeuOrderListItemContext<T> {
    readonly $implicit: T;
    readonly index: number;
    readonly selected: boolean;
}
```

## NeuOrderListItemDirective

Selector: `ng-template[neuOrderListItem]`

| Input | Required | Type |
| --- | --- | --- |
| neuOrderListItem | no | `import("@angular/core").InputSignal<"" \| readonly T[]>` |

| Output | Type |
| --- | --- |

## NeuPickListComponent

Selector: `neu-pick-list`

| Input | Required | Type |
| --- | --- | --- |
| source | no | `import("@angular/core").InputSignal<readonly T[]>` |
| target | no | `import("@angular/core").InputSignal<readonly T[]>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor$1<T> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<NeuOptionValueAccessor$1<T, V> \| null>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor$1<T> \| null>` |
| sourceHeader | no | `import("@angular/core").InputSignal<string>` |
| targetHeader | no | `import("@angular/core").InputSignal<string>` |
| filter | no | `import("@angular/core").InputSignal<boolean>` |
| filterConfig | no | `import("@angular/core").InputSignal<Readonly<NeuOptionFilterConfig<T>>>` |
| sourceFilterValue | no | `import("@angular/core").InputSignal<string \| null>` |
| targetFilterValue | no | `import("@angular/core").InputSignal<string \| null>` |
| filterPlaceholder | no | `import("@angular/core").InputSignal<string>` |
| sourceFilterLabel | no | `import("@angular/core").InputSignal<string>` |
| targetFilterLabel | no | `import("@angular/core").InputSignal<string>` |
| emptyFilterLabel | no | `import("@angular/core").InputSignal<string>` |
| moveAllScope | no | `import("@angular/core").InputSignal<NeuPickListMoveAllScope>` |
| dragDrop | no | `import("@angular/core").InputSignal<boolean>` |
| sourceSelectionKeys | no | `import("@angular/core").InputSignal<readonly V[] \| undefined>` |
| targetSelectionKeys | no | `import("@angular/core").InputSignal<readonly V[] \| undefined>` |

| Output | Type |
| --- | --- |
| sourceChange | `import("@angular/core").OutputEmitterRef<T[]>` |
| targetChange | `import("@angular/core").OutputEmitterRef<T[]>` |
| sourceSelectionChange | `import("@angular/core").OutputEmitterRef<T[]>` |
| targetSelectionChange | `import("@angular/core").OutputEmitterRef<T[]>` |
| sourceFilterChange | `import("@angular/core").OutputEmitterRef<string>` |
| targetFilterChange | `import("@angular/core").OutputEmitterRef<string>` |
| itemDrop | `import("@angular/core").OutputEmitterRef<NeuPickListDropEvent<T>>` |
| itemsChange | `import("@angular/core").OutputEmitterRef<{
    source: T[];
    target: T[];
}>` |

## NeuPickListDropEvent

```typescript
export interface NeuPickListDropEvent<T> {
    readonly item: T;
    readonly from: NeuListLocation;
    readonly to: NeuListLocation;
    readonly previousIndex: number;
    readonly currentIndex: number;
    readonly interaction: "pointer" | "keyboard";
    readonly originalEvent: MouseEvent | TouchEvent | KeyboardEvent | null;
}
```

## NeuPickListItemContext

```typescript
export interface NeuPickListItemContext<T> {
    readonly $implicit: T;
    readonly selected: boolean;
    readonly location: NeuListLocation;
}
```

## NeuPickListItemDirective

Selector: `ng-template[neuPickListItem]`

| Input | Required | Type |
| --- | --- | --- |
| neuPickListItem | no | `import("@angular/core").InputSignal<"" \| readonly T[]>` |

| Output | Type |
| --- | --- |

## NeuPickListMoveAllScope

```typescript
export type NeuPickListMoveAllScope = 'filtered' | 'all';
```

## NeuTransferItem

```typescript
export interface NeuTransferItem {
    value: string;
    label: string;
    disabled?: boolean;
    data?: unknown;
}
```

