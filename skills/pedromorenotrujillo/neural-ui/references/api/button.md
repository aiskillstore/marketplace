# @neural-ui/core/button

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuButtonComponent

Selector: `button[neu-button]`

| Input | Required | Type |
| --- | --- | --- |
| tone | no | `import("@angular/core").InputSignal<NeuButtonTone>` |
| variant | no | `import("@angular/core").InputSignal<NeuButtonVariant>` |
| size | no | `import("@angular/core").InputSignal<NeuButtonSize>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| loading | no | `import("@angular/core").InputSignal<boolean>` |
| fullWidth | no | `import("@angular/core").InputSignal<boolean>` |
| icon | no | `import("@angular/core").InputSignal<string \| null>` |
| iconPosition | no | `import("@angular/core").InputSignal<NeuButtonIconPosition>` |
| iconOnly | no | `import("@angular/core").InputSignal<boolean>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| neuClick | `import("@angular/core").OutputEmitterRef<MouseEvent>` |

## NeuButtonIconPosition

```typescript
export type NeuButtonIconPosition = 'start' | 'end';
```

## NeuButtonSize

```typescript
export type NeuButtonSize = 'sm' | 'md' | 'lg';
```

## NeuButtonTone

```typescript
export type NeuButtonTone = 'neutral' | 'brand' | 'success' | 'info' | 'warning' | 'danger';
```

## NeuButtonVariant

```typescript
export type NeuButtonVariant = 'solid' | 'outline' | 'ghost';
```

