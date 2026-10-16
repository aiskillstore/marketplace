# @neural-ui/core/input-tags

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuInputTagsClearedEvent

```typescript
export interface NeuInputTagsClearedEvent<V> {
    readonly originalEvent: Event;
    readonly previousValue: readonly V[];
}
```

## NeuInputTagsComponent

Selector: `neu-input-tags`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<readonly V[]>` |
| options | no | `import("@angular/core").InputSignal<readonly T[]>` |
| groups | no | `import("@angular/core").InputSignal<readonly NeuInputTagsGroup<T>[]>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor<T> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<NeuOptionValueAccessor<T, V> \| null>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor<T> \| null>` |
| compareWith | no | `import("@angular/core").InputSignal<NeuOptionCompareWith<V>>` |
| textValue | no | `import("@angular/core").InputSignal<((text: string) => V \| null \| undefined) \| null>` |
| normalizeToken | no | `import("@angular/core").InputSignal<(text: string) => string>` |
| separators | no | `import("@angular/core").InputSignal<readonly string[]>` |
| allowDuplicates | no | `import("@angular/core").InputSignal<boolean>` |
| maxItems | no | `import("@angular/core").InputSignal<number \| null>` |
| commitOnBlur | no | `import("@angular/core").InputSignal<boolean>` |
| typeahead | no | `import("@angular/core").InputSignal<boolean>` |
| delay | no | `import("@angular/core").InputSignal<number>` |
| minQueryLength | no | `import("@angular/core").InputSignal<number>` |
| completeOnFocus | no | `import("@angular/core").InputSignal<boolean>` |
| autoOptionFocus | no | `import("@angular/core").InputSignal<boolean>` |
| focusOnHover | no | `import("@angular/core").InputSignal<boolean>` |
| loading | no | `import("@angular/core").InputSignal<boolean>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| removeLabel | no | `import("@angular/core").InputSignal<string>` |
| emptyMessage | no | `import("@angular/core").InputSignal<string>` |
| scrollHeight | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| autofocus | no | `import("@angular/core").InputSignal<boolean>` |
| tabindex | no | `import("@angular/core").InputSignal<number \| null>` |
| inputId | no | `import("@angular/core").InputSignal<string>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| autocomplete | no | `import("@angular/core").InputSignal<string>` |
| title | no | `import("@angular/core").InputSignal<string>` |
| minlength | no | `import("@angular/core").InputSignal<number \| null>` |
| maxlength | no | `import("@angular/core").InputSignal<number \| null>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string>` |
| ariaRequired | no | `import("@angular/core").InputSignal<boolean>` |
| size | no | `import("@angular/core").InputSignal<"sm" \| "md" \| "lg">` |
| variant | no | `import("@angular/core").InputSignal<"outline" \| "solid">` |
| fluid | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<readonly V[]>` |
| suggestionsRequest | `import("@angular/core").OutputEmitterRef<NeuOptionDataRequest>` |
| optionActivated | `import("@angular/core").OutputEmitterRef<NeuOptionActivatedEvent<T, V>>` |
| pasteResult | `import("@angular/core").OutputEmitterRef<NeuInputTagsPasteResult<V>>` |
| itemRemoved | `import("@angular/core").OutputEmitterRef<NeuInputTagsRemovedEvent<V>>` |
| itemReordered | `import("@angular/core").OutputEmitterRef<NeuInputTagsReorderedEvent<V>>` |
| cleared | `import("@angular/core").OutputEmitterRef<NeuInputTagsClearedEvent<V>>` |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| focusEntered | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| focusLeft | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

## NeuInputTagsFooterDirective

Selector: `ng-template[neuInputTagsFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuInputTagsGroup

```typescript
export interface NeuInputTagsGroup<T> {
    readonly label: string;
    readonly options: readonly T[];
    readonly disabled?: boolean;
}
```

## NeuInputTagsGroupDirective

Selector: `ng-template[neuInputTagsGroup]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuInputTagsGroupTemplateContext

```typescript
export interface NeuInputTagsGroupTemplateContext<T> {
    readonly $implicit: NeuInputTagsGroup<T>;
    readonly group: NeuInputTagsGroup<T>;
}
```

## NeuInputTagsHeaderDirective

Selector: `ng-template[neuInputTagsHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuInputTagsItemDirective

Selector: `ng-template[neuInputTagsItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuInputTagsItemTemplateContext

```typescript
export interface NeuInputTagsItemTemplateContext<T, V> {
    readonly $implicit: V;
    readonly value: V;
    readonly option: T | null;
    readonly index: number;
    readonly onRemove: (event: Event, index: number) => void;
}
```

## NeuInputTagsOptionDirective

Selector: `ng-template[neuInputTagsOption]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuInputTagsOptionTemplateContext

```typescript
export interface NeuInputTagsOptionTemplateContext<T, V> {
    readonly $implicit: T;
    readonly option: T;
    readonly value: V;
    readonly index: number;
}
```

## NeuInputTagsPasteResult

```typescript
export interface NeuInputTagsPasteResult<V> {
    readonly originalEvent: ClipboardEvent;
    readonly accepted: readonly V[];
    readonly rejected: readonly string[];
}
```

## NeuInputTagsRemovedEvent

```typescript
export interface NeuInputTagsRemovedEvent<V> {
    readonly originalEvent: Event;
    readonly value: V;
    readonly index: number;
}
```

## NeuInputTagsRemoveIconDirective

Selector: `ng-template[neuInputTagsRemoveIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuInputTagsReorderedEvent

```typescript
export interface NeuInputTagsReorderedEvent<V> {
    readonly originalEvent: Event;
    readonly value: V;
    readonly from: number;
    readonly to: number;
}
```

