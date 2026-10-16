# @neural-ui/core/tag

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuTagComponent

Selector: `neu-tag`

| Input | Required | Type |
| --- | --- | --- |
| tone | no | `import("@angular/core").InputSignal<NeuTagTone>` |
| variant | no | `import("@angular/core").InputSignal<NeuTagVariant>` |
| value | no | `import("@angular/core").InputSignal<string \| number \| null \| undefined>` |
| icon | no | `import("@angular/core").InputSignal<string \| null>` |
| rounded | no | `import("@angular/core").InputSignal<boolean>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTagIconDirective

Selector: `ng-template[neuTagIcon]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTagTone

```typescript
export type NeuTagTone = 'neutral' | 'success' | 'info' | 'warning' | 'danger';
```

## NeuTagVariant

```typescript
export type NeuTagVariant = 'soft' | 'solid';
```

