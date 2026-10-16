# @neural-ui/core/dock

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuDockComponent

Selector: `neu-dock`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<NeuDockItem[]>` |
| position | no | `import("@angular/core").InputSignal<NeuDockPosition>` |
| breakpoint | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string \| null>` |
| magnification | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| direction | no | `import("@angular/core").InputSignal<NeuTextDirection>` |

| Output | Type |
| --- | --- |
| itemClick | `import("@angular/core").OutputEmitterRef<NeuDockItem>` |
| itemFocus | `import("@angular/core").OutputEmitterRef<FocusEvent>` |
| itemBlur | `import("@angular/core").OutputEmitterRef<FocusEvent>` |

## NeuDockItem

```typescript
export interface NeuDockItem extends NeuMenuActionLike<NeuDockItem> {
    key: string;
    label: string;
    data?: unknown;
}
```

## NeuDockItemDirective

Selector: `ng-template[neuDockItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuDockItemTemplateContext

```typescript
export interface NeuDockItemTemplateContext {
    $implicit: NeuDockItem;
    index: number;
    active: boolean;
}
```

## NeuDockPosition

```typescript
export type NeuDockPosition = 'top' | 'right' | 'bottom' | 'left';
```

