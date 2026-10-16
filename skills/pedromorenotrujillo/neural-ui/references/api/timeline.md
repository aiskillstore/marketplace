# @neural-ui/core/timeline

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuTimelineAlign

```typescript
export type NeuTimelineAlign = 'left' | 'right' | 'alternate';
```

## NeuTimelineComponent

Selector: `neu-timeline`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<readonly NeuTimelineItem[]>` |
| align | no | `import("@angular/core").InputSignal<NeuTimelineAlign>` |
| density | no | `import("@angular/core").InputSignal<NeuDensity>` |
| reverse | no | `import("@angular/core").InputSignal<boolean>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTimelineItem

```typescript
export interface NeuTimelineItem {
    id?: string | number;
    time?: string;
    title: string;
    description?: string;
    tone?: NeuTimelineItemTone;
    icon?: string;
}
```

## NeuTimelineItemContext

```typescript
export interface NeuTimelineItemContext {
    readonly $implicit: NeuTimelineItem;
    readonly index: number;
}
```

## NeuTimelineItemDirective

Selector: `ng-template[neuTimelineItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTimelineItemTone

```typescript
export type NeuTimelineItemTone = 'neutral' | 'success' | 'warning' | 'danger' | 'info';
```

## NeuTimelineMarkerContext

```typescript
export interface NeuTimelineMarkerContext {
    readonly $implicit: NeuTimelineItem;
}
```

## NeuTimelineMarkerDirective

Selector: `ng-template[neuTimelineMarker]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

