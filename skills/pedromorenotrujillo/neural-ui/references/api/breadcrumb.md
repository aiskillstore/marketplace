# @neural-ui/core/breadcrumb

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuBreadcrumbComponent

Selector: `neu-breadcrumb`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<NeuBreadcrumbItem[]>` |
| separator | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuBreadcrumbItem

```typescript
export interface NeuBreadcrumbItem {
    label: string;
    route?: string | string[];
    url?: string;
    icon?: NeuIconKey;
}
```

