# @neural-ui/core/number-input

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuNumberInputComponent

Selector: `neu-number-input`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<number \| null>` |
| min | no | `import("@angular/core").InputSignal<number \| undefined>` |
| max | no | `import("@angular/core").InputSignal<number \| undefined>` |
| step | no | `import("@angular/core").InputSignal<number>` |
| formatOptions | no | `import("@angular/core").InputSignal<NeuNumberInputFormatOptions>` |
| layout | no | `import("@angular/core").InputSignal<NeuNumberInputLayout>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string>` |
| decrementLabel | no | `import("@angular/core").InputSignal<string>` |
| incrementLabel | no | `import("@angular/core").InputSignal<string>` |
| floatingLabel | no | `import("@angular/core").InputSignal<boolean>` |
| size | no | `import("@angular/core").InputSignal<"sm" \| "md" \| "lg">` |
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
| inputDetail | `import("@angular/core").OutputEmitterRef<NeuNumberInputDetail>` |

## NeuNumberInputDetail

```typescript
export interface NeuNumberInputDetail {
    readonly rawText: string;
    readonly value: number | null;
    readonly state: NeuNumberInputState;
}
```

## NeuNumberInputFormatBase

```typescript
interface NeuNumberInputFormatBase {
    readonly locale: string;
    readonly minimumFractionDigits?: number;
    readonly maximumFractionDigits?: number;
    readonly useGrouping?: boolean;
}
```

## NeuNumberInputFormatOptions

```typescript
export type NeuNumberInputFormatOptions = (NeuNumberInputFormatBase & {
    readonly style?: 'decimal';
    readonly currency?: never;
}) | (NeuNumberInputFormatBase & {
    readonly style: 'currency';
    readonly currency: string;
});
```

## NeuNumberInputLayout

```typescript
export type NeuNumberInputLayout = 'horizontal' | 'stacked' | 'vertical';
```

## NeuNumberInputState

```typescript
export type NeuNumberInputState = 'valid' | 'incomplete' | 'invalid';
```

