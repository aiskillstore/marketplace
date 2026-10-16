# @neural-ui/core/context-menu

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuContextMenuDirective

Selector: `[neuContextMenu]`

| Input | Required | Type |
| --- | --- | --- |
| neuContextMenu | no | `import("@angular/core").InputSignal<NeuContextMenuItem[]>` |
| neuContextMenuDisabled | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| menuItemClick | `import("@angular/core").OutputEmitterRef<NeuContextMenuItem>` |
| menuOpened | `import("@angular/core").OutputEmitterRef<void>` |
| menuClosed | `import("@angular/core").OutputEmitterRef<void>` |

Supported imperative members:

```typescript
openAt(x: number, y: number, origin?: HTMLElement | null, onClose?: () => void): void;
close(): void;
```

## NeuContextMenuItem

```typescript
interface NeuContextMenuItem {
    key: string;
    label: string;
    icon?: string;
    separator?: boolean;
    disabled?: boolean;
    tone?: "neutral" | "danger";
}
```

## NeuContextMenuItemContext

```typescript
interface NeuContextMenuItemContext {
    $implicit: NeuContextMenuItem;
}
```

## NeuContextMenuItemDirective

Selector: `ng-template[neuContextMenuItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

