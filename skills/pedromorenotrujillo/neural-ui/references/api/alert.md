# @neural-ui/core/alert

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuAlertComponent

Selector: `neu-alert`

| Input | Required | Type |
| --- | --- | --- |
| tone | no | `import("@angular/core").InputSignal<NeuAlertTone>` |
| title | no | `import("@angular/core").InputSignal<string>` |
| icon | no | `import("@angular/core").InputSignal<string \| null>` |
| showIcon | no | `import("@angular/core").InputSignal<boolean>` |
| closable | no | `import("@angular/core").InputSignal<boolean>` |
| variant | no | `import("@angular/core").InputSignal<NeuAlertVariant>` |
| closeLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| closed | `import("@angular/core").OutputEmitterRef<void>` |

## NeuAlertTone

```typescript
export type NeuAlertTone = 'neutral' | 'success' | 'info' | 'warning' | 'danger';
```

## NeuAlertVariant

```typescript
export type NeuAlertVariant = 'soft' | 'outline';
```

