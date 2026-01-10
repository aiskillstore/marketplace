# Design System Thinking for Tamagui

This guide helps create distinctive, polished UIs using Tamagui's design system approach. Adapted from frontend design principles for cross-platform (web + native) contexts.

## Design Thinking Before Coding

Before writing Tamagui code, understand the context:

**Purpose**: What problem does this interface solve? Who uses it?

**Platform Reality**: Will this run on web, iOS, Android, or all three? Each has different interaction patterns (hover vs press, scroll behavior, safe areas).

**Tone**: Commit to an aesthetic direction that works cross-platform:
- Brutally minimal (works everywhere)
- Soft/organic (leverage borderRadius tokens, gentle shadows)
- Editorial/magazine (typography-forward, works best on larger screens)
- Playful/animated (use Tamagui animation drivers strategically)
- Industrial/utilitarian (strong contrast, functional)

**Differentiation**: What makes this unforgettable? The constraint of cross-platform actually forces cleaner design decisions.

## Typography in Tamagui

### Custom Fonts via createFont

```tsx
import { createFont } from 'tamagui'

const headingFont = createFont({
  family: 'SpaceGrotesk',
  size: {
    1: 12,
    2: 14,
    3: 16,
    // ...
    true: 16, // default
  },
  lineHeight: {
    1: 17,
    2: 20,
    3: 22,
  },
  weight: {
    4: '400',
    6: '600',
    7: '700',
  },
  letterSpacing: {
    4: 0,
    7: -0.5,
  },
})
```

### Font Loading by Platform

**Web**: Use `@font-face` or services like Google Fonts, then reference family name.

**Native**: Use expo-font or react-native-asset to bundle fonts, then reference family name.

**Avoid generic system fonts** - Inter, Roboto, Arial create "AI slop" aesthetics. Choose distinctive fonts:
- Display: Space Grotesk, Clash Display, Satoshi, General Sans
- Body: iA Writer, IBM Plex, Source Serif
- Monospace: JetBrains Mono, Berkeley Mono, Monaspace

### Typography Variants

```tsx
const config = createTamagui({
  fonts: {
    heading: headingFont,
    body: bodyFont,
  },
})

// Usage
<Text fontFamily="$heading" fontSize="$8" fontWeight="$7">
  Bold heading
</Text>
```

## Theme-Driven Color Systems

### Intentional Palettes with createThemes

Don't accept default grayscale. Create palettes with character:

```tsx
const warmPalette = [
  '#faf8f5',  // cream white
  '#f5f0e8',
  '#ebe3d6',
  // ... 12 steps
  '#1a1612',  // warm black
]

const coolPalette = [
  '#f8fafc',  // cool white
  '#f0f4f8',
  '#e2e8f0',
  // ... 12 steps
  '#0f172a',  // deep navy
]

createThemes({
  base: {
    palette: {
      light: warmPalette,
      dark: coolPalette,  // Different character, not just inverted
    },
  },
})
```

### Accent Themes for Bold Contrast

```tsx
createThemes({
  accent: {
    palette: {
      light: vibrantAccentPalette,
      dark: deepAccentPalette,
    },
  },
})

// Usage - dramatic color shift
<Theme name="accent">
  <Button>Call to Action</Button>
</Theme>
```

### childrenThemes for Semantic States

```tsx
createThemes({
  childrenThemes: {
    success: { palette: { light: greenPalette, dark: greenDarkPalette } },
    warning: { palette: { light: amberPalette, dark: amberDarkPalette } },
    error: { palette: { light: redPalette, dark: redDarkPalette } },
  },
})

// Usage - contextual coloring
<Theme name="error">
  <Card>
    <Text color="$color">Error state inherits theme</Text>
  </Card>
</Theme>
```

## Motion with Tamagui

### Animation Drivers

| Driver | Platform | Performance | Use Case |
|--------|----------|-------------|----------|
| `css` | Web | Excellent | Default for web |
| `react-native-reanimated` | Native | Native thread | Required for native |

Configure in tamagui.config.ts:
```tsx
import { createAnimations } from '@tamagui/animations-css'
// or
import { createAnimations } from '@tamagui/animations-reanimated'
```

### Page Transitions with enterStyle/exitStyle

```tsx
const FadeIn = styled(View, {
  opacity: 1,
  y: 0,
  enterStyle: {
    opacity: 0,
    y: 20,
  },
  animation: 'quick',
})
```

### Micro-interactions via Pseudo Styles

```tsx
const InteractiveCard = styled(Card, {
  pressStyle: {
    scale: 0.98,
    opacity: 0.9,
  },
  hoverStyle: {
    scale: 1.02,
    shadowRadius: 20,
  },
  animation: 'quick',
})
```

### Staggered Reveals

Use animation delay for orchestrated page loads:

```tsx
{items.map((item, i) => (
  <FadeInItem
    key={item.id}
    animation="quick"
    animateOnly={['opacity', 'transform']}
    enterStyle={{ opacity: 0, y: 20 }}
    style={{ animationDelay: `${i * 50}ms` }}
  >
    {item.content}
  </FadeInItem>
))}
```

### AnimatePresence for Exit Animations

```tsx
import { AnimatePresence } from 'tamagui'

<AnimatePresence>
  {show && (
    <View
      key="modal"
      animation="quick"
      enterStyle={{ opacity: 0, scale: 0.9 }}
      exitStyle={{ opacity: 0, scale: 0.95 }}
    >
      Content
    </View>
  )}
</AnimatePresence>
```

## Spatial Composition

### Intentional Layouts with Stacks

```tsx
// Asymmetric hero layout
<XStack flex={1}>
  <YStack flex={2} padding="$6" justifyContent="center">
    <Text fontSize="$10">Hero Title</Text>
  </YStack>
  <View flex={3} backgroundColor="$color5" />
</XStack>
```

### Responsive Asymmetry

```tsx
<XStack
  flexDirection="column"
  $md={{ flexDirection: 'row' }}
>
  <YStack flex={1} $md={{ flex: 2 }} />
  <YStack flex={1} $md={{ flex: 3 }} />
</XStack>
```

### Negative Space via Tokens

```tsx
// Generous breathing room
<YStack padding="$8" gap="$6">
  <Text>Content with space to breathe</Text>
</YStack>

// Controlled density
<YStack padding="$2" gap="$1">
  <Text>Compact information-dense area</Text>
</YStack>
```

### Grid-Breaking Overlays

```tsx
<View position="relative">
  <Image source={bg} />
  <View
    position="absolute"
    top="$-4"  // Negative token - breaks grid intentionally
    right="$6"
    backgroundColor="$background"
    padding="$4"
    borderRadius="$4"
    elevate
  >
    <Text>Floating element</Text>
  </View>
</View>
```

## Anti-Patterns: Avoiding Generic Tamagui

### Don't: Use defaultConfig without customization

```tsx
// GENERIC
import { defaultConfig } from '@tamagui/config/v4'
export const config = createTamagui(defaultConfig)

// DISTINCTIVE
export const config = createTamagui({
  ...defaultConfig,
  fonts: { heading: myCustomFont, body: myBodyFont },
  themes: myCustomThemes,
})
```

### Don't: Rely on default component styling

Every Button, Card, Input should have intentional styling that reflects your brand, not Tamagui's defaults.

### Don't: Ignore platform-specific opportunities

- Web: Use hover states, cursor changes, keyboard focus rings
- Native: Use native haptics, native sheets, platform navigation patterns

### Don't: Converge on common choices

If you find yourself using the same tokens everywhere (`$4`, `$blue10`, `$gray5`), you're not exploring the design space. Create semantic tokens:

```tsx
const semanticTokens = {
  $heroSpacing: '$8',
  $cardRadius: '$4',
  $subtleBackground: '$gray2',
  $emphasisColor: '$blue9',
}
```

## Design System Checklist

- [ ] Custom fonts loaded (not system defaults)
- [ ] Theme palette has character (not generic grayscale)
- [ ] Accent/semantic themes defined
- [ ] Animation driver configured for target platforms
- [ ] Micro-interactions on interactive elements
- [ ] Responsive breakpoints used intentionally
- [ ] Platform-specific adaptations (Adapt pattern)
- [ ] No reliance on Tamagui default styling
