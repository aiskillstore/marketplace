# @neural-ui/core/terminal

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuTerminalCommand

```typescript
export interface NeuTerminalCommand {
    command: string;
}
```

## NeuTerminalComponent

Selector: `neu-terminal`

| Input | Required | Type |
| --- | --- | --- |
| welcomeMessage | no | `import("@angular/core").InputSignal<string>` |
| prompt | no | `import("@angular/core").InputSignal<string>` |
| response | no | `import("@angular/core").InputSignal<string \| undefined>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| inputAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| output | no | `import("@angular/core").InputSignal<readonly NeuTerminalLine[]>` |

| Output | Type |
| --- | --- |
| commandSubmit | `import("@angular/core").OutputEmitterRef<NeuTerminalCommand>` |

## NeuTerminalLine

```typescript
export interface NeuTerminalLine {
    text: string;
    kind?: "output" | "error" | "info";
}
```

## TerminalEntry

```typescript
interface TerminalEntry {
    id: number;
    type: "command" | "output";
    text: string;
    kind?: NeuTerminalLine["kind"];
}
```

