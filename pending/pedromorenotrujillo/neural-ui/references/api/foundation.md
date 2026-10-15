# @neural-ui/core/foundation

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## allowsNeuOverlayDismissal

```typescript
export declare function allowsNeuOverlayDismissal(guard: NeuOverlayDismissGuard | null, context: NeuOverlayDismissContext): boolean;
```

## defineNeuPreset

```typescript
export declare function defineNeuPreset<const T extends NeuPreset & {
    readonly name: string;
}>(preset: T): T & NeuPresetDefinition;
```

## NEU_ICON_RESOLVER

```typescript
NEU_ICON_RESOLVER: InjectionToken<NeuIconResolver>
```

## NEU_OVERLAY_DISMISS_GUARD

```typescript
NEU_OVERLAY_DISMISS_GUARD: InjectionToken<NeuOverlayDismissGuard>
```

## NeuCloseReason

```typescript
export type NeuCloseReason = 'escape' | 'outside' | 'action' | 'programmatic-command';
```

## NeuCloseRequest

```typescript
export interface NeuCloseRequest {
    readonly reason: NeuCloseReason;
    readonly originalEvent?: Event;
}
```

## NeuIconKey

```typescript
export type NeuIconKey = string;
```

## NeuIconRender

```typescript
export interface NeuIconRender {
    readonly component: Type<unknown>;
    readonly inputs?: Readonly<Record<string, unknown>>;
}
```

## NeuIconRenderContext

```typescript
export interface NeuIconRenderContext {
    readonly key: NeuIconKey;
    readonly size: string | number;
    readonly strokeWidth: number;
    readonly label: string | null;
}
```

## NeuIconResolver

```typescript
export type NeuIconResolver = (context: NeuIconRenderContext) => NeuIconRender | null;
```

## NeuNow

```typescript
export type NeuNow = () => Date;
```

## NeuOverlayDismissContext

```typescript
export interface NeuOverlayDismissContext {
    readonly source: NeuOverlaySource;
    readonly reason: NeuOverlayDismissReason;
    readonly originalEvent: Event | null;
}
```

## NeuOverlayDismissGuard

```typescript
export type NeuOverlayDismissGuard = (context: NeuOverlayDismissContext) => boolean;
```

## NeuOverlayDismissReason

```typescript
export type NeuOverlayDismissReason = 'escape' | 'outside-pointer' | 'backdrop' | 'focus-loss';
```

## NeuOverlaySource

```typescript
export type NeuOverlaySource = 'dialog' | 'popover' | 'menu' | 'context-menu' | 'select' | 'tree-select' | 'cascade-select' | 'color-picker';
```

## NeuPreset

```typescript
interface NeuPreset {
    readonly light?: NeuPresetTokens;
    readonly dark?: NeuPresetTokens;
}
```

## neuPresetCss

```typescript
export declare function neuPresetCss(name: string, preset: NeuPreset): string;
```

## NeuPresetDefinition

```typescript
interface NeuPresetDefinition extends NeuPreset {
    readonly name: string;
}
```

## NeuPresetTokens

```typescript
type NeuPresetTokens = Readonly<Partial<Record<NeuTokenName, string | number>>>;
```

## NEURAL_LOCALE

```typescript
NEURAL_LOCALE: InjectionToken<string>
```

## NEURAL_NOW

```typescript
NEURAL_NOW: InjectionToken<NeuNow>
```

## NEURAL_TIME_ZONE

```typescript
NEURAL_TIME_ZONE: InjectionToken<string | undefined>
```

## NeuTokenName

```typescript
type NeuTokenName = '--neu-accent' | '--neu-alert-danger-bg' | '--neu-alert-danger-border' | '--neu-alert-danger-text' | '--neu-alert-dismiss-hover-bg' | '--neu-alert-error-bg' | '--neu-alert-error-border' | '--neu-alert-error-text' | '--neu-alert-info-bg' | '--neu-alert-info-border' | '--neu-alert-info-text' | '--neu-alert-success-bg' | '--neu-alert-success-border' | '--neu-alert-success-text' | '--neu-alert-warning-bg' | '--neu-alert-warning-border' | '--neu-alert-warning-text' | '--neu-autocomplete-option-height' | '--neu-bg' | '--neu-block-ui-bg' | '--neu-block-ui-radius' | '--neu-border' | '--neu-border-color' | '--neu-border-focus' | '--neu-border-hover' | '--neu-border-subtle' | '--neu-button-background' | '--neu-button-background-hover' | '--neu-button-border' | '--neu-button-foreground' | '--neu-cmd-bg' | '--neu-cmd-highlight' | '--neu-cmd-radius' | '--neu-cmd-shadow' | '--neu-code-block-accent' | '--neu-code-block-bar-bg' | '--neu-code-block-bg' | '--neu-code-block-border' | '--neu-code-block-copy-bg' | '--neu-code-block-copy-border' | '--neu-code-block-copy-hover-bg' | '--neu-code-block-copy-hover-border' | '--neu-code-block-copy-hover-text' | '--neu-code-block-copy-text' | '--neu-code-block-muted' | '--neu-code-block-text' | '--neu-context-menu-bg' | '--neu-context-menu-border' | '--neu-context-menu-color' | '--neu-context-menu-disabled-color' | '--neu-context-menu-hover' | '--neu-context-menu-radius' | '--neu-context-menu-shadow' | '--neu-dialog-body-flex' | '--neu-dialog-body-max-height' | '--neu-dialog-body-padding' | '--neu-dialog-footer-padding' | '--neu-dialog-footer-wrap' | '--neu-dialog-height' | '--neu-dialog-inset' | '--neu-dialog-margin' | '--neu-dialog-max-height' | '--neu-dialog-width-full' | '--neu-dialog-width-lg' | '--neu-dialog-width-md' | '--neu-dialog-width-sm' | '--neu-dialog-width-xl' | '--neu-error' | '--neu-error-bg' | '--neu-error-text' | '--neu-focus-color' | '--neu-focus-ring' | '--neu-focus-ring-alpha' | '--neu-focus-ring-color' | '--neu-focus-ring-offset' | '--neu-focus-ring-strong' | '--neu-focus-ring-strong-alpha' | '--neu-focus-ring-width' | '--neu-font-mono' | '--neu-font-sans' | '--neu-header-height' | '--neu-image-viewer-arrow-bg' | '--neu-image-viewer-arrow-hover' | '--neu-image-viewer-bg' | '--neu-image-viewer-btn-hover' | '--neu-image-viewer-caption' | '--neu-image-viewer-muted' | '--neu-info' | '--neu-info-bg' | '--neu-info-text' | '--neu-input-background' | '--neu-input-border' | '--neu-input-focus-border' | '--neu-input-focus-ring' | '--neu-knob-display-color' | '--neu-knob-label-color' | '--neu-knob-track' | '--neu-meter-radius' | '--neu-meter-track' | '--neu-meter-track-bg' | '--neu-nav-toggle-bg' | '--neu-nav-toggle-bg-hover' | '--neu-nav-toggle-border' | '--neu-nav-toggle-color' | '--neu-nav-toggle-offset-top' | '--neu-nav-toggle-shadow' | '--neu-nav-toggle-size' | '--neu-notification-unread-bg' | '--neu-number-input-btn-size' | '--neu-number-input-height' | '--neu-number-input-stacked-min-width' | '--neu-number-input-width' | '--neu-on-primary' | '--neu-otp-cell-bg' | '--neu-otp-cell-border' | '--neu-otp-cell-focus-border' | '--neu-otp-cell-radius' | '--neu-otp-cell-size' | '--neu-otp-gap' | '--neu-overlay-bg' | '--neu-overlay-bg-soft' | '--neu-popover-bg' | '--neu-popover-border' | '--neu-popover-color' | '--neu-popover-max-width' | '--neu-popover-min-width' | '--neu-popover-padding' | '--neu-popover-radius' | '--neu-popover-shadow' | '--neu-primary' | '--neu-primary-100' | '--neu-primary-200' | '--neu-primary-50' | '--neu-primary-alpha' | '--neu-primary-contrast' | '--neu-primary-dark' | '--neu-primary-fg' | '--neu-primary-light' | '--neu-primary-soft' | '--neu-primary-solid' | '--neu-primary-solid-fg' | '--neu-primary-solid-hover' | '--neu-radius' | '--neu-radius-2xl' | '--neu-radius-full' | '--neu-radius-lg' | '--neu-radius-sm' | '--neu-radius-xl' | '--neu-radius-xs' | '--neu-scroll-area-thumb' | '--neu-secondary' | '--neu-secondary-dark' | '--neu-secondary-fg' | '--neu-select-option-height' | '--neu-shadow' | '--neu-shadow-glow' | '--neu-shadow-lg' | '--neu-shadow-sm' | '--neu-shadow-xs' | '--neu-sidebar-bg' | '--neu-sidebar-collapsed-width' | '--neu-sidebar-width' | '--neu-space-1' | '--neu-space-10' | '--neu-space-12' | '--neu-space-16' | '--neu-space-2' | '--neu-space-3' | '--neu-space-4' | '--neu-space-5' | '--neu-space-6' | '--neu-space-8' | '--neu-spinner-track' | '--neu-split-button-primary-divider' | '--neu-splitter-handle-bg' | '--neu-splitter-handle-size' | '--neu-stepper-connector-gap' | '--neu-stepper-indicator-radius' | '--neu-stepper-indicator-size' | '--neu-success' | '--neu-success-bg' | '--neu-success-text' | '--neu-surface' | '--neu-surface-1' | '--neu-surface-2' | '--neu-surface-3' | '--neu-surface-hover' | '--neu-surface-inverse' | '--neu-surface-muted' | '--neu-surface-raised' | '--neu-surface-rgb' | '--neu-table-badge-danger-bg' | '--neu-table-badge-danger-text' | '--neu-table-badge-success-bg' | '--neu-table-badge-success-text' | '--neu-table-badge-warning-bg' | '--neu-table-badge-warning-text' | '--neu-table-cell-block' | '--neu-table-cell-block-compact' | '--neu-table-cell-block-relaxed' | '--neu-table-cell-inline' | '--neu-table-density-compact-padding' | '--neu-table-density-relaxed-padding' | '--neu-table-group-background' | '--neu-table-header-height' | '--neu-table-max-height' | '--neu-table-selected-background' | '--neu-table-space-sm' | '--neu-table-space-xs' | '--neu-table-state-block' | '--neu-table-sticky-offset' | '--neu-table-stripe-background' | '--neu-table-virtual-block-size' | '--neu-terminal-bg' | '--neu-terminal-border' | '--neu-terminal-error' | '--neu-terminal-font' | '--neu-terminal-muted' | '--neu-terminal-prompt' | '--neu-terminal-text' | '--neu-text' | '--neu-text-2xl' | '--neu-text-3xl' | '--neu-text-4xl' | '--neu-text-base' | '--neu-text-disabled' | '--neu-text-inverse' | '--neu-text-lg' | '--neu-text-muted' | '--neu-text-primary' | '--neu-text-secondary' | '--neu-text-sm' | '--neu-text-xl' | '--neu-text-xs' | '--neu-toast-bg' | '--neu-toast-radius' | '--neu-toast-shadow' | '--neu-toolbar-bg' | '--neu-toolbar-color' | '--neu-toolbar-primary-bg' | '--neu-toolbar-primary-color' | '--neu-tooltip-bg' | '--neu-tooltip-fg' | '--neu-tooltip-radius' | '--neu-tooltip-shadow' | '--neu-transition' | '--neu-transition-bounce' | '--neu-transition-slow' | '--neu-tree-table-cell-block' | '--neu-tree-table-cell-inline' | '--neu-tree-table-selected-background' | '--neu-tree-table-virtual-block-size' | '--neu-warning' | '--neu-warning-bg' | '--neu-warning-text' | '--neu-z-base' | '--neu-z-dropdown' | '--neu-z-modal' | '--neu-z-overlay' | '--neu-z-sidebar' | '--neu-z-sticky' | '--neu-z-toast';
```

## provideNeuIconResolver

```typescript
export declare function provideNeuIconResolver(resolver: NeuIconResolver): EnvironmentProviders;
```

## provideNeuOverlayDismissGuard

```typescript
export declare function provideNeuOverlayDismissGuard(guard: NeuOverlayDismissGuard): Provider;
```

