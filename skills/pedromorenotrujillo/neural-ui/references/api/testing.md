# @neural-ui/core/testing

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## captureNeuHydrationSnapshot

```typescript
export declare function captureNeuHydrationSnapshot(root: ParentNode): NeuHydrationSnapshot;
```

## collectCvaChanges

```typescript
export declare function collectCvaChanges<T>(component: NeuCvaLike<T>): T[];
```

## collectCvaTouches

```typescript
export declare function collectCvaTouches(component: NeuCvaLike<unknown>): boolean[];
```

## compareNeuHydrationSnapshots

```typescript
export declare function compareNeuHydrationSnapshots(server: NeuHydrationSnapshot, client: NeuHydrationSnapshot): string[];
```

## detectStableChanges

```typescript
export declare function detectStableChanges<T>(fixture: ComponentFixture<T>): Promise<void>;
```

## dispatchKeyboard

```typescript
export declare function dispatchKeyboard(target: EventTarget, key: string): KeyboardEvent;
```

## isNeuHydrationError

```typescript
export declare function isNeuHydrationError(message: unknown): boolean;
```

## NeuButtonHarness

Supported imperative members:

```typescript
static hostSelector: string;
static with(options?: NeuTextHarnessFilters): HarnessPredicate<NeuButtonHarness>;
getText(): Promise<string>;
isDisabled(): Promise<boolean>;
isLoading(): Promise<boolean>;
click(): Promise<void>;
focus(): Promise<void>;
```

## NeuCheckboxHarness

Supported imperative members:

```typescript
static hostSelector: string;
isChecked(): Promise<boolean>;
isDisabled(): Promise<boolean>;
toggle(): Promise<void>;
getLabel(): Promise<string>;
```

## NeuCvaLike

```typescript
export interface NeuCvaLike<T> {
    writeValue(value: T | null | undefined): void;
    registerOnChange(fn: (value: T) => void): void;
    registerOnTouched(fn: () => void): void;
    setDisabledState(isDisabled: boolean): void;
}
```

## NeuDateInputHarness

Supported imperative members:

```typescript
static hostSelector: string;
open(): Promise<void>;
close(): Promise<void>;
isOpen(): Promise<boolean>;
getDisplayValue(): Promise<string>;
selectDay(day: number): Promise<void>;
```

## NeuDialogHarness

Supported imperative members:

```typescript
static hostSelector: string;
isOpen(): Promise<boolean>;
getTitle(): Promise<string | null>;
getBodyText(): Promise<string | null>;
close(): Promise<void>;
```

## NeuHydrationElementSnapshot

```typescript
export interface NeuHydrationElementSnapshot {
    readonly path: string;
    readonly tag: string;
    readonly id: string | null;
    readonly htmlFor: string | null;
    readonly ariaControls: string | null;
    readonly ariaDescribedBy: string | null;
    readonly ariaLabelledBy: string | null;
    readonly ariaActiveDescendant: string | null;
}
```

## NeuHydrationSnapshot

```typescript
export interface NeuHydrationSnapshot {
    readonly elements: readonly NeuHydrationElementSnapshot[];
}
```

## NeuInputHarness

Supported imperative members:

```typescript
static hostSelector: string;
getValue(): Promise<string>;
setValue(value: string): Promise<void>;
getLabel(): Promise<string | null>;
getError(): Promise<string | null>;
isDisabled(): Promise<boolean>;
focus(): Promise<void>;
blur(): Promise<void>;
```

## NeuSelectHarness

Supported imperative members:

```typescript
static hostSelector: string;
open(): Promise<void>;
close(): Promise<void>;
isOpen(): Promise<boolean>;
getValueText(): Promise<string>;
getOptions(): Promise<string[]>;
selectOption(text: string | RegExp): Promise<void>;
```

## NeuSwitchHarness

Supported imperative members:

```typescript
static hostSelector: string;
isChecked(): Promise<boolean>;
isDisabled(): Promise<boolean>;
toggle(): Promise<void>;
getLabel(): Promise<string>;
```

## NeuTableHarness

Supported imperative members:

```typescript
static hostSelector: string;
getRowCount(): Promise<number>;
getHeaderTexts(): Promise<string[]>;
getCellText(row: number, column: number): Promise<string>;
```

## NeuTextHarnessFilters

```typescript
export interface NeuTextHarnessFilters extends BaseHarnessFilters {
    text?: string | RegExp;
}
```

