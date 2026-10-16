# @neural-ui/core/uploader

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuUploaderComponent

Selector: `neu-uploader`

| Input | Required | Type |
| --- | --- | --- |
| value | no | `import("@angular/core").ModelSignal<readonly File[]>` |
| label | no | `import("@angular/core").InputSignal<string>` |
| hint | no | `import("@angular/core").InputSignal<string>` |
| errorMessage | no | `import("@angular/core").InputSignal<string>` |
| placeholder | no | `import("@angular/core").InputSignal<string>` |
| pickerDescription | no | `import("@angular/core").InputSignal<string>` |
| dropzoneLabel | no | `import("@angular/core").InputSignal<string>` |
| chooseLabel | no | `import("@angular/core").InputSignal<string>` |
| clearLabel | no | `import("@angular/core").InputSignal<string>` |
| progressLabel | no | `import("@angular/core").InputSignal<string>` |
| showPickerText | no | `import("@angular/core").InputSignal<boolean>` |
| showProgress | no | `import("@angular/core").InputSignal<boolean>` |
| listAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| removeAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| acceptedTypesLabel | no | `import("@angular/core").InputSignal<string>` |
| maxFileSizeTextLabel | no | `import("@angular/core").InputSignal<string>` |
| fileCountSingularLabel | no | `import("@angular/core").InputSignal<string>` |
| fileCountPluralLabel | no | `import("@angular/core").InputSignal<string>` |
| emptySelectionMessage | no | `import("@angular/core").InputSignal<string>` |
| invalidTypeMessage | no | `import("@angular/core").InputSignal<string>` |
| maxFileSizeMessage | no | `import("@angular/core").InputSignal<string>` |
| duplicateFileMessage | no | `import("@angular/core").InputSignal<string>` |
| maxFilesMessage | no | `import("@angular/core").InputSignal<string>` |
| accept | no | `import("@angular/core").InputSignal<string>` |
| multiple | no | `import("@angular/core").InputSignal<boolean>` |
| dropzone | no | `import("@angular/core").InputSignal<boolean>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| readonly | no | `import("@angular/core").InputSignal<boolean>` |
| hidden | no | `import("@angular/core").InputSignal<boolean>` |
| invalid | no | `import("@angular/core").InputSignal<boolean>` |
| pending | no | `import("@angular/core").InputSignal<boolean>` |
| touched | no | `import("@angular/core").InputSignal<boolean>` |
| dirty | no | `import("@angular/core").InputSignal<boolean>` |
| required | no | `import("@angular/core").InputSignal<boolean>` |
| errors | no | `import("@angular/core").InputSignal<readonly ValidationError.WithOptionalFieldTree[]>` |
| size | no | `import("@angular/core").InputSignal<NeuUploaderSize>` |
| maxFiles | no | `import("@angular/core").InputSignal<number \| null>` |
| maxFileSize | no | `import("@angular/core").InputSignal<number \| null>` |
| progress | no | `import("@angular/core").InputSignal<number \| null>` |
| fileStates | no | `import("@angular/core").InputSignal<Record<string, {
    status?: NeuUploaderFileStatus;
    progress?: number \| null;
    error?: string;
}>>` |
| previewTemplate | no | `import("@angular/core").InputSignal<TemplateRef<{
    $implicit: NeuUploaderFileItem;
    item: NeuUploaderFileItem;
}> \| null>` |
| retryLabel | no | `import("@angular/core").InputSignal<string>` |
| retryAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| inputId | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| valueChange | `import("@angular/core").ModelSignal<readonly File[]>` |
| filesSelected | `import("@angular/core").OutputEmitterRef<readonly File[]>` |
| fileRemoved | `import("@angular/core").OutputEmitterRef<File>` |
| fileRetry | `import("@angular/core").OutputEmitterRef<NeuUploaderFileItem>` |
| filesRejected | `import("@angular/core").OutputEmitterRef<NeuUploaderError[]>` |
| cleared | `import("@angular/core").OutputEmitterRef<void>` |
| touch | `import("@angular/core").OutputEmitterRef<void>` |

## NeuUploaderError

```typescript
export interface NeuUploaderError {
    code: NeuUploaderErrorCode;
    message: string;
    file?: File;
}
```

## NeuUploaderErrorCode

```typescript
export type NeuUploaderErrorCode = 'accept' | 'max-file-size' | 'max-files' | 'duplicate' | 'empty-selection';
```

## NeuUploaderFileItem

```typescript
export interface NeuUploaderFileItem {
    id: string;
    file: File;
    name: string;
    size: number;
    type: string;
    progress: number | null;
    status: NeuUploaderFileStatus;
    error?: string;
}
```

## NeuUploaderFileStatus

```typescript
export type NeuUploaderFileStatus = 'idle' | 'uploading' | 'success' | 'error';
```

## NeuUploaderSize

```typescript
export type NeuUploaderSize = 'sm' | 'md' | 'lg';
```

