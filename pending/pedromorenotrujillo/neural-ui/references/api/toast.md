# @neural-ui/core/toast

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuToastContainerComponent

Selector: `neu-toast-container`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuToastItem

```typescript
export interface NeuToastItem extends Required<Omit<NeuToastOptions, "title">> {
    id: string;
    title: string;
}
```

## NeuToastOptions

```typescript
export interface NeuToastOptions {
    message: string;
    tone?: NeuToastTone;
    duration?: number;
    title?: string;
}
```

## NeuToastPosition

```typescript
export type NeuToastPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
```

## NeuToastService

Supported imperative members:

```typescript
readonly toasts: import("@angular/core").WritableSignal<NeuToastItem[]>;
readonly position: import("@angular/core").WritableSignal<NeuToastPosition>;
setPosition(position: NeuToastPosition): void;
show(options: NeuToastOptions): string;
success(message: string, opts?: Partial<NeuToastOptions>): string;
error(message: string, opts?: Partial<NeuToastOptions>): string;
info(message: string, opts?: Partial<NeuToastOptions>): string;
warning(message: string, opts?: Partial<NeuToastOptions>): string;
dismiss(id: string): void;
clear(): void;
```

## NeuToastTone

```typescript
export type NeuToastTone = 'neutral' | 'success' | 'info' | 'warning' | 'danger';
```

