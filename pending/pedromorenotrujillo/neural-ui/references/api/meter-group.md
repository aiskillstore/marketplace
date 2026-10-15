# @neural-ui/core/meter-group

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuMeterGroupComponent

Selector: `neu-meter-group`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<NeuMeterItem[]>` |
| total | no | `import("@angular/core").InputSignal<number>` |
| height | no | `import("@angular/core").InputSignal<number>` |
| rounded | no | `import("@angular/core").InputSignal<boolean>` |
| showLegend | no | `import("@angular/core").InputSignal<boolean>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuMeterItem

```typescript
export interface NeuMeterItem {
    label: string;
    value: number;
    color?: string;
}
```

