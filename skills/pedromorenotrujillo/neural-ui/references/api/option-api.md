# @neural-ui/core/option-api

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## deserializeNeuOptionValue

```typescript
export declare function deserializeNeuOptionValue(serialized: string): string | number | boolean;
```

## NeuIndexRange

```typescript
export interface NeuIndexRange {
    readonly start: number;
    readonly end: number;
}
```

## NeuOptionAccessor

```typescript
export type NeuOptionAccessor<T, R = unknown> = Exclude<keyof T, string> | NeuOptionPath<T> | ((option: T) => R);
```

## NeuOptionActivatedEvent

```typescript
export interface NeuOptionActivatedEvent<T, V> {
    readonly option: T;
    readonly value: V;
    readonly source: "pointer" | "keyboard";
    readonly originalEvent?: Event;
}
```

## NeuOptionCompareWith

```typescript
export type NeuOptionCompareWith<V> = (left: V, right: V) => boolean;
```

## NeuOptionDataRequest

```typescript
export interface NeuOptionDataRequest {
    readonly requestId: number;
    readonly queryRevision: number;
    readonly query: string;
    readonly range?: NeuViewportRange;
    readonly reason: "initial" | "query" | "viewport" | "retry";
}
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

## NeuOptionFilterStrategy

```typescript
export type NeuOptionFilterStrategy = 'client' | 'server';
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

## NeuOptionLazyRequestReason

```typescript
export type NeuOptionLazyRequestReason = 'initial' | 'scroll' | 'filter' | 'reset' | 'programmatic';
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

## NeuOptionPath

```typescript
export type NeuOptionPath<T> = Extract<keyof T, string> | `${Extract<keyof T, string>}.${string}`;
```

## neuOptionsEqual

```typescript
export declare function neuOptionsEqual<T, V = NeuOptionValue<T>, I = unknown>(left: T, right: T, config?: NeuOptionIdentityConfig<T, V, I>): boolean;
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

## neuOptionValuesEqual

```typescript
export declare function neuOptionValuesEqual<V>(left: V, right: V): boolean;
```

## NeuSelectionMode

```typescript
export type NeuSelectionMode = 'single' | 'multiple';
```

## NeuSelectionValue

```typescript
export type NeuSelectionValue<V, M extends NeuSelectionMode> = M extends 'multiple' ? readonly V[] : V | null;
```

## NeuViewportRange

```typescript
export interface NeuViewportRange {
    readonly render: NeuIndexRange;
    readonly visible: NeuIndexRange;
}
```

## readNeuOptionAccessor

```typescript
export declare function readNeuOptionAccessor<T, R>(option: T, accessor: NeuOptionAccessor<T, R>): R | undefined;
```

## resolveNeuOptionDisabled

```typescript
export declare function resolveNeuOptionDisabled<T>(option: T, accessor?: NeuOptionAccessor<T> | null): boolean;
```

## resolveNeuOptionGroup

```typescript
export declare function resolveNeuOptionGroup<T>(option: T): string | undefined;
```

## resolveNeuOptionGroupChildren

```typescript
export declare function resolveNeuOptionGroupChildren<T, G>(group: G, config: NeuOptionGroupConfig<T, G>): readonly T[];
```

## resolveNeuOptionGroupDisabled

```typescript
export declare function resolveNeuOptionGroupDisabled<T, G>(group: G, config: NeuOptionGroupConfig<T, G>): boolean;
```

## resolveNeuOptionGroupLabel

```typescript
export declare function resolveNeuOptionGroupLabel<T, G>(group: G, config: NeuOptionGroupConfig<T, G>): string;
```

## resolveNeuOptionLabel

```typescript
export declare function resolveNeuOptionLabel<T>(option: T, accessor?: NeuOptionAccessor<T> | null): string;
```

## resolveNeuOptionValue

```typescript
export declare function resolveNeuOptionValue<T, V = NeuOptionValue<T>>(option: T, accessor?: NeuOptionAccessor<T, V> | null): V;
```

## serializeNeuOptionValue

```typescript
export declare function serializeNeuOptionValue(value: unknown): string | null;
```

