# @neural-ui/core/accordion

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuAccordionBodyContext

```typescript
export interface NeuAccordionBodyContext<T extends NeuAccordionItem<NeuAccordionKey> = NeuAccordionItem<NeuAccordionKey>> {
    readonly $implicit: T;
    readonly expanded: boolean;
}
```

## NeuAccordionBodyDirective

Selector: `ng-template[neuAccordionBody]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAccordionComponent

Selector: `neu-accordion`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<readonly T[]>` |
| multiple | no | `import("@angular/core").InputSignal<boolean>` |
| bordered | no | `import("@angular/core").InputSignal<boolean>` |
| expandedKeys | no | `import("@angular/core").InputSignal<readonly K[] \| undefined>` |
| initialExpandedKeys | no | `import("@angular/core").InputSignal<readonly K[]>` |

| Output | Type |
| --- | --- |
| expandedKeysChange | `import("@angular/core").OutputEmitterRef<readonly K[]>` |
| panelToggle | `import("@angular/core").OutputEmitterRef<NeuAccordionPanelToggle<K>>` |

## NeuAccordionHeaderContext

```typescript
export interface NeuAccordionHeaderContext<T extends NeuAccordionItem<NeuAccordionKey> = NeuAccordionItem<NeuAccordionKey>> {
    readonly $implicit: T;
    readonly expanded: boolean;
}
```

## NeuAccordionHeaderDirective

Selector: `ng-template[neuAccordionHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuAccordionItem

```typescript
export interface NeuAccordionItem<K extends NeuAccordionKey = string> {
    readonly id: K;
    readonly title: string;
    readonly content?: string;
    readonly disabled?: boolean;
}
```

## NeuAccordionKey

```typescript
export type NeuAccordionKey = string | number;
```

## NeuAccordionPanelToggle

```typescript
export interface NeuAccordionPanelToggle<K extends NeuAccordionKey = string> {
    readonly id: K;
    readonly expanded: boolean;
}
```

