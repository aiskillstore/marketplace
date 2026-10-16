# @neural-ui/core/confirm-popup

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuConfirmPopupComponent

Selector: `neu-confirm-popup`

| Input | Required | Type |
| --- | --- | --- |
| open | no | `import("@angular/core").InputSignal<boolean>` |
| title | no | `import("@angular/core").InputSignal<string>` |
| message | no | `import("@angular/core").InputSignal<string>` |
| acceptLabel | no | `import("@angular/core").InputSignal<string>` |
| rejectLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| accepted | `import("@angular/core").OutputEmitterRef<void>` |
| rejected | `import("@angular/core").OutputEmitterRef<void>` |

## NeuConfirmPopupOptions

```typescript
export interface NeuConfirmPopupOptions {
    title?: string;
    message: string;
    acceptLabel?: string;
    rejectLabel?: string;
}
```

## NeuConfirmPopupService

Supported imperative members:

```typescript
readonly state: import("@angular/core").WritableSignal<NeuConfirmPopupOptions | null>;
confirm(options: NeuConfirmPopupOptions): Promise<boolean>;
close(value: boolean): void;
```

