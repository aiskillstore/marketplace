# @neural-ui/core/key-filter

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuKeyFilterDirective

Selector: `[neuKeyFilter]`

| Input | Required | Type |
| --- | --- | --- |
| neuKeyFilter | no | `import("@angular/core").InputSignal<NeuKeyFilterValue>` |
| neuKeyFilterValidateOnly | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |

| Output | Type |
| --- | --- |

## NeuKeyFilterPattern

```typescript
export type NeuKeyFilterPattern = 'pint' | 'int' | 'pnum' | 'money' | 'num' | 'hex' | 'email' | 'alpha' | 'alphanum';
```

## NeuKeyFilterValue

```typescript
export type NeuKeyFilterValue = NeuKeyFilterPattern | RegExp | null | undefined;
```

