# @neural-ui/core/slider

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## isSliderRange

```typescript
declare function isSliderRange(value: SliderValue): value is SliderRange;
```

## NeuSliderComponent

Selector: `neu-slider`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<V>` |
| minValue | no | `import("@angular/core").InputSignal<number>` |
| maxValue | no | `import("@angular/core").InputSignal<number>` |
| step | no | `import("@angular/core").InputSignal<number>` |
| minStepsBetweenThumbs | no | `import("@angular/core").InputSignal<number>` |
| orientation | no | `import("@angular/core").InputSignal<"horizontal" \| "vertical">` |
| label | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string>` |
| showValue | no | `import("@angular/core").InputSignal<boolean>` |
| showTicks | no | `import("@angular/core").InputSignal<boolean>` |
| unit | no | `import("@angular/core").InputSignal<string>` |
| inputId | no | `import("@angular/core").InputSignal<string>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<V>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

## NeuSliderValue

```typescript
export type NeuSliderValue = SliderValue;
```

## sliderClamp

```typescript
declare function sliderClamp(value: number, min: number, max: number): number;
```

## sliderCommitRange

```typescript
declare function sliderCommitRange(current: SliderRange, thumb: SliderThumb, candidate: number, min: number, max: number, step: number, gap: number): SliderRange;
```

## SliderRange

```typescript
type SliderRange = readonly [
    number,
    number
];
```

## sliderSnap

```typescript
declare function sliderSnap(value: number, min: number, step: number): number;
```

## SliderThumb

```typescript
type SliderThumb = 0 | 1;
```

## SliderValue

```typescript
type SliderValue = number | SliderRange;
```

## sliderVisualRange

```typescript
declare function sliderVisualRange(value: SliderRange, min: number, max: number, gap: number): SliderRange;
```

