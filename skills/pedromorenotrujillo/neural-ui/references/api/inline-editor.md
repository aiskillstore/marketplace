# @neural-ui/core/inline-editor

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuInlineEditorCommitEvent

```typescript
export interface NeuInlineEditorCommitEvent<M extends NeuInlineMode = NeuInlineMode> {
    readonly previousValue: NeuInlineValue<M>;
    readonly value: NeuInlineValue<M>;
}
```

## NeuInlineEditorComponent

```typescript
export type NeuInlineEditorComponent<M extends NeuInlineMode = 'text'> = NeuInlineEditorControl<NeuInlineValue<M>>;
```

## NeuInlineEditorControl

Selector: `neu-inline-editor`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<V>` |
| type | no | `import("@angular/core").InputSignal<NeuInlineEditorType>` |
| options | no | `import("@angular/core").InputSignal<readonly unknown[]>` |
| size | no | `import("@angular/core").InputSignal<NeuInlineEditorSize>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |
| editLabel | no | `import("@angular/core").InputSignal<string>` |
| saveLabel | no | `import("@angular/core").InputSignal<string>` |
| cancelLabel | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| ariaDescribedBy | no | `import("@angular/core").InputSignal<string>` |
| startInEdit | no | `import("@angular/core").InputSignal<boolean>` |
| saveOnBlur | no | `import("@angular/core").InputSignal<boolean>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<V>` |
| editStart | `import("@angular/core").OutputEmitterRef<V>` |
| editCancel | `import("@angular/core").OutputEmitterRef<V>` |
| valueCommitted | `import("@angular/core").OutputEmitterRef<NeuInlineEditorValueCommitEvent<V>>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

## NeuInlineEditorSize

```typescript
export type NeuInlineEditorSize = 'sm' | 'md' | 'lg';
```

## NeuInlineEditorType

```typescript
export type NeuInlineEditorType = NeuInlineMode | 'select' | 'textarea' | 'date';
```

## NeuInlineEditorValueCommitEvent

```typescript
interface NeuInlineEditorValueCommitEvent<V> {
    readonly previousValue: V;
    readonly value: V;
}
```

## NeuInlineMode

```typescript
export type NeuInlineMode = 'text' | 'number';
```

## NeuInlineValue

```typescript
export type NeuInlineValue<M extends NeuInlineMode> = M extends 'number' ? number | null : string;
```

