# @neural-ui/core/timeline-grid

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuTimelineGridColumn

```typescript
export interface NeuTimelineGridColumn {
    id: string;
    label: string;
    description?: string;
}
```

## NeuTimelineGridComponent

Selector: `neu-timeline-grid`

| Input | Required | Type |
| --- | --- | --- |
| columns | no | `import("@angular/core").InputSignal<readonly NeuTimelineGridColumn[]>` |
| rows | no | `import("@angular/core").InputSignal<readonly NeuTimelineGridRow[]>` |
| density | no | `import("@angular/core").InputSignal<NeuDensity>` |
| stickyLabels | no | `import("@angular/core").InputSignal<boolean>` |
| minColumnWidth | no | `import("@angular/core").InputSignal<string>` |
| selectedItemId | no | `import("@angular/core").InputSignal<string \| null>` |
| selectedSlot | no | `import("@angular/core").InputSignal<NeuTimelineGridSlotSelection \| null>` |

| Output | Type |
| --- | --- |
| itemClick | `import("@angular/core").OutputEmitterRef<NeuTimelineGridItem>` |
| slotClick | `import("@angular/core").OutputEmitterRef<NeuTimelineGridSlotSelection>` |

## NeuTimelineGridItem

```typescript
export interface NeuTimelineGridItem {
    id: string;
    title: string;
    start: string;
    span?: number;
    subtitle?: string;
    meta?: string;
    tone?: NeuTimelineGridItemTone;
}
```

## NeuTimelineGridItemTone

```typescript
export type NeuTimelineGridItemTone = 'neutral' | 'success' | 'warning' | 'danger' | 'info';
```

## NeuTimelineGridRow

```typescript
export interface NeuTimelineGridRow {
    id: string;
    label: string;
    description?: string;
    items: readonly NeuTimelineGridItem[];
}
```

## NeuTimelineGridSlotSelection

```typescript
export interface NeuTimelineGridSlotSelection {
    rowId: string;
    columnId: string;
}
```

