# @neural-ui/core/drag-drop

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuDragDropGroupDirective

Selector: `[neuDragDropGroup]`

| Input | Required | Type |
| --- | --- | --- |
| neuDragDropGroupDisabled | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |

| Output | Type |
| --- | --- |

## NeuDragEffect

```typescript
export type NeuDragEffect = 'copy' | 'move' | 'link' | 'none';
```

## NeuDragEndEvent

```typescript
export interface NeuDragEndEvent<T> extends NeuDragEvent<T> {
    readonly distance: Readonly<{
        x: number;
        y: number;
    }>;
    readonly cancelled: boolean;
}
```

## NeuDragEvent

```typescript
export interface NeuDragEvent<T> {
    readonly data: T;
    readonly scope: readonly string[];
    readonly effect: NeuDragEffect;
    readonly interaction: NeuDragInteraction;
    readonly originalEvent: MouseEvent | TouchEvent | KeyboardEvent | null;
}
```

## NeuDraggableDirective

Selector: `[neuDraggable]`

| Input | Required | Type |
| --- | --- | --- |
| neuDraggable | yes | `import("@angular/core").InputSignal<T>` |
| neuDragScope | no | `import("@angular/core").InputSignal<NeuDragScope>` |
| neuDragEffect | no | `import("@angular/core").InputSignal<NeuDragEffect>` |
| neuDraggableDisabled | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| neuDragKeyboard | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| neuDragPointer | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| neuDragAriaLabel | no | `import("@angular/core").InputSignal<string \| null>` |
| neuDragRole | no | `import("@angular/core").InputSignal<string \| null>` |
| neuDragTabIndex | no | `import("@angular/core").InputSignal<number>` |

| Output | Type |
| --- | --- |
| dragStart | `import("@angular/core").OutputEmitterRef<NeuDragEvent<T>>` |
| dragMove | `import("@angular/core").OutputEmitterRef<NeuDragMoveEvent<T>>` |
| dragEnd | `import("@angular/core").OutputEmitterRef<NeuDragEndEvent<T>>` |

## NeuDragHandleDirective

Selector: `[neuDragHandle]`

| Input | Required | Type |
| --- | --- | --- |
| neuDragHandleDisabled | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |

| Output | Type |
| --- | --- |

## NeuDragInteraction

```typescript
export type NeuDragInteraction = 'pointer' | 'keyboard';
```

## NeuDragMoveEvent

```typescript
export interface NeuDragMoveEvent<T> extends NeuDragEvent<T> {
    readonly pointerPosition: Readonly<{
        x: number;
        y: number;
    }>;
    readonly distance: Readonly<{
        x: number;
        y: number;
    }>;
}
```

## NeuDragScope

```typescript
export type NeuDragScope = string | readonly string[];
```

## NeuDropAccept

```typescript
export type NeuDropAccept<T, Z = unknown> = (data: T, targetData: Z) => boolean;
```

## NeuDropEvent

```typescript
export interface NeuDropEvent<T, Z = unknown> extends NeuDragEvent<T> {
    readonly targetData: Z;
    readonly previousIndex?: number;
    readonly currentIndex?: number;
}
```

## NeuDropOrientation

```typescript
export type NeuDropOrientation = 'horizontal' | 'vertical' | 'mixed';
```

## NeuDropZoneDirective

Selector: `[neuDropZone]`

| Input | Required | Type |
| --- | --- | --- |
| neuDropZone | no | `import("@angular/core").InputSignal<Z \| undefined>` |
| neuDropScope | no | `import("@angular/core").InputSignal<NeuDragScope>` |
| neuDropEffect | no | `import("@angular/core").InputSignal<NeuDragEffect>` |
| neuDropZoneDisabled | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| neuDropSortingDisabled | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| neuDropOrientation | no | `import("@angular/core").InputSignal<NeuDropOrientation>` |
| neuDropAccept | no | `import("@angular/core").InputSignal<NeuDropAccept<T, Z> \| null>` |
| neuDropAriaLabel | no | `import("@angular/core").InputSignal<string \| null>` |
| neuDropRole | no | `import("@angular/core").InputSignal<string \| null>` |
| neuDropTabIndex | no | `import("@angular/core").InputSignal<number>` |

| Output | Type |
| --- | --- |
| dragEnter | `import("@angular/core").OutputEmitterRef<NeuDropEvent<T, Z>>` |
| dragLeave | `import("@angular/core").OutputEmitterRef<NeuDropEvent<T, Z>>` |
| drop | `import("@angular/core").OutputEmitterRef<NeuDropEvent<T, Z>>` |

## neuReorder

```typescript
export declare function neuReorder<T>(items: readonly T[], previousIndex: number, currentIndex: number): readonly T[];
```

## neuTransfer

```typescript
export declare function neuTransfer<T>(source: readonly T[], target: readonly T[], previousIndex: number, currentIndex: number): NeuTransferProposal<T> | null;
```

## NeuTransferProposal

```typescript
export interface NeuTransferProposal<T> {
    readonly source: readonly T[];
    readonly target: readonly T[];
    readonly item: T;
}
```

