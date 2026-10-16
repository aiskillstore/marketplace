# @neural-ui/core/rich-text-editor

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuRichTextEditorCommand

```typescript
type NeuRichTextEditorCommand = 'bold' | 'italic' | 'underline' | 'insertUnorderedList' | 'insertOrderedList' | 'removeFormat';
```

## NeuRichTextEditorComponent

Selector: `neu-rich-text-editor`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<string>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| errorMessage | no | `import("@angular/core").InputSignal<string>` |
| size | no | `import("@angular/core").InputSignal<NeuRichTextEditorSize>` |
| minHeight | no | `import("@angular/core").InputSignal<string>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| labels | no | `import("@angular/core").InputSignal<Partial<NeuRichTextEditorLabels>>` |
| variables | no | `import("@angular/core").InputSignal<readonly string[]>` |
| variablesLabel | no | `import("@angular/core").InputSignal<string>` |
| variablesAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| maxPastedImageBytes | no | `import("@angular/core").InputSignal<number>` |
| showPreview | no | `import("@angular/core").InputSignal<boolean>` |
| previewLabel | no | `import("@angular/core").InputSignal<string>` |
| editorId | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<string>` |
| imageRejected | `import("@angular/core").OutputEmitterRef<NeuRichTextImageRejectedEvent>` |
| valueCommitted | `import("@angular/core").OutputEmitterRef<string>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

## NeuRichTextEditorLabels

```typescript
interface NeuRichTextEditorLabels {
    toolbar: string;
    formatGroup: string;
    listsGroup: string;
    insertGroup: string;
    clearGroup: string;
    bold: string;
    italic: string;
    underline: string;
    unorderedList: string;
    orderedList: string;
    addLink: string;
    addImageUrl: string;
    clearFormat: string;
    linkUrlPrompt: string;
    linkTextPrompt: string;
    imageUrlPrompt: string;
    imageAltPrompt: string;
    imageAltFallback: string;
    pastedImageAlt: string;
}
```

## NeuRichTextEditorSize

```typescript
type NeuRichTextEditorSize = 'sm' | 'md' | 'lg';
```

## NeuRichTextImageRejectedEvent

```typescript
interface NeuRichTextImageRejectedEvent {
    file: File;
    maxBytes: number;
    reason: "size";
}
```

