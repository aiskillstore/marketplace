# @neural-ui/core/input

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuInputComponent

Selector: `neu-input`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<string>` |
| type | no | `import("@angular/core").InputSignal<NeuInputType>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| floatingLabel | no | `import("@angular/core").InputSignal<boolean>` |
| size | no | `import("@angular/core").InputSignal<"sm" \| "md" \| "lg">` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| errorMessage | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| autocomplete | no | `import("@angular/core").InputSignal<string>` |
| startIcon | no | `import("@angular/core").InputSignal<boolean>` |
| endIcon | no | `import("@angular/core").InputSignal<boolean>` |
| icon | no | `import("@angular/core").InputSignal<string \| null>` |
| iconPosition | no | `import("@angular/core").InputSignal<"left" \| "right">` |
| inputId | no | `import("@angular/core").InputSignal<string>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| maxLength | no | `import("@angular/core").InputSignal<number \| undefined>` |
| minLength | no | `import("@angular/core").InputSignal<number \| undefined>` |
| min | no | `import("@angular/core").InputSignal<string \| undefined>` |
| max | no | `import("@angular/core").InputSignal<string \| undefined>` |
| pattern | no | `import("@angular/core").InputSignal<readonly RegExp[]>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<string>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

## NeuInputType

```typescript
export type NeuInputType = 'text' | 'email' | 'password' | 'tel' | 'url' | 'search';
```

