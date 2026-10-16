# @neural-ui/core/form-field

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuFormFieldComponent

Selector: `neu-form-field`

| Input | Required | Type |
| --- | --- | --- |
| label | no | `import("@angular/core").InputSignal<string>` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| error | no | `import("@angular/core").InputSignal<string>` |
| prefix | no | `import("@angular/core").InputSignal<string>` |
| suffix | no | `import("@angular/core").InputSignal<string>` |
| forId | no | `import("@angular/core").InputSignal<string>` |
| id | no | `import("@angular/core").InputSignal<string>` |
| size | no | `import("@angular/core").InputSignal<NeuFormFieldSize>` |

| Output | Type |
| --- | --- |

Supported imperative members:

```typescript
mergeDescribedBy(...ids: Array<string | null | undefined>): string;
```

## NeuFormFieldSize

```typescript
export type NeuFormFieldSize = 'sm' | 'md' | 'lg';
```

## NeuInputGroupComponent

Selector: `neu-input-group`

| Input | Required | Type |
| --- | --- | --- |
| size | no | `import("@angular/core").InputSignal<NeuFormFieldSize>` |
| attached | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |

