# @neural-ui/core/tabs

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuTab

```typescript
interface NeuTab<K extends NeuTabKey = string> {
    readonly id: K;
    readonly label: string;
    readonly badge?: string;
    readonly disabled?: boolean;
}
```

## NeuTabKey

```typescript
type NeuTabKey = string | number;
```

## NeuTabLabelContext

```typescript
interface NeuTabLabelContext<T extends NeuTab<NeuTabKey> = NeuTab<NeuTabKey>> {
    readonly $implicit: T;
    readonly active: boolean;
}
```

## NeuTabLabelDirective

Selector: `ng-template[neuTabLabel]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTabPanelComponent

Selector: `neu-tab-panel`

| Input | Required | Type |
| --- | --- | --- |
| tabId | yes | `import("@angular/core").InputSignal<K>` |

| Output | Type |
| --- | --- |

## NeuTabsComponent

Selector: `neu-tabs`

| Input | Required | Type |
| --- | --- | --- |
| tabs | no | `import("@angular/core").InputSignal<readonly T[]>` |
| activeId | no | `import("@angular/core").InputSignal<K \| null \| undefined>` |
| initialActiveId | no | `import("@angular/core").InputSignal<K \| null>` |
| flush | no | `import("@angular/core").InputSignal<boolean>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| activeIdChange | `import("@angular/core").OutputEmitterRef<K \| null>` |

