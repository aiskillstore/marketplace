# @neural-ui/core/scroll-top

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuScrollTopBehavior

```typescript
export type NeuScrollTopBehavior = 'auto' | 'smooth';
```

## NeuScrollTopComponent

Selector: `neu-scroll-top`

| Input | Required | Type |
| --- | --- | --- |
| target | no | `import("@angular/core").InputSignal<NeuScrollTopTarget>` |
| threshold | no | `import("@angular/core").InputSignal<number>` |
| behavior | no | `import("@angular/core").InputSignal<NeuScrollTopBehavior>` |
| icon | no | `import("@angular/core").InputSignal<string>` |
| buttonAriaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuScrollTopIconDirective

Selector: `ng-template[neuScrollTopIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuScrollTopTarget

```typescript
export type NeuScrollTopTarget = 'window' | 'parent';
```

