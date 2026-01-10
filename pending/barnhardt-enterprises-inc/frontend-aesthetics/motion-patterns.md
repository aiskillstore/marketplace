# Motion Patterns

Motion is critical for creating polished, professional interfaces. This guide covers CSS-only and Framer Motion patterns for modern web applications.

## Principles

1. **Purposeful** - Every animation should communicate state change
2. **Subtle** - Motion enhances, not distracts
3. **Consistent** - Same duration/easing across similar interactions
4. **Performant** - Use transform/opacity, avoid layout shifts

## Timing Standards

```css
/* Duration scale */
--duration-fast: 150ms;    /* Micro-interactions (hover, toggle) */
--duration-normal: 200ms;  /* Standard transitions */
--duration-slow: 300ms;    /* Page transitions, modals */
--duration-slower: 500ms;  /* Staggered reveals */

/* Easing functions */
--ease-out: cubic-bezier(0.33, 1, 0.68, 1);     /* Default - smooth deceleration */
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);  /* Symmetric - modals */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy - emphasis */
```

## CSS-Only Patterns

### Button Hover
```typescript
// Scale + glow effect (use your brand color for shadow)
<Button className="
  transition-all duration-200 ease-out
  hover:scale-105
  hover:shadow-lg hover:shadow-brand-500/20
  active:scale-95
">
  Click Me
</Button>
```

### Card Hover
```typescript
// Border glow + subtle lift (use your brand color)
<Card className="
  transition-all duration-200 ease-out
  border border-white/5
  hover:border-brand-500/20
  hover:shadow-xl hover:shadow-brand-500/5
  hover:-translate-y-0.5
">
  {content}
</Card>
```

### Link Underline
```typescript
// Animated underline reveal (use your brand color)
<a className="
  relative
  after:absolute after:bottom-0 after:left-0
  after:h-px after:w-0 after:bg-brand-400
  after:transition-all after:duration-200
  hover:after:w-full
">
  Learn More
</a>
```

### Toggle States
```typescript
// Color transition for active state (use your brand color)
<button className={cn(
  "transition-colors duration-150",
  isActive
    ? "bg-brand-500 text-white"
    : "bg-white/5 text-zinc-400 hover:bg-white/10"
)}>
  {label}
</button>
```

### Loading Spinner
```typescript
// Smooth rotation (use your brand color)
<div className="
  w-5 h-5 border-2 border-white/20 border-t-brand-500 rounded-full
  animate-spin
" />

// Or pulsing dot
<div className="
  w-2 h-2 bg-brand-500 rounded-full
  animate-pulse
" />
```

## Tailwind animate-in Classes

Tailwind CSS has built-in animation utilities via `tailwindcss-animate`:

```typescript
// Fade in
<div className="animate-in fade-in duration-300">

// Slide from bottom
<div className="animate-in slide-in-from-bottom-4 duration-300">

// Slide from right (for sidebars)
<div className="animate-in slide-in-from-right duration-300">

// Zoom in (for modals)
<div className="animate-in zoom-in-95 duration-200">

// Combined
<div className="animate-in fade-in slide-in-from-bottom-4 duration-500">

// Fade out
<div className="animate-out fade-out duration-200">
```

### Staggered List (CSS-only)
```typescript
// Using animation-delay with Tailwind
{items.map((item, i) => (
  <div
    key={i}
    className="animate-in fade-in slide-in-from-bottom-4 duration-500"
    style={{ animationDelay: `${i * 100}ms` }}
  >
    {item}
  </div>
))}
```

## Framer Motion Patterns

### Page Enter Animation
```typescript
import { motion } from 'framer-motion'

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  enter: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

export default function Page() {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="enter"
      exit="exit"
      transition={{ duration: 0.3, ease: [0.33, 1, 0.68, 1] }}
    >
      {content}
    </motion.div>
  )
}
```

### Staggered Children
```typescript
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: [0.33, 1, 0.68, 1] }
  }
}

<motion.div variants={container} initial="hidden" animate="show">
  {items.map((i) => (
    <motion.div key={i} variants={item}>
      {i}
    </motion.div>
  ))}
</motion.div>
```

### Modal Animation
```typescript
const modalVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 10
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.2,
      ease: [0.33, 1, 0.68, 1]
    }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.15 }
  }
}

const overlayVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 }
}

<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        variants={overlayVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      />
      <motion.div
        className="fixed inset-0 flex items-center justify-center"
        variants={modalVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        <DialogContent>{children}</DialogContent>
      </motion.div>
    </>
  )}
</AnimatePresence>
```

### Expandable Card
```typescript
const [isExpanded, setIsExpanded] = useState(false)

<motion.div
  layout
  className="bg-[#0f0f0f] rounded-xl overflow-hidden"
  transition={{ duration: 0.3, ease: [0.33, 1, 0.68, 1] }}
>
  <motion.div layout="position" className="p-4">
    <h3>Card Title</h3>
    <Button onClick={() => setIsExpanded(!isExpanded)}>
      {isExpanded ? 'Collapse' : 'Expand'}
    </Button>
  </motion.div>

  <AnimatePresence>
    {isExpanded && (
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        transition={{ duration: 0.2 }}
        className="px-4 pb-4"
      >
        <p>Expanded content here...</p>
      </motion.div>
    )}
  </AnimatePresence>
</motion.div>
```

### Number Counter
```typescript
import { useSpring, animated } from '@react-spring/web'

function AnimatedNumber({ value }: { value: number }) {
  const { number } = useSpring({
    from: { number: 0 },
    number: value,
    delay: 200,
    config: { mass: 1, tension: 20, friction: 10 }
  })

  return <animated.span>{number.to(n => n.toFixed(0))}</animated.span>
}

// Usage
<div className="text-4xl font-bold">
  <AnimatedNumber value={1234} />
</div>
```

### Hover Card Reveal
```typescript
<motion.div
  className="relative group"
  whileHover="hover"
  initial="rest"
>
  <Card>
    <CardContent>Main content</CardContent>

    <motion.div
      className="absolute inset-0 bg-brand-500/10 rounded-xl"
      variants={{
        rest: { opacity: 0 },
        hover: { opacity: 1 }
      }}
      transition={{ duration: 0.2 }}
    />

    <motion.div
      className="absolute bottom-4 right-4"
      variants={{
        rest: { opacity: 0, y: 10 },
        hover: { opacity: 1, y: 0 }
      }}
      transition={{ duration: 0.2 }}
    >
      <Button size="sm">View Details</Button>
    </motion.div>
  </Card>
</motion.div>
```

## Data Dashboard Patterns

### Skeleton Loading
```typescript
// Pulsing skeleton for loading states
<div className="space-y-4">
  <div className="h-8 w-48 bg-white/5 rounded animate-pulse" />
  <div className="h-4 w-full bg-white/5 rounded animate-pulse" />
  <div className="h-4 w-3/4 bg-white/5 rounded animate-pulse" />
</div>

// Or shimmer effect
<div className="
  h-32 bg-gradient-to-r from-white/5 via-white/10 to-white/5
  bg-[length:200%_100%] animate-shimmer rounded-xl
" />

// Add to tailwind.config.js:
// animation: { shimmer: 'shimmer 2s infinite' }
// keyframes: { shimmer: { '0%': { backgroundPosition: '200% 0' }, '100%': { backgroundPosition: '-200% 0' } } }
```

### Live Data Update
```typescript
// Flash effect when data updates (use your brand RGB values)
const [flash, setFlash] = useState(false)

useEffect(() => {
  setFlash(true)
  const timer = setTimeout(() => setFlash(false), 500)
  return () => clearTimeout(timer)
}, [data])

<motion.div
  animate={{
    backgroundColor: flash ? 'rgba(var(--brand-rgb), 0.1)' : 'transparent'
  }}
  transition={{ duration: 0.5 }}
  className="p-4 rounded-lg"
>
  {data}
</motion.div>
```

### Progress Ring
```typescript
<svg className="w-16 h-16 -rotate-90">
  {/* Background ring */}
  <circle
    cx="32" cy="32" r="28"
    className="stroke-white/10 fill-none"
    strokeWidth="4"
  />
  {/* Progress ring (use your brand color) */}
  <motion.circle
    cx="32" cy="32" r="28"
    className="stroke-brand-500 fill-none"
    strokeWidth="4"
    strokeLinecap="round"
    initial={{ pathLength: 0 }}
    animate={{ pathLength: progress / 100 }}
    transition={{ duration: 1, ease: "easeOut" }}
    style={{
      strokeDasharray: "1",
      strokeDashoffset: "0"
    }}
  />
</svg>
```

## Performance Tips

1. **Use transform/opacity** - These are GPU-accelerated
   ```typescript
   // GOOD - GPU accelerated
   className="transition-transform hover:scale-105"
   className="transition-opacity hover:opacity-80"

   // AVOID - Causes layout recalculation
   className="transition-all hover:w-full"
   className="transition-all hover:h-auto"
   ```

2. **Use will-change sparingly**
   ```typescript
   // Only for known animations
   <motion.div className="will-change-transform">
   ```

3. **Prefer CSS for simple transitions**
   ```typescript
   // Simple hover - use CSS
   className="transition-colors duration-200 hover:bg-brand-500"

   // Complex orchestration - use Framer Motion
   <motion.div variants={...} animate={...}>
   ```

4. **Reduce motion for accessibility**
   ```typescript
   // Respect user preferences
   <motion.div
     initial={{ opacity: 0, y: 20 }}
     animate={{ opacity: 1, y: 0 }}
     transition={{
       duration: prefersReducedMotion ? 0 : 0.3
     }}
   >
   ```
