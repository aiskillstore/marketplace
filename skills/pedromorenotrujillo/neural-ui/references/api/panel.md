# @neural-ui/core/panel

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuFieldsetComponent

Selector: `neu-fieldset`

| Input | Required | Type |
| --- | --- | --- |
| legend | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| collapsible | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| collapsed | no | `import("@angular/core").InputSignal<boolean \| undefined>` |

| Output | Type |
| --- | --- |
| collapsedChange | `import("@angular/core").OutputEmitterRef<boolean>` |

## NeuPanelComponent

Selector: `neu-panel`

| Input | Required | Type |
| --- | --- | --- |
| header | no | `import("@angular/core").InputSignal<string>` |
| collapsible | no | `import("@angular/core").InputSignal<boolean>` |
| expandLabel | no | `import("@angular/core").InputSignal<string>` |
| collapseLabel | no | `import("@angular/core").InputSignal<string>` |
| collapsed | no | `import("@angular/core").InputSignal<boolean \| undefined>` |
| initialCollapsed | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| collapsedChange | `import("@angular/core").OutputEmitterRef<boolean>` |

## NeuScrollAreaComponent

Selector: `neu-scroll-area`

| Input | Required | Type |
| --- | --- | --- |
| maxHeight | no | `import("@angular/core").InputSignal<string>` |
| maxWidth | no | `import("@angular/core").InputSignal<string \| null>` |
| enhanced | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| variant | no | `import("@angular/core").InputSignal<NeuScrollAreaVariant>` |
| mask | no | `import("@angular/core").InputSignalWithTransform<boolean, unknown>` |
| tabindex | no | `import("@angular/core").InputSignalWithTransform<number, unknown>` |
| step | no | `import("@angular/core").InputSignal<number>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| scrollPositionChange | `import("@angular/core").OutputEmitterRef<NeuScrollPosition>` |

Supported imperative members:

```typescript
scrollTo(options: ScrollToOptions): void;
```

## NeuScrollAreaVariant

```typescript
export type NeuScrollAreaVariant = 'auto' | 'hover' | 'scroll' | 'always' | 'hidden';
```

## NeuScrollPosition

```typescript
export interface NeuScrollPosition {
    top: number;
    left: number;
    scrollHeight: number;
    scrollWidth: number;
    clientHeight: number;
    clientWidth: number;
}
```

