---
name: tamagui-best-practices
description: Use when working with Tamagui projects (tamagui.config.ts, @tamagui imports).
---

# Tamagui Best Practices

Tamagui v1.x patterns beyond fundamentals: Config v4, compiler optimization, compound components, and gotchas.

## Reference Files — Read Before Writing Code

| Context | File | What it covers |
|---------|------|----------------|
| Dialog, Sheet, modal overlays | @DIALOG_PATTERNS.md | Adapt component, accessibility |
| Form, Input, Label, validation | @FORM_PATTERNS.md | zod integration |
| Animations, transitions | @ANIMATION_PATTERNS.md | drivers, enterStyle/exitStyle |
| Popover, Tooltip, Select | @OVERLAY_PATTERNS.md | overlay primitives |
| Compiler optimization | @COMPILER_PATTERNS.md | what the compiler can/cannot flatten |
| Design tokens, theming | @DESIGN_SYSTEM.md | palette, token structure |

## Config v4

Minimal setup with `@tamagui/config/v4`. Add `styleCompat: 'react-native'` for new projects to align `flexBasis` with React Native behavior:

```tsx
import { defaultConfig } from '@tamagui/config/v4'
import { createTamagui } from 'tamagui'

export const config = createTamagui({
  ...defaultConfig,
  settings: { ...defaultConfig.settings, styleCompat: 'react-native' },
})

declare module 'tamagui' {
  interface TamaguiCustomConfig extends typeof config {}
}
```

For custom themes use `createThemes` with `palette`/`accent`/`childrenThemes` — see @DESIGN_SYSTEM.md.

## Compiler Optimization Rules

- Use `styled()` variants instead of inline conditionals — dynamic values break flattening.
- Avoid `style={{ ... }}` with variables; use variant props instead.
- The `context` pattern (createStyledContext) disables compiler flattening — use for higher-level components (Button, Card), not primitives.

```tsx
// BAD — breaks compiler
<View backgroundColor={isDark ? '$gray1' : '$gray12'} />

// GOOD — use variants
const Box = styled(View, {
  variants: {
    dark: { true: { backgroundColor: '$gray1' }, false: { backgroundColor: '$gray12' } },
  },
})
```

## styled() vs Inline

- `styled()`: reusable components, variant-driven behavior, compiler-optimizable primitives.
- Inline props: one-off layout adjustments on already-styled components.
- Always use `as const` on `variants` objects (TypeScript limitation until inferred const generics).

## Key Gotchas

**Prop order determines override priority** — props after a spread cannot be overridden by callers:
```tsx
// width is locked; backgroundColor can be overridden
<View backgroundColor="$red10" {...props} width={200} />
```

**Variant order matters** — later props win:
```tsx
<Component scale={3} huge />  // scale = 3 (scale listed first)
<Component huge scale={3} />  // scale = 2 (huge overrides, comes first in variants)
```

**Use `.styleable()` when wrapping styled components** — preserves variant inheritance:
```tsx
const CorrectWrapper = StyledText.styleable((props, ref) => (
  <StyledText ref={ref} {...props} />
))
```

**`accept` prop for non-standard token resolution** (SVG fill/stroke, contentContainerStyle):
```tsx
const StyledSVG = styled(SVG, {}, { accept: { fill: 'color', stroke: 'color' } as const })
```

**Import consistency** — `tamagui`, `@tamagui/core`, and `@tamagui/button` are different packages; pick one approach per project.

**Never mix RN StyleSheet with Tamagui** — StyleSheet values don't resolve tokens.

**Platform branching for Dialog/Sheet** — use `Adapt` instead of `Platform.OS` checks (see @DIALOG_PATTERNS.md).

## Quick Reference

**Config v4 shorthands**: `bg` backgroundColor, `p` padding, `m` margin, `w` width, `h` height, `br` borderRadius

**Media breakpoints**: `$xs` 660px, `$sm` 800px, `$md` 1020px, `$lg` 1280px, `$xl` 1420px

**Animation drivers**: `css` (web, default), `react-native-reanimated` (native, required)

**Token `$` prefix**: use in props (`color="$color"`), omit in theme definitions (`{ color: palette[11] }`)

## Fetching Current Docs

```bash
curl -sL "https://tamagui.dev/docs/core/configuration.md"
curl -sL "https://tamagui.dev/llms.txt"  # full index
```
