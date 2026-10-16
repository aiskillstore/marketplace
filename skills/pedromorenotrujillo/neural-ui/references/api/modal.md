# @neural-ui/core/modal

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuDialogComponent

Selector: `neu-dialog`

| Input | Required | Type |
| --- | --- | --- |
| open | no | `import("@angular/core").InputSignal<boolean>` |
| title | no | `import("@angular/core").InputSignal<string>` |
| size | no | `import("@angular/core").InputSignal<NeuDialogSize>` |
| layout | no | `import("@angular/core").InputSignal<NeuDialogLayout>` |
| disableClose | no | `import("@angular/core").InputSignal<boolean>` |
| responsive | no | `import("@angular/core").InputSignal<boolean>` |
| restoreFocus | no | `import("@angular/core").InputSignal<boolean>` |
| draggable | no | `import("@angular/core").InputSignal<boolean>` |
| resizable | no | `import("@angular/core").InputSignal<boolean>` |
| maximizable | no | `import("@angular/core").InputSignal<boolean>` |
| maximized | no | `import("@angular/core").InputSignal<boolean \| undefined>` |
| maximizeLabel | no | `import("@angular/core").InputSignal<string>` |
| restoreLabel | no | `import("@angular/core").InputSignal<string>` |
| resizeLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| closeRequested | `import("@angular/core").OutputEmitterRef<NeuCloseRequest>` |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| maximizedChange | `import("@angular/core").OutputEmitterRef<boolean>` |

## NeuDialogData

```typescript
export interface NeuDialogData<T = unknown> {
    title?: string;
    data?: T;
}
```

## NeuDialogLayout

```typescript
export type NeuDialogLayout = 'auto' | 'viewport';
```

## NeuDialogService

Supported imperative members:

```typescript
open<T = unknown, R = unknown>(component: Type<unknown>, config?: {
    title?: string;
    data?: T;
    size?: NeuDialogSize;
    layout?: NeuDialogLayout;
    responsive?: boolean;
    disableClose?: boolean;
    restoreFocus?: boolean;
}): DialogRef<R>;
```

## NeuDialogSize

```typescript
export type NeuDialogSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';
```

