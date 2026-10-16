# @neural-ui/core/stats-card

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuStatsCardComponent

Selector: `neu-stats-card`

| Input | Required | Type |
| --- | --- | --- |
| title | no | `import("@angular/core").InputSignal<string>` |
| value | no | `import("@angular/core").InputSignal<string>` |
| change | no | `import("@angular/core").InputSignal<string>` |
| trend | no | `import("@angular/core").InputSignal<NeuStatsTrend>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| icon | no | `import("@angular/core").InputSignal<string \| null>` |

| Output | Type |
| --- | --- |

## NeuStatsTrend

```typescript
export type NeuStatsTrend = 'up' | 'down' | 'neutral';
```

