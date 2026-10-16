# @neural-ui/core/input-mask

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuInputMaskComponent

Selector: `neu-input-mask`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<string>` |
| mask | no | `import("@angular/core").InputSignal<string>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
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
| required | no | `import("@angular/core").InputSignal<boolean>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| minLength | no | `import("@angular/core").InputSignal<number \| undefined>` |
| maxLength | no | `import("@angular/core").InputSignal<number \| undefined>` |
| pattern | no | `import("@angular/core").InputSignal<readonly RegExp[]>` |
| inputId | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<string>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

