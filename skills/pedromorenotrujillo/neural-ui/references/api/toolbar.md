# @neural-ui/core/toolbar

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuToolbarComponent

Selector: `neu-toolbar`

| Input | Required | Type |
| --- | --- | --- |
| size | no | `import("@angular/core").InputSignal<NeuToolbarSize>` |
| shadow | no | `import("@angular/core").InputSignal<boolean>` |
| bordered | no | `import("@angular/core").InputSignal<boolean>` |
| density | no | `import("@angular/core").InputSignal<NeuDensity>` |
| wrap | no | `import("@angular/core").InputSignal<NeuToolbarWrap>` |
| tone | no | `import("@angular/core").InputSignal<NeuToolbarTone>` |
| variant | no | `import("@angular/core").InputSignal<NeuToolbarVariant>` |

| Output | Type |
| --- | --- |

## NeuToolbarSize

```typescript
export type NeuToolbarSize = 'sm' | 'md' | 'lg';
```

## NeuToolbarTone

```typescript
export type NeuToolbarTone = 'neutral' | 'brand' | 'success' | 'info' | 'warning' | 'danger';
```

## NeuToolbarVariant

```typescript
export type NeuToolbarVariant = 'solid' | 'soft' | 'ghost';
```

## NeuToolbarWrap

```typescript
export type NeuToolbarWrap = 'nowrap' | 'wrap';
```

