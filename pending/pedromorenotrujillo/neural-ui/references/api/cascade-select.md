# @neural-ui/core/cascade-select

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuCascadeSelectComponent

Selector: `neu-cascade-select`

| Input | Required | Type |
| --- | --- | --- |
| options | no | `import("@angular/core").InputSignal<readonly T[]>` |
| optionLabel | no | `import("@angular/core").InputSignal<NeuOptionLabelAccessor$1<T> \| null>` |
| optionValue | no | `import("@angular/core").InputSignal<(option: T) => V>` |
| compareWith | no | `import("@angular/core").InputSignal<(left: V, right: V) => boolean>` |
| optionDisabled | no | `import("@angular/core").InputSignal<NeuOptionDisabledAccessor$1<T> \| null>` |
| optionChildren | no | `import("@angular/core").InputSignal<NeuOptionAccessor$1<T, readonly T[]> \| null>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| rootLabel | no | `import("@angular/core").InputSignal<string>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |
| breadcrumbAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| backAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| clearAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| clearable | no | `import("@angular/core").InputSignal<boolean>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| value | no | `import("@angular/core").ModelSignal<V \| null>` |

| Output | Type |
| --- | --- |
| touch | `import("@angular/core").OutputEmitterRef<void>` |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| groupChange | `import("@angular/core").OutputEmitterRef<readonly T[]>` |
| optionActivated | `import("@angular/core").OutputEmitterRef<NeuOptionActivatedEvent<T, V>>` |
| valueChange | `import("@angular/core").ModelSignal<V \| null>` |

## NeuCascadeSelectEmptyDirective

Selector: `ng-template[neuCascadeSelectEmpty]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCascadeSelectFooterDirective

Selector: `ng-template[neuCascadeSelectFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCascadeSelectHeaderDirective

Selector: `ng-template[neuCascadeSelectHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCascadeSelectItemContext

```typescript
export interface NeuCascadeSelectItemContext<T> {
    $implicit: T;
    depth: number;
    hasChildren: boolean;
}
```

## NeuCascadeSelectItemDirective

Selector: `ng-template[neuCascadeSelectItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCascadeSelectNode

```typescript
export interface NeuCascadeSelectNode<V = string> {
    value: V;
    label: string;
    disabled?: boolean;
    children?: readonly NeuCascadeSelectNode<V>[];
    data?: unknown;
}
```

## NeuCascadeSelectSelectedContext

```typescript
export interface NeuCascadeSelectSelectedContext<T> {
    $implicit: T | null;
}
```

## NeuCascadeSelectSelectedDirective

Selector: `ng-template[neuCascadeSelectSelected]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

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

