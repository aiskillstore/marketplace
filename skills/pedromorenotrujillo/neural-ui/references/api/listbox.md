# @neural-ui/core/listbox

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuListboxChangeEvent

```typescript
export interface NeuListboxChangeEvent<T, V> {
    readonly originalEvent: Event | null;
    readonly option: T | null;
    readonly value: V | readonly V[] | null;
    readonly selectedOptions: readonly T[];
    readonly selected: boolean;
}
```

## NeuListboxComponent

Selector: `neu-listbox`

| Input | Required | Type |
| --- | --- | --- |
| id | no | `import("@angular/core").InputSignal<string \| null>` |
| options | no | `import("@angular/core").InputSignal<readonly T[]>` |
| groups | no | `import("@angular/core").InputSignal<readonly G[]>` |
| groupConfig | no | `import("@angular/core").InputSignal<NeuOptionGroupConfig$1<T, G> \| null>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaFilterLabel | no | `import("@angular/core").InputSignal<string>` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |
| noResultsMessage | no | `import("@angular/core").InputSignal<string>` |
| mode | no | `import("@angular/core").InputSignal<M>` |
| searchable | no | `import("@angular/core").InputSignal<boolean>` |
| searchPlaceholder | no | `import("@angular/core").InputSignal<string>` |
| filterValue | no | `import("@angular/core").InputSignal<string \| null>` |
| filterConfig | no | `import("@angular/core").InputSignal<Readonly<NeuOptionFilterConfig$1<T>>>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| tabindex | no | `import("@angular/core").InputSignal<number>` |
| autoOptionFocus | no | `import("@angular/core").InputSignal<boolean>` |
| selectOnFocus | no | `import("@angular/core").InputSignal<boolean>` |
| focusOnHover | no | `import("@angular/core").InputSignal<boolean>` |
| metaKeySelection | no | `import("@angular/core").InputSignal<boolean>` |
| checkbox | no | `import("@angular/core").InputSignal<boolean>` |
| checkmark | no | `import("@angular/core").InputSignal<boolean>` |
| highlightOnSelect | no | `import("@angular/core").InputSignal<boolean>` |
| showToggleAll | no | `import("@angular/core").InputSignal<boolean>` |
| toggleAllLabel | no | `import("@angular/core").InputSignal<string>` |
| striped | no | `import("@angular/core").InputSignal<boolean>` |
| fluid | no | `import("@angular/core").InputSignal<boolean>` |
| scrollHeight | no | `import("@angular/core").InputSignal<string>` |
| listStyle | no | `import("@angular/core").InputSignal<Record<string, string \| number> \| null>` |
| listStyleClass | no | `import("@angular/core").InputSignal<string \| null>` |
| virtualScroll | no | `import("@angular/core").InputSignal<boolean>` |
| virtualScrollItemSize | no | `import("@angular/core").InputSignal<number>` |
| virtualScrollViewportItems | no | `import("@angular/core").InputSignal<number>` |
| virtualScrollBuffer | no | `import("@angular/core").InputSignal<number>` |
| lazy | no | `import("@angular/core").InputSignal<boolean>` |
| loading | no | `import("@angular/core").InputSignal<boolean>` |
| totalItems | no | `import("@angular/core").InputSignal<number \| null>` |
| dataFirst | no | `import("@angular/core").InputSignal<number>` |
| dragdrop | no | `import("@angular/core").InputSignal<boolean>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor$1<T> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<(option: T) => V>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor$1<T> \| null>` |
| compareWith | no | `import("@angular/core").InputSignal<(left: V, right: V) => boolean>` |
| value | no | `import("@angular/core").ModelSignal<NeuSelectionValue<V, M>>` |

| Output | Type |
| --- | --- |
| optionActivated | `import("@angular/core").OutputEmitterRef<NeuOptionActivatedEvent<T, V>>` |
| filterChange | `import("@angular/core").OutputEmitterRef<string>` |
| dataRequest | `import("@angular/core").OutputEmitterRef<NeuOptionDataRequest>` |
| rangeChange | `import("@angular/core").OutputEmitterRef<NeuViewportRange>` |
| focusEntered | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| focusLeft | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |
| drop | `import("@angular/core").OutputEmitterRef<NeuListboxDropEvent<T>>` |
| valueChange | `import("@angular/core").ModelSignal<NeuSelectionValue<V, M>>` |

Supported imperative members:

```typescript
setFilter(value: string, originalEvent?: Event | null): void;
resetFilter(): void;
toggleAll(event: Event): void;
```

## NeuListboxDropEvent

```typescript
export interface NeuListboxDropEvent<T> {
    readonly originalEvent: Event;
    readonly option: T;
    readonly previousIndex: number;
    readonly currentIndex: number;
    readonly options: readonly T[];
}
```

## NeuListboxEmptyDirective

Selector: `ng-template[neuListboxEmpty]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuListboxEmptyFilterDirective

Selector: `ng-template[neuListboxEmptyFilter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuListboxFilterDirective

Selector: `ng-template[neuListboxFilter]`

| Input | Required | Type |
| --- | --- | --- |
| neuListboxFilter | no | `import("@angular/core").InputSignal<"" \| Readonly<NeuOptionFilterConfig$1<T>>>` |

| Output | Type |
| --- | --- |

## NeuListboxFilterEvent

```typescript
export interface NeuListboxFilterEvent<T> {
    readonly originalEvent: Event | null;
    readonly filter: string;
    readonly visibleOptions: readonly T[];
    readonly config: Readonly<NeuOptionFilterConfig$1<T>>;
}
```

## NeuListboxFooterDirective

Selector: `ng-template[neuListboxFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuListboxGroupDirective

Selector: `ng-template[neuListboxGroup]`

| Input | Required | Type |
| --- | --- | --- |
| neuListboxGroup | no | `import("@angular/core").InputSignal<"" \| readonly G[]>` |

| Output | Type |
| --- | --- |

## NeuListboxHeaderDirective

Selector: `ng-template[neuListboxHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuListboxIndicatorContext

```typescript
export interface NeuListboxIndicatorContext<T, V> {
    readonly $implicit: boolean;
    readonly selected: boolean;
    readonly option: T;
    readonly value: V;
    readonly checkbox: boolean;
    readonly checkmark: boolean;
}
```

## NeuListboxIndicatorDirective

Selector: `ng-template[neuListboxIndicator]`

| Input | Required | Type |
| --- | --- | --- |
| neuListboxIndicator | no | `import("@angular/core").InputSignal<"" \| readonly T[]>` |

| Output | Type |
| --- | --- |

## NeuListboxItemContext

```typescript
export type NeuListboxItemContext<T> = NeuOptionTemplateContext$1<T>;
```

## NeuListboxItemDirective

Selector: `ng-template[neuListboxItem]`

| Input | Required | Type |
| --- | --- | --- |
| neuListboxItem | no | `import("@angular/core").InputSignal<"" \| readonly T[]>` |

| Output | Type |
| --- | --- |

## NeuListboxLoaderDirective

Selector: `ng-template[neuListboxLoader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuListboxOption

```typescript
export interface NeuListboxOption {
    value: string;
    label: string;
    disabled?: boolean;
    data?: unknown;
    group?: string;
}
```

## NeuListboxOptionEvent

```typescript
export interface NeuListboxOptionEvent<T, V> {
    readonly originalEvent: Event;
    readonly option: T;
    readonly value: V | readonly V[] | null;
}
```

## NeuListboxSelectAllEvent

```typescript
export interface NeuListboxSelectAllEvent<T, V> {
    readonly originalEvent: Event;
    readonly checked: boolean;
    readonly scope: "visible-eligible";
    readonly options: readonly T[];
    readonly value: readonly V[];
}
```

## NeuOptionAccessor

```typescript
export type NeuOptionAccessor<T, R = unknown> = Exclude<keyof T, string> | NeuOptionPath<T> | ((option: T) => R);
```

## NeuOptionDisabledAccessor

```typescript
export type NeuOptionDisabledAccessor<T> = NeuOptionAccessor<T, boolean>;
```

## NeuOptionFilterConfig

```typescript
export interface NeuOptionFilterConfig<T> {
    readonly fields?: readonly NeuOptionAccessor<T, unknown>[];
    readonly matchMode?: NeuOptionFilterMatchMode;
    readonly locale?: string;
    readonly strategy?: NeuOptionFilterStrategy;
}
```

## NeuOptionFilterMatchMode

```typescript
export type NeuOptionFilterMatchMode = 'startsWith' | 'contains' | 'notContains' | 'endsWith' | 'equals' | 'notEquals';
```

## NeuOptionFilterTemplateContext

```typescript
export interface NeuOptionFilterTemplateContext<T> {
    readonly $implicit: string;
    readonly value: string;
    readonly config: Readonly<NeuOptionFilterConfig<T>>;
    readonly filter: (value: string) => void;
    readonly reset: () => void;
}
```

## NeuOptionGroupConfig

```typescript
export interface NeuOptionGroupConfig<T, G> {
    readonly labelAccessor: NeuOptionAccessor<G, unknown>;
    readonly childrenAccessor: NeuOptionAccessor<G, readonly T[]>;
    readonly disabledAccessor?: NeuOptionAccessor<G, boolean> | null;
}
```

## NeuOptionGroupTemplateContext

```typescript
export interface NeuOptionGroupTemplateContext<G> {
    readonly $implicit: G;
    readonly group: G;
    readonly index: number;
    readonly label: string;
    readonly disabled: boolean;
}
```

## NeuOptionIdentityConfig

```typescript
export interface NeuOptionIdentityConfig<T, V = NeuOptionValue<T>, I = unknown> {
    readonly identityAccessor?: NeuOptionAccessor<T, I> | null;
    readonly compareWith?: NeuOptionCompareWith<V> | null;
    readonly valueAccessor?: NeuOptionAccessor<T, V> | null;
}
```

## NeuOptionLabelAccessor

```typescript
export type NeuOptionLabelAccessor<T> = NeuOptionAccessor<T, string>;
```

## NeuOptionLazyRequest

```typescript
export interface NeuOptionLazyRequest {
    readonly first: number;
    readonly end: number;
    readonly count: number;
    readonly filterValue: string;
    readonly filterFields?: readonly string[];
    readonly filterFieldsSerializable: boolean;
    readonly filterMatchMode: NeuOptionFilterMatchMode;
    readonly filterLocale?: string;
    readonly reason: NeuOptionLazyRequestReason;
    readonly requestId: number;
}
```

## NeuOptionLoaderTemplateContext

```typescript
export interface NeuOptionLoaderTemplateContext {
    readonly $implicit: number;
    readonly logicalIndex: number;
    readonly first: number;
    readonly end: number;
    readonly count: number;
}
```

## NeuOptionTemplateContext

```typescript
export interface NeuOptionTemplateContext<T> {
    readonly $implicit: T;
    readonly option: T;
    readonly index: number;
    readonly logicalIndex: number;
    readonly selected: boolean;
    readonly disabled: boolean;
    readonly active: boolean;
}
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

