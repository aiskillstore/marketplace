# @neural-ui/core/mega-menu

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuMegaMenuColumn

```typescript
export interface NeuMegaMenuColumn {
    readonly key: string;
    readonly groups: readonly NeuMegaMenuGroup[];
}
```

## NeuMegaMenuCommand

```typescript
type NeuMegaMenuCommand = (event: {
    originalEvent: Event;
    item: NeuMegaMenuItem | NeuMegaMenuLeaf;
}) => void;
```

## NeuMegaMenuComponent

Selector: `neu-mega-menu`

| Input | Required | Type |
| --- | --- | --- |
| id | no | `import("@angular/core").InputSignal<string \| undefined>` |
| items | no | `import("@angular/core").InputSignal<readonly NeuMegaMenuItem[]>` |
| orientation | no | `import("@angular/core").InputSignal<NeuMegaMenuOrientation>` |
| breakpoint | no | `import("@angular/core").InputSignal<string>` |
| scrollHeight | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string \| null>` |
| menuButtonAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| direction | no | `import("@angular/core").InputSignal<NeuTextDirection>` |

| Output | Type |
| --- | --- |
| itemClick | `import("@angular/core").OutputEmitterRef<NeuMegaMenuItem \| NeuMegaMenuLeaf>` |
| mobileActiveChange | `import("@angular/core").OutputEmitterRef<boolean>` |

## NeuMegaMenuDestination

```typescript
type NeuMegaMenuDestination = {
    readonly routerLink: string | unknown[];
    readonly url?: never;
    readonly target?: never;
    readonly rel?: never;
} | {
    readonly url: string;
    readonly routerLink?: never;
    readonly target?: string;
    readonly rel?: string;
};
```

## NeuMegaMenuEndDirective

Selector: `ng-template[neuMegaMenuEnd]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuMegaMenuEntry

```typescript
interface NeuMegaMenuEntry {
    readonly key: string;
    readonly label: string;
    readonly icon?: NeuIconKey;
    readonly badge?: string | number;
    readonly active?: boolean;
    readonly disabled?: boolean;
    readonly visible?: boolean;
    readonly tooltip?: string;
    readonly data?: unknown;
}
```

## NeuMegaMenuGroup

```typescript
export interface NeuMegaMenuGroup {
    readonly key: string;
    readonly label?: string;
    readonly items: readonly NeuMegaMenuLeaf[];
}
```

## NeuMegaMenuItem

```typescript
export type NeuMegaMenuItem = (NeuMegaMenuEntry & NeuMegaMenuDestination & {
    readonly kind: 'link';
    readonly command?: never;
    readonly panel?: never;
}) | (NeuMegaMenuEntry & {
    readonly kind: 'command';
    readonly command: NeuMegaMenuCommand;
    readonly url?: never;
    readonly routerLink?: never;
    readonly panel?: never;
}) | (NeuMegaMenuEntry & {
    readonly kind: 'panel';
    readonly panel: NeuMegaMenuPanel;
    readonly url?: never;
    readonly routerLink?: never;
    readonly command?: never;
});
```

## NeuMegaMenuItemDirective

Selector: `ng-template[neuMegaMenuItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuMegaMenuItemTemplateContext

```typescript
export interface NeuMegaMenuItemTemplateContext {
    $implicit: NeuMegaMenuItem | NeuMegaMenuLeaf;
    index: number;
    level: 0 | 3;
    active: boolean;
}
```

## NeuMegaMenuLeaf

```typescript
export type NeuMegaMenuLeaf = (NeuMegaMenuEntry & NeuMegaMenuDestination & {
    readonly kind: 'link';
    readonly command?: never;
    readonly panel?: never;
}) | (NeuMegaMenuEntry & {
    readonly kind: 'command';
    readonly command: NeuMegaMenuCommand;
    readonly url?: never;
    readonly routerLink?: never;
    readonly panel?: never;
});
```

## NeuMegaMenuOrientation

```typescript
export type NeuMegaMenuOrientation = 'horizontal' | 'vertical';
```

## NeuMegaMenuPanel

```typescript
export interface NeuMegaMenuPanel {
    readonly columns: readonly NeuMegaMenuColumn[];
}
```

## NeuMegaMenuStartDirective

Selector: `ng-template[neuMegaMenuStart]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## ValidatedMegaMenu

```typescript
interface ValidatedMegaMenu {
    roots: readonly NeuMegaMenuItem[];
    invalid: ReadonlySet<string>;
}
```

