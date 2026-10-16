# @neural-ui/core/speed-dial

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuSpeedDialAnimationConfig

```typescript
export interface NeuSpeedDialAnimationConfig {
    readonly itemDelay?: number;
    readonly rotateTrigger?: boolean;
}
```

## NeuSpeedDialComponent

Selector: `neu-speed-dial`

| Input | Required | Type |
| --- | --- | --- |
| id | no | `import("@angular/core").InputSignal<string \| undefined>` |
| items | no | `import("@angular/core").InputSignal<readonly NeuSpeedDialItem[]>` |
| open | no | `import("@angular/core").InputSignal<boolean \| null>` |
| direction | no | `import("@angular/core").InputSignal<NeuSpeedDialDirection>` |
| type | no | `import("@angular/core").InputSignal<NeuSpeedDialType>` |
| radius | no | `import("@angular/core").InputSignalWithTransform<number, unknown>` |
| mask | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| disabled | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| hideOnClickOutside | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| animation | no | `import("@angular/core").InputSignal<Readonly<NeuSpeedDialAnimationConfig>>` |
| tooltip | no | `import("@angular/core").InputSignal<Readonly<NeuSpeedDialTooltipConfig> \| null>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string \| null>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string \| null>` |
| tabindex | no | `import("@angular/core").InputSignalWithTransform<number, unknown>` |

| Output | Type |
| --- | --- |
| openChange | `import("@angular/core").OutputEmitterRef<boolean>` |
| triggerClick | `import("@angular/core").OutputEmitterRef<MouseEvent>` |
| itemActivate | `import("@angular/core").OutputEmitterRef<NeuSpeedDialItemEvent>` |
| opened | `import("@angular/core").OutputEmitterRef<NeuSpeedDialVisibilityEvent>` |
| closed | `import("@angular/core").OutputEmitterRef<NeuSpeedDialVisibilityEvent>` |

Supported imperative members:

```typescript
open(): void;
close(): void;
toggle(): void;
```

## NeuSpeedDialDirection

```typescript
export type NeuSpeedDialDirection = 'up' | 'down' | 'left' | 'right' | 'up-left' | 'up-right' | 'down-left' | 'down-right';
```

## NeuSpeedDialItem

```typescript
export interface NeuSpeedDialItem extends NeuMenuActionLike<NeuSpeedDialItem> {
    key: string;
    label: string;
    data?: unknown;
}
```

## NeuSpeedDialItemDirective

Selector: `ng-template[neuSpeedDialItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSpeedDialItemEvent

```typescript
export interface NeuSpeedDialItemEvent {
    readonly originalEvent: Event;
    readonly item: NeuSpeedDialItem;
}
```

## NeuSpeedDialItemTemplateContext

```typescript
export interface NeuSpeedDialItemTemplateContext {
    readonly $implicit: NeuSpeedDialItem;
    readonly index: number;
    readonly active: boolean;
    readonly disabled: boolean;
    readonly open: boolean;
}
```

## NeuSpeedDialTooltipConfig

```typescript
export interface NeuSpeedDialTooltipConfig {
    readonly position?: NeuTooltipPosition;
}
```

## NeuSpeedDialTriggerDirective

Selector: `ng-template[neuSpeedDialTrigger]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuSpeedDialTriggerTemplateContext

```typescript
export interface NeuSpeedDialTriggerTemplateContext {
    readonly $implicit: boolean;
    readonly open: boolean;
}
```

## NeuSpeedDialType

```typescript
export type NeuSpeedDialType = 'linear' | 'circle' | 'semi-circle' | 'quarter-circle';
```

## NeuSpeedDialVisibilityEvent

```typescript
export interface NeuSpeedDialVisibilityEvent {
    readonly originalEvent: Event | null;
    readonly reason: NeuSpeedDialVisibilityReason;
}
```

## NeuSpeedDialVisibilityReason

```typescript
export type NeuSpeedDialVisibilityReason = 'trigger' | 'item' | 'escape' | 'outside' | 'mask' | 'disabled' | 'programmatic';
```

