# @neural-ui/core/menu

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuMenubarComponent

Selector: `neu-menubar`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<NeuMenuItem$1[]>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| itemClick | `import("@angular/core").OutputEmitterRef<NeuMenuItem$1>` |

## NeuMenuButtonComponent

Selector: `neu-menu-button`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<NeuMenuItem$1[]>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| itemClick | `import("@angular/core").OutputEmitterRef<NeuMenuItem$1>` |
| openChange | `import("@angular/core").OutputEmitterRef<boolean>` |

## NeuMenuComponent

Selector: `neu-menu`

| Input | Required | Type |
| --- | --- | --- |
| itemTemplate | no | `import("@angular/core").InputSignal<TemplateRef<{
    $implicit: NeuMenuItem$1;
}> \| null>` |
| items | no | `import("@angular/core").InputSignal<NeuMenuItem$1[]>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| expandedKeys | no | `import("@angular/core").InputSignal<readonly string[] \| undefined>` |

| Output | Type |
| --- | --- |
| expandedKeysChange | `import("@angular/core").OutputEmitterRef<string[]>` |
| itemClick | `import("@angular/core").OutputEmitterRef<NeuMenuItem$1>` |

Supported imperative members:

```typescript
activate(item: NeuMenuItem$1, originalEvent?: Event): void;
```

## NeuMenuItem

```typescript
interface NeuMenuItem {
    key: string;
    label: string;
    icon?: NeuIconKey;
    badge?: string | number;
    active?: boolean;
    command?: (event: {
        originalEvent: Event;
        item: NeuMenuItem;
    }) => void;
    routerLink?: string | unknown[];
    url?: string;
    target?: string;
    rel?: string;
    tooltip?: string;
    visible?: boolean;
    shortcut?: string;
    disabled?: boolean;
    separator?: boolean;
    children?: NeuMenuItem[];
    data?: unknown;
}
```

## NeuMenuItemDirective

Selector: `ng-template[neuMenuItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTieredMenuComponent

Selector: `neu-tiered-menu`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<NeuMenuItem[]>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| expandedKeys | no | `import("@angular/core").InputSignal<readonly string[] \| undefined>` |

| Output | Type |
| --- | --- |
| expandedKeysChange | `import("@angular/core").OutputEmitterRef<string[]>` |
| itemClick | `import("@angular/core").OutputEmitterRef<NeuMenuItem>` |

