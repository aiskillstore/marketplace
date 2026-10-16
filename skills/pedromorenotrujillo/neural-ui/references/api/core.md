# @neural-ui/core

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## defineNeuPreset

```typescript
export declare function defineNeuPreset<const T extends NeuPreset & {
    readonly name: string;
}>(preset: T): T & NeuPresetDefinition;
```

## NeuDensity

```typescript
type NeuDensity = 'compact' | 'normal' | 'relaxed';
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

## NeuralUIConfig

```typescript
export interface NeuralUIConfig {
    locale?: string;
    timeZone?: string;
    now?: NeuNow;
    theme?: NeuralUIThemeConfig;
}
```

## NeuralUIThemeConfig

```typescript
export interface NeuralUIThemeConfig {
    preset?: NeuPresetDefinition;
}
```

## NeuTone

```typescript
type NeuTone = 'neutral' | 'brand' | 'info' | 'success' | 'warning' | 'danger';
```

## NeuVariant

```typescript
type NeuVariant = 'solid' | 'soft' | 'outline' | 'ghost' | 'text';
```

## provideNeuralUI

```typescript
export declare function provideNeuralUI(config?: NeuralUIConfig): EnvironmentProviders;
```

