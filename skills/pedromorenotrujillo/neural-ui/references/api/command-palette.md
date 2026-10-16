# @neural-ui/core/command-palette

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## firstEnabledId

```typescript
declare function firstEnabledId(entries: readonly NeuCommandEntry[]): string | null;
```

## groupCommands

```typescript
declare function groupCommands(entries: readonly NeuCommandEntry[]): readonly NeuCommandGroup[];
```

## NeuCommand

```typescript
export type NeuCommand = NeuCommandAction | NeuCommandRouterLink | NeuCommandLink;
```

## NeuCommandAction

```typescript
export interface NeuCommandAction extends NeuCommandBase {
    readonly kind: "action";
    readonly routerLink?: never;
    readonly href?: never;
    readonly target?: never;
    readonly action?: never;
}
```

## NeuCommandBase

```typescript
export interface NeuCommandBase {
    readonly id: string;
    readonly label: string;
    readonly description?: string;
    readonly icon?: string;
    readonly keywords?: readonly string[];
    readonly group?: string;
    readonly shortcut?: string;
    readonly disabled?: boolean;
}
```

## NeuCommandEntry

```typescript
interface NeuCommandEntry {
    readonly command: NeuCommand;
    readonly sourceIndex: number;
    readonly searchable: string;
    readonly routerCommands: string | unknown[] | null;
}
```

## NeuCommandGroup

```typescript
interface NeuCommandGroup {
    readonly key: string;
    readonly label: string | null;
    readonly entries: readonly NeuCommandEntry[];
}
```

## NeuCommandLink

```typescript
export interface NeuCommandLink extends NeuCommandBase {
    readonly kind: "link";
    readonly href: string;
    readonly target?: string;
    readonly routerLink?: never;
    readonly action?: never;
}
```

## NeuCommandPaletteComponent

Selector: `neu-command-palette`

| Input | Required | Type |
| --- | --- | --- |
| commands | no | `import("@angular/core").InputSignal<readonly NeuCommand[]>` |

| Output | Type |
| --- | --- |
| commandAction | `import("@angular/core").OutputEmitterRef<NeuCommandAction>` |

Supported imperative members:

```typescript
open(): void;
close(): void;
```

## NeuCommandPaletteItemContext

```typescript
export interface NeuCommandPaletteItemContext {
    readonly $implicit: NeuCommand;
    readonly index: number;
}
```

## NeuCommandPaletteItemDirective

Selector: `ng-template[neuCommandPaletteItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCommandRouterLink

```typescript
export interface NeuCommandRouterLink extends NeuCommandBase {
    readonly kind: "router";
    readonly routerLink: string | readonly unknown[];
    readonly href?: never;
    readonly target?: never;
    readonly action?: never;
}
```

## nextEnabledId

```typescript
declare function nextEnabledId(entries: readonly NeuCommandEntry[], currentId: string | null, direction: 1 | -1): string | null;
```

## normalizeCommandText

```typescript
declare function normalizeCommandText(value: string): string;
```

## prepareCommands

```typescript
declare function prepareCommands(commands: readonly NeuCommand[]): readonly NeuCommandEntry[];
```

## searchCommands

```typescript
declare function searchCommands(entries: readonly NeuCommandEntry[], query: string): readonly NeuCommandEntry[];
```

