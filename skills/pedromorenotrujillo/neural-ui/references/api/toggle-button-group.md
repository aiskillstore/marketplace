# @neural-ui/core/toggle-button-group

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

## NeuToggleButtonGroupComponent

Selector: `neu-toggle-button-group`

| Input | Required | Type |
| --- | --- | --- |
| options | no | `import("@angular/core").InputSignal<readonly NeuToggleOptionModel<T, V>[]>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor$1<NeuToggleOptionModel<T, V>> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<(option: NeuToggleOptionModel<T, V>) => NeuToggleValue<T, V>>` |
| compareWith | no | `import("@angular/core").InputSignal<(left: NeuToggleValue<T, V>, right: NeuToggleValue<T, V>) => boolean>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor$1<NeuToggleOptionModel<T, V>> \| null>` |
| mode | no | `import("@angular/core").InputSignal<M>` |
| deselectable | no | `import("@angular/core").InputSignal<boolean>` |
| size | no | `import("@angular/core").InputSignal<NeuButtonSize>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| value | no | `import("@angular/core").ModelSignal<NeuSelectionValue<NeuToggleValue<T, V>, M>>` |

| Output | Type |
| --- | --- |
| touch | `import("@angular/core").OutputEmitterRef<void>` |
| optionActivated | `import("@angular/core").OutputEmitterRef<NeuOptionActivatedEvent<NeuToggleOptionModel<T, V>, NeuToggleValue<T, V>>>` |
| valueChange | `import("@angular/core").ModelSignal<NeuSelectionValue<NeuToggleValue<T, V>, M>>` |

## NeuToggleButtonItemDirective

Selector: `ng-template[neuToggleButtonItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuToggleOption

```typescript
export interface NeuToggleOption<T = unknown> {
    label: string;
    value: T;
    icon?: NeuIconKey;
    disabled?: boolean;
}
```

