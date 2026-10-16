# @neural-ui/core/rating

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuRatingComponent

Selector: `neu-rating`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<number \| null>` |
| stars | no | `import("@angular/core").InputSignal<number>` |
| step | no | `import("@angular/core").InputSignal<1 \| 0.5>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string>` |
| inputId | no | `import("@angular/core").InputSignal<string>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<number \| null>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

