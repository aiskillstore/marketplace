# @neural-ui/core/date-input

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## civilDate

```typescript
export declare function civilDate(value: string): CivilDate;
```

## CivilDate

```typescript
export type CivilDate = string & {
    readonly [civilDateBrand]: true;
};
```

## CivilDateRange

```typescript
export interface CivilDateRange {
    readonly start: CivilDate | null;
    readonly end: CivilDate | null;
}
```

## CivilMonth

```typescript
export interface CivilMonth {
    readonly year: number;
    readonly month: number;
}
```

## CivilYear

```typescript
export interface CivilYear {
    readonly year: number;
}
```

## emptyDateValue

```typescript
export declare function emptyDateValue(mode: 'date'): CivilDate | null;
```

## isCivilDate

```typescript
export declare function isCivilDate(value: unknown): value is CivilDate;
```

## isLocalDateTime

```typescript
export declare function isLocalDateTime(value: unknown): value is LocalDateTime;
```

## isLocalTime

```typescript
export declare function isLocalTime(value: unknown): value is LocalTime;
```

## localDateTime

```typescript
export declare function localDateTime(value: string): LocalDateTime;
```

## LocalDateTime

```typescript
export type LocalDateTime = string & {
    readonly [localDateTimeBrand]: true;
};
```

## localTime

```typescript
export declare function localTime(value: string): LocalTime;
```

## LocalTime

```typescript
export type LocalTime = string & {
    readonly [localTimeBrand]: true;
};
```

## NeuDateBoundary

```typescript
export type NeuDateBoundary<M extends NeuDateMode> = M extends 'time' ? LocalTime : M extends 'datetime' ? LocalDateTime : M extends 'month' ? CivilMonth : M extends 'year' ? CivilYear : CivilDate;
```

## NeuDateInputComponent

```typescript
export type NeuDateInputComponent<M extends NeuDateMode = 'date'> = NeuDateInputControl<NeuDateValue<M>>;
```

## NeuDateInputControl

Selector: `neu-date-input`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<V>` |
| mode | no | `import("@angular/core").InputSignal<NeuDateMode>` |
| presentation | no | `import("@angular/core").InputSignal<NeuDatePresentation>` |
| showWeekNumbers | no | `import("@angular/core").InputSignal<boolean>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| errorMessage | no | `import("@angular/core").InputSignal<string>` |
| size | no | `import("@angular/core").InputSignal<"sm" \| "md" \| "lg">` |
| name | no | `import("@angular/core").InputSignal<string>` |
| inputId | no | `import("@angular/core").InputSignal<string>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string>` |
| min | no | `import("@angular/core").InputSignal<NonNullable<V> \| undefined>` |
| max | no | `import("@angular/core").InputSignal<NonNullable<V> \| undefined>` |
| step | no | `import("@angular/core").InputSignal<number>` |
| locale | no | `import("@angular/core").InputSignal<string \| null>` |
| disabledDates | no | `import("@angular/core").InputSignal<readonly CivilDate[] \| ((date: CivilDate) => boolean)>` |
| showMonthYearPicker | no | `import("@angular/core").InputSignal<boolean>` |
| yearRange | no | `import("@angular/core").InputSignal<number>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| dateFormat | no | `import("@angular/core").InputSignal<"short" \| "medium" \| "long" \| "full" \| "numeric">` |
| floatingLabel | no | `import("@angular/core").InputSignal<boolean>` |
| presets | no | `import("@angular/core").InputSignal<readonly NeuDatePreset[]>` |
| firstDayOfWeek | no | `import("@angular/core").InputSignal<number>` |
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
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| cleared | `import("@angular/core").OutputEmitterRef<void>` |
| viewChange | `import("@angular/core").OutputEmitterRef<NeuDateViewChangeEvent>` |

## NeuDateMode

```typescript
export type NeuDateMode = 'date' | 'time' | 'datetime' | 'multiple' | 'range' | 'month' | 'year';
```

## NeuDatePresentation

```typescript
export type NeuDatePresentation = 'overlay' | 'inline';
```

## NeuDatePreset

```typescript
interface NeuDatePreset {
    readonly label: string;
    readonly range: CivilDateRange | (() => CivilDateRange);
}
```

## NeuDateValue

```typescript
export type NeuDateValue<M extends NeuDateMode> = NeuDateValueMap[M];
```

## NeuDateValueMap

```typescript
export interface NeuDateValueMap {
    readonly date: CivilDate | null;
    readonly time: LocalTime | null;
    readonly datetime: LocalDateTime | null;
    readonly multiple: readonly CivilDate[];
    readonly range: CivilDateRange;
    readonly month: CivilMonth | null;
    readonly year: CivilYear | null;
}
```

## NeuDateViewChangeEvent

```typescript
interface NeuDateViewChangeEvent {
    readonly start: CivilDate;
    readonly end: CivilDate;
}
```

