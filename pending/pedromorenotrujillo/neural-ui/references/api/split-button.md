# @neural-ui/core/split-button

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuSplitButtonAction

```typescript
export interface NeuSplitButtonAction {
    id: string;
    label: string;
    icon?: NeuIconKey;
    disabled?: boolean;
    divider?: boolean;
}
```

## NeuSplitButtonComponent

Selector: `neu-split-button`

| Input | Required | Type |
| --- | --- | --- |
| label | no | `import("@angular/core").InputSignal<string>` |
| tone | no | `import("@angular/core").InputSignal<NeuButtonTone>` |
| variant | no | `import("@angular/core").InputSignal<NeuButtonVariant>` |
| size | no | `import("@angular/core").InputSignal<NeuButtonSize>` |
| disabled | no | `import("@angular/core").InputSignal<boolean>` |
| loading | no | `import("@angular/core").InputSignal<boolean>` |
| actions | no | `import("@angular/core").InputSignal<NeuSplitButtonAction[]>` |
| moreActionsAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| actionsAriaLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| opened | `import("@angular/core").OutputEmitterRef<void>` |
| closed | `import("@angular/core").OutputEmitterRef<void>` |
| primaryClick | `import("@angular/core").OutputEmitterRef<MouseEvent>` |
| actionClick | `import("@angular/core").OutputEmitterRef<NeuSplitButtonAction>` |

## NeuSplitButtonItemDirective

Selector: `ng-template[neuSplitButtonItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

