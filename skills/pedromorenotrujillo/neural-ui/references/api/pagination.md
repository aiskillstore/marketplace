# @neural-ui/core/pagination

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuPaginationComponent

Selector: `neu-pagination`

| Input | Required | Type |
| --- | --- | --- |
| page | no | `import("@angular/core").InputSignal<number>` |
| total | no | `import("@angular/core").InputSignal<number>` |
| pageSize | no | `import("@angular/core").InputSignal<number>` |
| pageSizeOptions | no | `import("@angular/core").InputSignal<readonly number[]>` |
| pageSizeAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| maxVisible | no | `import("@angular/core").InputSignal<number>` |

| Output | Type |
| --- | --- |
| pageChange | `import("@angular/core").OutputEmitterRef<number>` |
| pageSizeChange | `import("@angular/core").OutputEmitterRef<number>` |

## NeuPaginationLocaleLabels

```typescript
interface NeuPaginationLocaleLabels {
    readonly pagination: string;
    readonly itemsPerPage: string;
    readonly previousPage: string;
    readonly nextPage: string;
    readonly page: (page: number) => string;
}
```

