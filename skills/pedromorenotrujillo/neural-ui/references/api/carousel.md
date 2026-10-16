# @neural-ui/core/carousel

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuCarouselComponent

Selector: `neu-carousel`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<readonly T[]>` |
| page | no | `import("@angular/core").InputSignal<number \| null>` |
| initialPage | no | `import("@angular/core").InputSignal<number>` |
| numVisible | no | `import("@angular/core").InputSignal<number>` |
| numScroll | no | `import("@angular/core").InputSignal<number>` |
| responsiveOptions | no | `import("@angular/core").InputSignal<readonly NeuCarouselResponsiveOption[]>` |
| circular | no | `import("@angular/core").InputSignal<boolean>` |
| autoplayInterval | no | `import("@angular/core").InputSignal<number>` |
| showIndicators | no | `import("@angular/core").InputSignal<boolean>` |
| showNavigators | no | `import("@angular/core").InputSignal<boolean>` |
| orientation | no | `import("@angular/core").InputSignal<"horizontal" \| "vertical">` |
| verticalViewPortHeight | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| indicatorLabel | no | `import("@angular/core").InputSignal<string>` |
| previousLabel | no | `import("@angular/core").InputSignal<string>` |
| nextLabel | no | `import("@angular/core").InputSignal<string>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |
| trackBy | no | `import("@angular/core").InputSignal<(index: number, item: T) => unknown>` |

| Output | Type |
| --- | --- |
| pageChange | `import("@angular/core").OutputEmitterRef<NeuCarouselPageEvent>` |

## NeuCarouselFooterDirective

Selector: `ng-template[neuCarouselFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCarouselHeaderDirective

Selector: `ng-template[neuCarouselHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCarouselItemContext

```typescript
export interface NeuCarouselItemContext<T> {
    $implicit: T;
    index: number;
}
```

## NeuCarouselItemDirective

Selector: `ng-template[neuCarouselItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCarouselPageEvent

```typescript
export interface NeuCarouselPageEvent {
    page: number;
    first: number;
}
```

## NeuCarouselResponsiveOption

```typescript
export interface NeuCarouselResponsiveOption {
    breakpoint: string | number;
    numVisible: number;
    numScroll?: number;
}
```

