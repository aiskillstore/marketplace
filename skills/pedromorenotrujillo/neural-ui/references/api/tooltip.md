# @neural-ui/core/tooltip

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuTooltipDirective

Selector: `[neuTooltip]`

| Input | Required | Type |
| --- | --- | --- |
| neuTooltip | yes | `import("@angular/core").InputSignal<string>` |
| neuTooltipPosition | no | `import("@angular/core").InputSignal<NeuTooltipPosition>` |
| neuTooltipDisabled | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |

Supported imperative members:

```typescript
show(): void;
hide(): void;
```

## NeuTooltipPosition

```typescript
type NeuTooltipPosition = 'top' | 'bottom' | 'left' | 'right';
```

