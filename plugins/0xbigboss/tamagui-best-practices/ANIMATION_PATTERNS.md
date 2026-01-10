# Animation Patterns

Prescriptive patterns for animations and transitions. Read this before adding animations.

## Mandatory Rules

### 1. Never Conditionally Include animation Prop

Animation hooks are called based on prop presence. Toggling the prop causes errors:

```tsx
// WRONG - causes hook errors
<View animation={isAnimated ? 'quick' : undefined} />
<View {...(isAnimated && { animation: 'quick' })} />

// CORRECT - use null to disable
<View animation={isAnimated ? 'quick' : null} />
```

### 2. Use animateOnly for Performance

Restrict animations to necessary properties:

```tsx
// WRONG - animates everything
<View animation="quick" opacity={0.5} scale={0.9} />

// CORRECT - only animate what's needed
<View
  animation="quick"
  animateOnly={['opacity', 'transform']}
  opacity={0.5}
  scale={0.9}
/>
```

### 3. Animation Props on Content, Not Containers

For Dialog/Sheet/Popover, apply to Content component:

```tsx
// WRONG
<Dialog.Portal animation="quick">

// CORRECT
<Dialog.Content animation="quick" enterStyle={{...}}>
```

## Animation Drivers

Choose based on platform:

| Driver | Package | Best For |
|--------|---------|----------|
| CSS | `@tamagui/animations-css` | Web apps, small bundle |
| Animated | `@tamagui/animations-react-native` | Cross-platform RN |
| Reanimated | `@tamagui/animations-moti` | Native apps, complex motion |

### CSS Driver Config

```tsx
// tamagui.config.ts
import { createAnimations } from '@tamagui/animations-css'

const animations = createAnimations({
  fast: 'ease-in 150ms',
  medium: 'ease-in 300ms',
  slow: 'ease-in 450ms',
  quick: 'ease-out 100ms',
  bouncy: 'cubic-bezier(0.175, 0.885, 0.32, 1.275) 300ms',
})
```

### Reanimated Driver Config

```tsx
// tamagui.config.ts
import { createAnimations } from '@tamagui/animations-moti'

const animations = createAnimations({
  fast: {
    type: 'spring',
    damping: 20,
    mass: 1.2,
    stiffness: 250,
  },
  medium: {
    type: 'spring',
    damping: 15,
    mass: 1,
    stiffness: 200,
  },
  slow: {
    type: 'spring',
    damping: 20,
    stiffness: 60,
  },
  quick: {
    type: 'spring',
    damping: 20,
    mass: 0.8,
    stiffness: 300,
  },
  bouncy: {
    type: 'spring',
    damping: 10,
    mass: 0.9,
    stiffness: 100,
  },
})
```

## enterStyle and exitStyle

Define initial and final animation states:

```tsx
<View
  animation="quick"
  enterStyle={{ opacity: 0, y: -20, scale: 0.9 }}
  exitStyle={{ opacity: 0, y: 10, scale: 0.95 }}
>
```

### Default Normalization

Tamagui normalizes unmapped properties:
- `opacity` defaults to `1`
- `x`, `y` default to `0`
- `scale` defaults to `1`

So `enterStyle={{ opacity: 0 }}` animates from 0 to 1 automatically.

## Per-Property Animation

Customize animation per property:

```tsx
// Simple - same animation for all
<View animation="quick" />

// Per-property config
<View
  animation={{
    opacity: 'slow',
    y: {
      type: 'quick',
      overshootClamping: true,
    },
  }}
  enterStyle={{ opacity: 0, y: -20 }}
/>

// Array syntax for base + overrides
<View
  animation={[
    'quick',
    {
      opacity: {
        overshootClamping: true,
      },
    },
  ]}
/>
```

## AnimatePresence

For mount/unmount animations:

```tsx
import { AnimatePresence } from 'tamagui'

function Notification({ show, message }: { show: boolean; message: string }) {
  return (
    <AnimatePresence>
      {show && (
        <View
          key="notification"
          animation="quick"
          enterStyle={{ opacity: 0, y: -50 }}
          exitStyle={{ opacity: 0, y: -50 }}
          padding="$4"
          backgroundColor="$blue10"
        >
          <Text color="white">{message}</Text>
        </View>
      )}
    </AnimatePresence>
  )
}
```

### Unique Keys Required

Each child needs a unique `key` for AnimatePresence to track:

```tsx
<AnimatePresence>
  {items.map(item => (
    <View
      key={item.id}  // REQUIRED
      animation="quick"
      enterStyle={{ opacity: 0 }}
      exitStyle={{ opacity: 0 }}
    >
      {item.content}
    </View>
  ))}
</AnimatePresence>
```

### Exit Direction with custom

Pass direction for exit animations:

```tsx
<AnimatePresence custom={{ direction: 'left' }}>
  {show && (
    <View
      key="slide"
      animation="quick"
      enterStyle={{ x: 100 }}
      exitStyle={(custom) => ({ x: custom.direction === 'left' ? -100 : 100 })}
    />
  )}
</AnimatePresence>
```

## Common Animation Presets

### Fade

```tsx
<View
  animation="quick"
  enterStyle={{ opacity: 0 }}
  exitStyle={{ opacity: 0 }}
/>
```

### Fade + Scale

```tsx
<View
  animation="quick"
  animateOnly={['opacity', 'transform']}
  enterStyle={{ opacity: 0, scale: 0.9 }}
  exitStyle={{ opacity: 0, scale: 0.95 }}
/>
```

### Slide Up

```tsx
<View
  animation="quick"
  animateOnly={['opacity', 'transform']}
  enterStyle={{ opacity: 0, y: 20 }}
  exitStyle={{ opacity: 0, y: 20 }}
/>
```

### Slide Down (Dialog style)

```tsx
<View
  animation={['quick', { opacity: { overshootClamping: true } }]}
  animateOnly={['opacity', 'transform']}
  enterStyle={{ opacity: 0, y: -20, scale: 0.9 }}
  exitStyle={{ opacity: 0, y: 10, scale: 0.95 }}
/>
```

### Bounce In

```tsx
<View
  animation="bouncy"
  animateOnly={['transform']}
  enterStyle={{ scale: 0.5 }}
/>
```

## Overlay Animations

Standard patterns for Dialog/Sheet/Popover:

### Overlay

```tsx
<Dialog.Overlay
  animation="quick"
  opacity={0.5}
  enterStyle={{ opacity: 0 }}
  exitStyle={{ opacity: 0 }}
/>
```

### Content

```tsx
<Dialog.Content
  animation={['quick', { opacity: { overshootClamping: true } }]}
  animateOnly={['transform', 'opacity']}
  enterStyle={{ x: 0, y: -20, opacity: 0, scale: 0.9 }}
  exitStyle={{ x: 0, y: 10, opacity: 0, scale: 0.95 }}
/>
```

## Performance Notes

1. **Animation hooks are expensive** - only add `animation` prop when needed
2. **Hot reload issues** - adding animations during HMR may error; save again or reload
3. **Bundle size** - CSS driver is smallest, Reanimated is largest
4. **Native performance** - Reanimated runs off-thread for smoother native animations
5. **Use animateOnly** - always restrict to needed properties

## Disabling Animations

For reduced motion or performance:

```tsx
// Disable with null
<View animation={prefersReducedMotion ? null : 'quick'} />

```

## Debug Animations

Enable debug mode to see animation frames:

```tsx
// In development
<View animation="quick" debug />
```
