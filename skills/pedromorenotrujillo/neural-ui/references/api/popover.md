# @neural-ui/core/popover

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuPopoverDirective

Selector: `[neuPopover]`

| Input | Required | Type |
| --- | --- | --- |
| neuPopover | no | `import("@angular/core").InputSignal<TemplateRef<unknown> \| null>` |
| neuPopoverText | no | `import("@angular/core").InputSignal<string>` |
| neuPopoverPosition | no | `import("@angular/core").InputSignal<NeuPopoverPosition>` |
| neuPopoverTrigger | no | `import("@angular/core").InputSignal<NeuPopoverTrigger>` |
| neuPopoverDisabled | no | `import("@angular/core").InputSignal<boolean>` |
| neuPopoverContext | no | `import("@angular/core").InputSignal<unknown>` |

| Output | Type |
| --- | --- |
| popoverOpened | `import("@angular/core").OutputEmitterRef<void>` |
| popoverClosed | `import("@angular/core").OutputEmitterRef<void>` |

Supported imperative members:

```typescript
open(): void;
close(): void;
toggle(): void;
```

## NeuPopoverPosition

```typescript
type NeuPopoverPosition = 'top' | 'bottom' | 'left' | 'right';
```

## NeuPopoverTrigger

```typescript
type NeuPopoverTrigger = 'click' | 'hover' | 'focus';
```

