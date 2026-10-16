# @neural-ui/core/calendar

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## CalendarDayCell

```typescript
interface CalendarDayCell {
    date: Date;
    inCurrentMonth: boolean;
    isToday: boolean;
    isSelected: boolean;
    events: NormalizedCalendarEvent[];
}
```

## NeuCalendarComponent

Selector: `neu-calendar`

| Input | Required | Type |
| --- | --- | --- |
| events | no | `import("@angular/core").InputSignal<NeuCalendarEvent[]>` |
| view | no | `import("@angular/core").InputSignal<NeuCalendarView>` |
| selectedDate | no | `import("@angular/core").InputSignal<string \| Date>` |
| locale | no | `import("@angular/core").InputSignal<string>` |
| maxVisibleEvents | no | `import("@angular/core").InputSignal<number>` |
| showHeader | no | `import("@angular/core").InputSignal<boolean>` |
| labels | no | `import("@angular/core").InputSignal<Partial<NeuCalendarLabels>>` |
| firstDayOfWeek | no | `import("@angular/core").InputSignal<number>` |

| Output | Type |
| --- | --- |
| selectedDateChange | `import("@angular/core").OutputEmitterRef<Date>` |
| eventClick | `import("@angular/core").OutputEmitterRef<NeuCalendarEvent>` |

## NeuCalendarEvent

```typescript
export interface NeuCalendarEvent {
    id: string;
    title: string;
    start: string | Date;
    end?: string | Date;
    description?: string;
    meta?: string;
    allDay?: boolean;
    tone?: NeuCalendarEventTone;
}
```

## NeuCalendarEventContext

```typescript
export interface NeuCalendarEventContext {
    readonly $implicit: NeuCalendarEvent;
    readonly view: NeuCalendarEventView;
}
```

## NeuCalendarEventDirective

Selector: `ng-template[neuCalendarEvent]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuCalendarEventTone

```typescript
export type NeuCalendarEventTone = 'neutral' | 'brand' | 'success' | 'info' | 'warning' | 'danger';
```

## NeuCalendarEventView

```typescript
export type NeuCalendarEventView = 'month' | 'week' | 'agenda';
```

## NeuCalendarLabelOverrides

```typescript
export type NeuCalendarLabelOverrides = Partial<NeuCalendarLabels>;
```

## NeuCalendarLabels

```typescript
export interface NeuCalendarLabels {
    previousButtonAriaLabel: string;
    nextButtonAriaLabel: string;
    todayButton: string;
    allDay: string;
    noEvents: string;
    eventCount: (count: number) => string;
    moreEvents: (count: number) => string;
}
```

## NeuCalendarView

```typescript
export type NeuCalendarView = 'month' | 'week';
```

## NormalizedCalendarEvent

```typescript
interface NormalizedCalendarEvent extends Omit<NeuCalendarEvent, "start" | "end"> {
    start: Date;
    end?: Date;
}
```

