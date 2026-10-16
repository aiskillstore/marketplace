# @neural-ui/core/select

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

## NeuSelectClearedEvent

```typescript
export interface NeuSelectClearedEvent {
    readonly source: "pointer" | "keyboard" | "programmatic-command";
    readonly originalEvent?: Event;
}
```

## NeuSelectClearIconDirective

Selector: `ng-template[neuSelectClearIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectComponent

Selector: `neu-select`

| Input | Required | Type |
| --- | --- | --- |
| options | no | `import("@angular/core").InputSignal<readonly T[]>` |
| groups | no | `import("@angular/core").InputSignal<readonly G[]>` |
| groupConfig | no | `import("@angular/core").InputSignal<NeuOptionGroupConfig<T, G> \| null>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor$1<T> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<(option: T) => V>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor$1<T> \| null>` |
| compareWith | no | `import("@angular/core").InputSignal<(left: V, right: V) => boolean>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| errorMessage | no | `import("@angular/core").InputSignal<string>` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| id | no | `import("@angular/core").InputSignal<string \| null>` |
| inputId | no | `import("@angular/core").InputSignal<string \| null>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| autocomplete | no | `import("@angular/core").InputSignal<string \| null>` |
| autofocus | no | `import("@angular/core").InputSignal<boolean>` |
| tabindex | no | `import("@angular/core").InputSignal<number>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaFilterLabel | no | `import("@angular/core").InputSignal<string>` |
| fluid | no | `import("@angular/core").InputSignal<boolean>` |
| variant | no | `import("@angular/core").InputSignal<NeuSelectVariant>` |
| floatingLabel | no | `import("@angular/core").InputSignal<boolean>` |
| size | no | `import("@angular/core").InputSignal<NeuSelectSize>` |
| searchable | no | `import("@angular/core").InputSignal<boolean>` |
| filterValue | no | `import("@angular/core").InputSignal<string \| null>` |
| filterConfig | no | `import("@angular/core").InputSignal<Readonly<NeuOptionFilterConfig<T>>>` |
| resetFilterOnHide | no | `import("@angular/core").InputSignal<boolean>` |
| autofocusFilter | no | `import("@angular/core").InputSignal<boolean>` |
| searchPlaceholder | no | `import("@angular/core").InputSignal<string>` |
| loading | no | `import("@angular/core").InputSignal<boolean>` |
| loadingLabel | no | `import("@angular/core").InputSignal<string>` |
| clearable | no | `import("@angular/core").InputSignal<boolean>` |
| checkmark | no | `import("@angular/core").InputSignal<boolean>` |
| mode | no | `import("@angular/core").InputSignal<M>` |
| selectionOptions | no | `import("@angular/core").InputSignal<Readonly<NeuSelectSelectionOptions>>` |
| filterOptions | no | `import("@angular/core").InputSignal<Readonly<NeuSelectFilterOptions>>` |
| open | no | `import("@angular/core").InputSignal<boolean \| undefined>` |
| virtualScroll | no | `import("@angular/core").InputSignal<boolean>` |
| virtualScrollVisibleItems | no | `import("@angular/core").InputSignal<number>` |
| virtualScrollItemSize | no | `import("@angular/core").InputSignal<number \| null>` |
| virtualScrollBuffer | no | `import("@angular/core").InputSignal<number>` |
| lazy | no | `import("@angular/core").InputSignal<boolean>` |
| dataFirst | no | `import("@angular/core").InputSignal<number>` |
| totalItems | no | `import("@angular/core").InputSignal<number \| null>` |
| scrollHeight | no | `import("@angular/core").InputSignal<string>` |
| focusOnHover | no | `import("@angular/core").InputSignal<boolean>` |
| selectOnFocus | no | `import("@angular/core").InputSignal<boolean>` |
| autoOptionFocus | no | `import("@angular/core").InputSignal<boolean>` |
| noResultsMessage | no | `import("@angular/core").InputSignal<string>` |
| emptyMessage | no | `import("@angular/core").InputSignal<string>` |
| clearAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| selectAllLabel | no | `import("@angular/core").InputSignal<string>` |
| clearAllLabel | no | `import("@angular/core").InputSignal<string>` |
| value | no | `import("@angular/core").ModelSignal<NeuSelectionValue<V, M>>` |

| Output | Type |
| --- | --- |
| openChange | `import("@angular/core").OutputEmitterRef<boolean>` |
| filterChange | `import("@angular/core").OutputEmitterRef<string>` |
| dataRequest | `import("@angular/core").OutputEmitterRef<NeuOptionDataRequest>` |
| optionActivated | `import("@angular/core").OutputEmitterRef<NeuOptionActivatedEvent<T, V>>` |
| focusEntered | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| focusLeft | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| cleared | `import("@angular/core").OutputEmitterRef<NeuSelectClearedEvent>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |
| valueChange | `import("@angular/core").ModelSignal<NeuSelectionValue<V, M>>` |

Supported imperative members:

```typescript
focus(): void;
resetFilter(emit?: boolean): void;
clear(event?: Event): void;
selectOption(option: T): void;
```

## NeuSelectDataRequest

```typescript
export type NeuSelectDataRequest = NeuOptionDataRequest;
```

## NeuSelectDropdownIconDirective

Selector: `ng-template[neuSelectDropdownIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectEmptyDirective

Selector: `ng-template[neuSelectEmpty]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectEmptyFilterDirective

Selector: `ng-template[neuSelectEmptyFilter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectFilterContext

```typescript
export type NeuSelectFilterContext<T> = NeuOptionFilterTemplateContext<T>;
```

## NeuSelectFilterDirective

Selector: `ng-template[neuSelectFilter]`

| Input | Required | Type |
| --- | --- | --- |
| neuSelectFilter | no | `import("@angular/core").InputSignal<"" \| Readonly<NeuOptionFilterConfig<T>>>` |

| Output | Type |
| --- | --- |

## NeuSelectFilterIconDirective

Selector: `ng-template[neuSelectFilterIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectFilterOptions

```typescript
export interface NeuSelectFilterOptions {
    readonly enabled?: boolean;
    readonly debounceMs?: number;
    readonly locale?: string;
    readonly resetOnClose?: boolean;
}
```

## NeuSelectFooterDirective

Selector: `ng-template[neuSelectFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectGroup

```typescript
export interface NeuSelectGroup<T = NeuSelectOption> {
    label: string;
    options: T[];
    disabled?: boolean;
}
```

## NeuSelectGroupContext

```typescript
export type NeuSelectGroupContext<G> = NeuOptionGroupTemplateContext<G>;
```

## NeuSelectGroupDirective

Selector: `ng-template[neuSelectGroup]`

| Input | Required | Type |
| --- | --- | --- |
| neuSelectGroup | no | `import("@angular/core").InputSignal<"" \| readonly G[]>` |

| Output | Type |
| --- | --- |

## NeuSelectHeaderDirective

Selector: `ng-template[neuSelectHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectIconContext

```typescript
export interface NeuSelectIconContext {
    readonly $implicit: boolean;
    readonly active: boolean;
}
```

## NeuSelectItemContext

```typescript
export interface NeuSelectItemContext<T> extends NeuOptionTemplateContext<T> {
}
```

## NeuSelectItemDirective

Selector: `ng-template[neuSelectItem]`

| Input | Required | Type |
| --- | --- | --- |
| neuSelectItem | no | `import("@angular/core").InputSignal<"" \| readonly T[]>` |

| Output | Type |
| --- | --- |

## NeuSelectLoaderContext

```typescript
export type NeuSelectLoaderContext = NeuOptionLoaderTemplateContext;
```

## NeuSelectLoaderDirective

Selector: `ng-template[neuSelectLoader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectLoadingIconDirective

Selector: `ng-template[neuSelectLoadingIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSelectMode

```typescript
export type NeuSelectMode = NeuSelectionMode;
```

## NeuSelectModelValue

```typescript
export type NeuSelectModelValue<V, M extends NeuSelectMode = 'single'> = NeuSelectionValue<V, M>;
```

## NeuSelectOption

```typescript
export interface NeuSelectOption<V = string, D = unknown> {
    value: V;
    label: string;
    disabled?: boolean;
    group?: string;
    data?: D;
}
```

## NeuSelectOptionActivated

```typescript
export type NeuSelectOptionActivated<T, V> = NeuOptionActivatedEvent<T, V>;
```

## NeuSelectSelectedContext

```typescript
export interface NeuSelectSelectedContext<T, V = unknown> {
    readonly $implicit: T | null;
    readonly option: T | null;
    readonly value: V | null;
    readonly options: readonly T[];
    readonly values: readonly V[];
    readonly multiple: boolean;
}
```

## NeuSelectSelectedDirective

Selector: `ng-template[neuSelectSelected]`

| Input | Required | Type |
| --- | --- | --- |
| neuSelectSelected | no | `import("@angular/core").InputSignal<"" \| readonly T[]>` |

| Output | Type |
| --- | --- |

## NeuSelectSelectionOptions

```typescript
export interface NeuSelectSelectionOptions {
    readonly chips?: boolean;
    readonly selectionLimit?: number;
    readonly maxSelectedLabels?: number;
    readonly toggleAll?: boolean;
    readonly toggleAllScope?: "filtered" | "loaded";
}
```

## NeuSelectSize

```typescript
export type NeuSelectSize = 'sm' | 'md' | 'lg';
```

## NeuSelectVariant

```typescript
export type NeuSelectVariant = 'outline' | 'solid';
```

