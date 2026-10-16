# @neural-ui/core/gallery

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuGalleryCaptionContext

```typescript
export interface NeuGalleryCaptionContext {
    $implicit: NeuGalleryItem;
    index: number;
}
```

## NeuGalleryCaptionDirective

Selector: `ng-template[neuGalleryCaption]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuGalleryComponent

Selector: `neu-gallery`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<readonly NeuImageViewerItem[]>` |
| activeIndex | no | `import("@angular/core").InputSignal<number \| null>` |
| initialIndex | no | `import("@angular/core").InputSignal<number>` |
| circular | no | `import("@angular/core").InputSignal<boolean>` |
| showThumbnails | no | `import("@angular/core").InputSignal<boolean>` |
| thumbnailPosition | no | `import("@angular/core").InputSignal<"bottom" \| "start">` |
| showItemNavigators | no | `import("@angular/core").InputSignal<boolean>` |
| showCounter | no | `import("@angular/core").InputSignal<boolean>` |
| previewEnabled | no | `import("@angular/core").InputSignal<boolean>` |
| objectFit | no | `import("@angular/core").InputSignal<"cover" \| "contain">` |
| imageLoading | no | `import("@angular/core").InputSignal<"eager" \| "lazy">` |
| maxZoom | no | `import("@angular/core").InputSignal<number>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| thumbnailLabel | no | `import("@angular/core").InputSignal<string>` |
| previewLabel | no | `import("@angular/core").InputSignal<string>` |
| toolbarLabel | no | `import("@angular/core").InputSignal<string>` |
| zoomOutLabel | no | `import("@angular/core").InputSignal<string>` |
| zoomInLabel | no | `import("@angular/core").InputSignal<string>` |
| rotateLeftLabel | no | `import("@angular/core").InputSignal<string>` |
| rotateRightLabel | no | `import("@angular/core").InputSignal<string>` |
| flipHorizontalLabel | no | `import("@angular/core").InputSignal<string>` |
| flipVerticalLabel | no | `import("@angular/core").InputSignal<string>` |
| resetLabel | no | `import("@angular/core").InputSignal<string>` |
| previousLabel | no | `import("@angular/core").InputSignal<string>` |
| nextLabel | no | `import("@angular/core").InputSignal<string>` |
| closeLabel | no | `import("@angular/core").InputSignal<string>` |
| downloadLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| activeIndexChange | `import("@angular/core").OutputEmitterRef<number>` |
| previewChange | `import("@angular/core").OutputEmitterRef<boolean>` |
| zoomChange | `import("@angular/core").OutputEmitterRef<number>` |
| rotationChange | `import("@angular/core").OutputEmitterRef<number>` |
| flipChange | `import("@angular/core").OutputEmitterRef<{
    x: number;
    y: number;
}>` |
| imageError | `import("@angular/core").OutputEmitterRef<{
    item: NeuGalleryItem;
    index: number;
}>` |

## NeuGalleryItem

```typescript
export type NeuGalleryItem = NeuImageViewerItem;
```

## NeuGalleryItemContext

```typescript
export interface NeuGalleryItemContext {
    $implicit: NeuGalleryItem;
    index: number;
    active: boolean;
}
```

## NeuGalleryItemDirective

Selector: `ng-template[neuGalleryItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

