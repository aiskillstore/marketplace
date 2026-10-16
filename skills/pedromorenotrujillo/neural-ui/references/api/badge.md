# @neural-ui/core/badge

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuBadgeComponent

Selector: `neu-badge`

| Input | Required | Type |
| --- | --- | --- |
| tone | no | `import("@angular/core").InputSignal<NeuBadgeTone>` |
| variant | no | `import("@angular/core").InputSignal<NeuBadgeVariant>` |
| size | no | `import("@angular/core").InputSignal<NeuBadgeSize>` |
| dot | no | `import("@angular/core").InputSignal<boolean>` |
| pill | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |

## NeuBadgeSize

```typescript
export type NeuBadgeSize = 'sm' | 'md';
```

## NeuBadgeTone

```typescript
export type NeuBadgeTone = 'neutral' | 'success' | 'info' | 'warning' | 'danger';
```

## NeuBadgeVariant

```typescript
export type NeuBadgeVariant = 'soft' | 'outline';
```

