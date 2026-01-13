# Tamagui Compiler Optimization Patterns

The Tamagui compiler extracts styles at build time, generating atomic CSS and flattening components to native primitives (`div` on web, `View` on native).

## What Gets Optimized

### Static Props
```tsx
// OPTIMIZED - all values known at compile time
<View backgroundColor="$blue10" padding="$4" borderRadius="$2" />
```

### Variants
```tsx
// OPTIMIZED - variant values are static
<Button size="$large" variant="primary" />
```

### Spread from Variables (with constraints)
```tsx
// OPTIMIZED - if buttonProps contains only static values
const buttonProps = { size: '$large' } as const
<Button {...buttonProps} />
```

## What Breaks Optimization

### Dynamic Values
```tsx
// NOT OPTIMIZED - runtime calculation
<View width={containerWidth * 0.5} />
<View backgroundColor={isDark ? '$gray1' : '$gray12'} />

// FIX: Use variants
const Box = styled(View, {
  variants: {
    half: { true: { width: '50%' } },
    dark: { true: { bg: '$gray1' }, false: { bg: '$gray12' } },
  },
})
```

### Inline Functions
```tsx
// NOT OPTIMIZED - function reference
<View onPress={() => doSomething()} />
```

### Non-deterministic Spread
```tsx
// NOT OPTIMIZED - props could be anything
<View {...props} />

// PARTIALLY OPTIMIZED - known static props extracted
<View backgroundColor="$blue10" {...props} />
```

### Theme Usage on Native (experimental)
```tsx
// NOT OPTIMIZED on native by default
<View backgroundColor="$background" />

// Enable with experimentalFlattenThemesOnNative (v1.75+)
```

## Escape Hatches

### File-Level: `// tamagui-ignore`

Disable compiler for entire file:
```tsx
// tamagui-ignore

import { View } from 'tamagui'
// All components in this file skip optimization
```

### Component-Level: `disableOptimization`

Disable for single component instance:
```tsx
<View disableOptimization backgroundColor="$blue10" />
```

## Bundler Configuration

### Vite

```tsx
// vite.config.ts
import { tamaguiPlugin } from '@tamagui/vite-plugin'

export default defineConfig({
  plugins: [
    tamaguiPlugin({
      config: 'src/tamagui.config.ts',
      components: ['tamagui'],
      optimize: true,
    }),
  ],
})
```

### Webpack

```js
// webpack.config.js
const { TamaguiPlugin } = require('tamagui-loader')

module.exports = {
  plugins: [
    new TamaguiPlugin({
      config: './tamagui.config.ts',
      components: ['tamagui'],
      importsWhitelist: ['constants.js', 'colors.js'],
      logTimings: true,
      disableExtraction: process.env.NODE_ENV === 'development',
    }),
  ],
}
```

### Next.js

```js
// next.config.js
const { withTamagui } = require('@tamagui/next-plugin')

module.exports = withTamagui({
  config: './tamagui.config.ts',
  components: ['tamagui'],
  disableExtraction: process.env.NODE_ENV === 'development',
  excludeReactNativeWebExports: ['Switch', 'ProgressBar', 'Picker'],
})
```

### Babel / Metro (React Native)

```js
// babel.config.js
module.exports = {
  plugins: [
    [
      '@tamagui/babel-plugin',
      {
        components: ['tamagui'],
        config: './tamagui.config.ts',
        logTimings: true,
        disableExtraction: process.env.NODE_ENV === 'development',
        // v1.75+: experimental native theme flattening
        experimentalFlattenThemesOnNative: true,
      },
    ],
  ],
}
```

### CLI-Based (Turbopack, any bundler)

For bundlers without plugins, use pre-compilation:

```bash
# Install
yarn add -D @tamagui/cli

# Build for web
npx tamagui build --target web ./src

# Build for native
npx tamagui build --target native ./src

# Verify optimization count in CI
npx tamagui build --target web --expect-optimizations 10 ./src
```

Config file:
```ts
// tamagui.build.ts
import type { TamaguiBuildOptions } from 'tamagui'

export default {
  config: './tamagui.config.ts',
  components: ['tamagui'],
  importsWhitelist: ['constants.js', 'colors.js'],
  outputCSS: './public/tamagui.css',
} satisfies TamaguiBuildOptions
```

## Key Options

| Option | Description |
|--------|-------------|
| `config` | Path to tamagui.config.ts |
| `components` | Array of component packages to optimize |
| `importsWhitelist` | Files whose exports can be evaluated at compile time |
| `disableExtraction` | Skip optimization (faster dev builds) |
| `logTimings` | Log compilation timing info |
| `enableDynamicEvaluation` | Experimental: optimize inline styled() calls |

## Development vs Production

**Development**: Set `disableExtraction: true` for faster HMR and easier debugging.

**Production**: Enable full extraction for optimal bundle size and runtime performance.

```js
{
  disableExtraction: process.env.NODE_ENV === 'development',
}
```

## Debugging Optimization

1. **Check output**: Look for `.tamagui` directory with compiled output
2. **Add to .gitignore**: The `.tamagui` directory should not be committed
3. **Use logTimings**: See which files are being processed
4. **Inspect data- attributes**: In dev mode, optimized components get `data-` attributes showing optimization info
