# @neural-ui/core/radio

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NEU_RADIO_GROUP

```typescript
NEU_RADIO_GROUP: InjectionToken<object>
```

## NeuRadioComponent

Selector: `neu-radio`

| Input | Required | Type |
| --- | --- | --- |
| value | yes | `import("@angular/core").InputSignal<V>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| inputId | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuRadioGroupComponent

Selector: `neu-radio-group`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<V \| null>` |
| direction | no | `import("@angular/core").InputSignal<"row" \| "column">` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
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
| compareWith | no | `import("@angular/core").InputSignal<(left: V, right: V) => boolean>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<V \| null>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

