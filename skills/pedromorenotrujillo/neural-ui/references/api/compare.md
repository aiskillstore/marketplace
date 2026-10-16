# @neural-ui/core/compare

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuCompareComponent

Selector: `neu-compare`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").InputSignal<number \| undefined>` |
| defaultValue | no | `import("@angular/core").InputSignal<number>` |
| orientation | no | `import("@angular/core").InputSignal<NeuCompareOrientation>` |
| min | no | `import("@angular/core").InputSignal<number>` |
| max | no | `import("@angular/core").InputSignal<number>` |
| step | no | `import("@angular/core").InputSignal<number>` |
| slideOnHover | no | `import("@angular/core").InputSignal<boolean>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").OutputEmitterRef<NeuCompareValueChangeEvent>` |
| valueChangeEnd | `import("@angular/core").OutputEmitterRef<NeuCompareValueChangeEvent>` |

## NeuCompareHandleComponent

Selector: `neu-compare-handle`

| Input | Required | Type |
| --- | --- | --- |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaLabelledBy | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuCompareIndicatorComponent

Selector: `neu-compare-indicator`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCompareItemComponent

Selector: `neu-compare-item`

| Input | Required | Type |
| --- | --- | --- |
| position | no | `import("@angular/core").InputSignal<"before" \| "after">` |

| Output | Type |
| --- | --- |

## NeuCompareOrientation

```typescript
type NeuCompareOrientation = 'horizontal' | 'vertical';
```

## NeuCompareValueChangeEvent

```typescript
interface NeuCompareValueChangeEvent {
    originalEvent: Event;
    value: number;
}
```

