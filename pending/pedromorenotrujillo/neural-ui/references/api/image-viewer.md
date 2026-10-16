# @neural-ui/core/image-viewer

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuImageViewerDirective

Selector: `[neuImageViewer]`

| Input | Required | Type |
| --- | --- | --- |
| neuImageViewer | no | `import("@angular/core").InputSignal<string \| NeuImageViewerItem \| readonly NeuImageViewerItem[]>` |
| neuIvIndex | no | `import("@angular/core").InputSignal<number>` |

| Output | Type |
| --- | --- |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |

Supported imperative members:

```typescript
open(): void;
close(): void;
```

## NeuImageViewerItem

```typescript
interface NeuImageViewerItem {
    src: string;
    alt: string;
    caption?: string;
}
```

