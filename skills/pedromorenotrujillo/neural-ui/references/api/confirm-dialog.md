# @neural-ui/core/confirm-dialog

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuConfirmDialogComponent

Selector: `neu-confirm-dialog`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuConfirmDialogData

```typescript
export interface NeuConfirmDialogData {
    title?: string;
    message: string;
    acceptLabel?: string;
    rejectLabel?: string;
    rejectVariant?: "secondary" | "danger";
    acceptVariant?: "primary" | "danger";
}
```

## NeuConfirmDialogService

Supported imperative members:

```typescript
confirm(data: NeuConfirmDialogData): Promise<boolean>;
```

