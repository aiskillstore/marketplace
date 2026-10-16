# @neural-ui/core/dashboard-grid

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuDashboardGridComponent

Selector: `neu-dashboard-grid`

| Input | Required | Type |
| --- | --- | --- |
| tiles | no | `import("@angular/core").InputSignal<readonly NeuDashboardTileConfig[]>` |
| columns | no | `import("@angular/core").InputSignal<number>` |

| Output | Type |
| --- | --- |
| orderChange | `import("@angular/core").OutputEmitterRef<readonly NeuDashboardTileConfig[]>` |

## NeuDashboardTileConfig

```typescript
export interface NeuDashboardTileConfig {
    id: string;
    cols?: number;
    rows?: number;
    title?: string;
}
```

