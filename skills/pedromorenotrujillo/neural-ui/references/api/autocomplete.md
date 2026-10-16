# @neural-ui/core/autocomplete

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuAutocompleteClearEvent

```typescript
export interface NeuAutocompleteClearEvent<V, F extends NeuAutocompleteMode = "strict"> {
    readonly originalEvent: Event | null;
    readonly previousValue: NeuAutocompleteValue<V, F>;
    readonly previousText: string;
    readonly reason: "button" | "input" | "force-selection" | "programmatic";
}
```

## NeuAutocompleteClearIconDirective

Selector: `ng-template[neuAutocompleteClearIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAutocompleteCompleteEvent

```typescript
export interface NeuAutocompleteCompleteEvent {
    readonly originalEvent: Event | null;
    readonly query: string;
    readonly source: NeuAutocompleteCompletionSource;
    readonly requestId: number;
}
```

## NeuAutocompleteCompletionSource

```typescript
export type NeuAutocompleteCompletionSource = 'input' | 'focus' | 'dropdown' | 'programmatic';
```

## NeuAutocompleteComponent

Selector: `neu-autocomplete`

| Input | Required | Type |
| --- | --- | --- |
| options | no | `import("@angular/core").InputSignal<readonly T[]>` |
| suggestions | no | `import("@angular/core").InputSignal<readonly T[] \| null>` |
| groups | no | `import("@angular/core").InputSignal<readonly G[]>` |
| groupSuggestions | no | `import("@angular/core").InputSignal<readonly G[] \| null>` |
| groupConfig | no | `import("@angular/core").InputSignal<NeuOptionGroupConfig$1<T, G> \| null>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor$1<T> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<NeuOptionValueAccessor$1<T, V> \| null>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor$1<T> \| null>` |
| compareWith | no | `import("@angular/core").InputSignal<(left: V, right: V) => boolean>` |
| minQueryLength | no | `import("@angular/core").InputSignal<number>` |
| delay | no | `import("@angular/core").InputSignal<number>` |
| completeOnFocus | no | `import("@angular/core").InputSignal<boolean>` |
| dropdown | no | `import("@angular/core").InputSignal<boolean>` |
| dropdownMode | no | `import("@angular/core").InputSignal<NeuAutocompleteDropdownMode>` |
| mode | no | `import("@angular/core").InputSignal<F>` |
| filterConfig | no | `import("@angular/core").InputSignal<Readonly<NeuOptionFilterConfig<T>>>` |
| autoHighlight | no | `import("@angular/core").InputSignal<boolean>` |
| autoOptionFocus | no | `import("@angular/core").InputSignal<boolean>` |
| selectOnFocus | no | `import("@angular/core").InputSignal<boolean>` |
| focusOnHover | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| loading | no | `import("@angular/core").InputSignal<boolean>` |
| id | no | `import("@angular/core").InputSignal<string \| null>` |
| inputId | no | `import("@angular/core").InputSignal<string \| null>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| type | no | `import("@angular/core").InputSignal<string>` |
| autocomplete | no | `import("@angular/core").InputSignal<string>` |
| autofocus | no | `import("@angular/core").InputSignal<boolean>` |
| tabindex | no | `import("@angular/core").InputSignal<number>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| inputSize | no | `import("@angular/core").InputSignal<number \| null>` |
| minLength | no | `import("@angular/core").InputSignal<number \| undefined>` |
| maxLength | no | `import("@angular/core").InputSignal<number \| undefined>` |
| pattern | no | `import("@angular/core").InputSignal<readonly RegExp[]>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string \| null>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| errorMessage | no | `import("@angular/core").InputSignal<string>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |
| showEmptyMessage | no | `import("@angular/core").InputSignal<boolean>` |
| loadingLabel | no | `import("@angular/core").InputSignal<string>` |
| searchMessage | no | `import("@angular/core").InputSignal<string \| null>` |
| emptySelectionMessage | no | `import("@angular/core").InputSignal<string>` |
| selectionMessage | no | `import("@angular/core").InputSignal<string>` |
| dropdownAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| clearAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| listAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| clearable | no | `import("@angular/core").InputSignal<boolean>` |
| floatingLabel | no | `import("@angular/core").InputSignal<boolean>` |
| size | no | `import("@angular/core").InputSignal<NeuAutocompleteSize>` |
| variant | no | `import("@angular/core").InputSignal<NeuAutocompleteVariant>` |
| fluid | no | `import("@angular/core").InputSignal<boolean>` |
| scrollHeight | no | `import("@angular/core").InputSignal<string>` |
| virtualScroll | no | `import("@angular/core").InputSignal<boolean>` |
| virtualScrollVisibleItems | no | `import("@angular/core").InputSignal<number>` |
| virtualScrollItemSize | no | `import("@angular/core").InputSignal<number \| null>` |
| virtualScrollBuffer | no | `import("@angular/core").InputSignal<number>` |
| lazy | no | `import("@angular/core").InputSignal<boolean>` |
| dataFirst | no | `import("@angular/core").InputSignal<number>` |
| totalItems | no | `import("@angular/core").InputSignal<number \| null>` |
| value | no | `import("@angular/core").ModelSignal<NeuAutocompleteValue<V, F>>` |

| Output | Type |
| --- | --- |
| suggestionsRequest | `import("@angular/core").OutputEmitterRef<NeuAutocompleteSuggestionsRequest>` |
| optionActivated | `import("@angular/core").OutputEmitterRef<NeuOptionActivatedEvent<T, V>>` |
| focusEntered | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| focusLeft | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| dropdownClick | `import("@angular/core").OutputEmitterRef<NeuAutocompleteDropdownClickEvent>` |
| cleared | `import("@angular/core").OutputEmitterRef<NeuAutocompleteClearEvent<V, F>>` |
| inputKeydown | `import("@angular/core").OutputEmitterRef<KeyboardEvent>` |
| keyUp | `import("@angular/core").OutputEmitterRef<KeyboardEvent>` |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| queryChange | `import("@angular/core").OutputEmitterRef<string>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |
| valueChange | `import("@angular/core").ModelSignal<NeuAutocompleteValue<V, F>>` |

Supported imperative members:

```typescript
openAll(event?: Event | null): void;
selectOption(option: T, originalEvent?: Event | null): void;
clear(originalEvent?: Event | null, reason?: 'button' | 'force-selection' | 'programmatic'): void;
open(originalEvent?: Event | null, reason?: OverlayReason): void;
close(originalEvent?: Event | null, reason?: OverlayReason, restoreFocus?: boolean): void;
focus(): void;
reset(): void;
```

## NeuAutocompleteDropdownClickEvent

```typescript
export interface NeuAutocompleteDropdownClickEvent {
    readonly originalEvent: Event;
    readonly query: string;
    readonly mode: NeuAutocompleteDropdownMode;
}
```

## NeuAutocompleteDropdownIconDirective

Selector: `ng-template[neuAutocompleteDropdownIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAutocompleteDropdownMode

```typescript
export type NeuAutocompleteDropdownMode = 'blank' | 'current';
```

## NeuAutocompleteEmptyDirective

Selector: `ng-template[neuAutocompleteEmpty]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAutocompleteFooterDirective

Selector: `ng-template[neuAutocompleteFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAutocompleteGroupContext

```typescript
export type NeuAutocompleteGroupContext<G> = NeuOptionGroupTemplateContext<G>;
```

## NeuAutocompleteGroupDirective

Selector: `ng-template[neuAutocompleteGroup]`

| Input | Required | Type |
| --- | --- | --- |
| neuAutocompleteGroup | no | `import("@angular/core").InputSignal<"" \| readonly G[]>` |

| Output | Type |
| --- | --- |

## NeuAutocompleteHeaderDirective

Selector: `ng-template[neuAutocompleteHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAutocompleteIconContext

```typescript
export interface NeuAutocompleteIconContext {
    readonly $implicit: boolean;
    readonly active: boolean;
}
```

## NeuAutocompleteItemContext

```typescript
export interface NeuAutocompleteItemContext<T, V = unknown> extends NeuOptionTemplateContext<T> {
    readonly label: string;
    readonly value: V;
}
```

## NeuAutocompleteItemDirective

Selector: `ng-template[neuAutocompleteItem]`

| Input | Required | Type |
| --- | --- | --- |
| neuAutocompleteItem | no | `import("@angular/core").InputSignal<"" \| readonly T[]>` |

| Output | Type |
| --- | --- |

## NeuAutocompleteLoaderContext

```typescript
export type NeuAutocompleteLoaderContext = NeuOptionLoaderTemplateContext;
```

## NeuAutocompleteLoaderDirective

Selector: `ng-template[neuAutocompleteLoader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAutocompleteLoadingIconDirective

Selector: `ng-template[neuAutocompleteLoadingIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAutocompleteMode

```typescript
export type NeuAutocompleteMode = 'strict' | 'free-text';
```

## NeuAutocompleteOption

```typescript
export interface NeuAutocompleteOption<V = unknown> {
    readonly value: V;
    readonly label: string;
    readonly disabled?: boolean;
}
```

## NeuAutocompleteOverlayEvent

```typescript
export interface NeuAutocompleteOverlayEvent {
    readonly originalEvent: Event | null;
    readonly reason: "completion" | "focus" | "dropdown" | "keyboard" | "selection" | "clear" | "escape" | "outside" | "tab" | "programmatic";
}
```

## NeuAutocompleteSelectEvent

```typescript
export interface NeuAutocompleteSelectEvent<T, V> {
    readonly originalEvent: Event | null;
    readonly option: T;
    readonly value: V;
}
```

## NeuAutocompleteSize

```typescript
export type NeuAutocompleteSize = 'sm' | 'md' | 'lg';
```

## NeuAutocompleteSuggestionsRequest

```typescript
export interface NeuAutocompleteSuggestionsRequest {
    readonly query: string;
    readonly source: NeuAutocompleteCompletionSource;
    readonly requestId: number;
    readonly queryRevision: number;
    readonly range?: NeuViewportRange;
    readonly reason: "initial" | "query" | "viewport" | "retry";
}
```

## NeuAutocompleteValue

```typescript
export type NeuAutocompleteValue<V, F extends NeuAutocompleteMode = 'strict'> = F extends 'free-text' ? V | string | null : V | null;
```

## NeuAutocompleteVariant

```typescript
export type NeuAutocompleteVariant = 'outline' | 'solid';
```

## NeuOptionAccessor

```typescript
export type NeuOptionAccessor<T, R = unknown> = Exclude<keyof T, string> | NeuOptionPath<T> | ((option: T) => R);
```

## NeuOptionCompareWith

```typescript
export type NeuOptionCompareWith<V> = (left: V, right: V) => boolean;
```

## NeuOptionDisabledAccessor

```typescript
export type NeuOptionDisabledAccessor<T> = NeuOptionAccessor<T, boolean>;
```

## NeuOptionGroupConfig

```typescript
export interface NeuOptionGroupConfig<T, G> {
    readonly labelAccessor: NeuOptionAccessor<G, unknown>;
    readonly childrenAccessor: NeuOptionAccessor<G, readonly T[]>;
    readonly disabledAccessor?: NeuOptionAccessor<G, boolean> | null;
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

