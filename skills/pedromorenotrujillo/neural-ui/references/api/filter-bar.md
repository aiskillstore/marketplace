# @neural-ui/core/filter-bar

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuFilterBarComponent

Selector: `neu-filter-bar`

| Input | Required | Type |
| --- | --- | --- |
| filters | no | `import("@angular/core").InputSignal<readonly NeuFilterChip[]>` |
| clearable | no | `import("@angular/core").InputSignal<boolean>` |
| clearLabel | no | `import("@angular/core").InputSignal<string>` |
| multi | no | `import("@angular/core").InputSignal<boolean>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| filterChange | `import("@angular/core").OutputEmitterRef<NeuFilterChip[]>` |

## NeuFilterChip

```typescript
export interface NeuFilterChip {
    key: string;
    label: string;
    active?: boolean;
}
```

