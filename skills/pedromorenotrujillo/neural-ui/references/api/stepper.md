# @neural-ui/core/stepper

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuStepperComponent

Selector: `neu-stepper`

| Input | Required | Type |
| --- | --- | --- |
| steps | no | `import("@angular/core").InputSignal<NeuStepperStep[]>` |
| activeStep | no | `import("@angular/core").InputSignal<number>` |
| linear | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| stepChange | `import("@angular/core").OutputEmitterRef<number>` |

Supported imperative members:

```typescript
goTo(i: number): void;
next(): void;
prev(): void;
```

## NeuStepperStep

```typescript
export interface NeuStepperStep {
    label: string;
    description?: string;
    completed?: boolean;
    disabled?: boolean;
}
```

