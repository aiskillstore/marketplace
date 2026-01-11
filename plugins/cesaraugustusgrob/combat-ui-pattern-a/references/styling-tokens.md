# Styling Tokens - Pattern A Split-Panel Combat UI

## Color Palette

### Base Colors (Zinc Scale)

```typescript
const COLORS = {
  // Backgrounds
  bg: {
    primary: 'bg-zinc-950',      // #09090b - Deepest
    secondary: 'bg-zinc-900',    // #18181b - Panels
    elevated: 'bg-zinc-800',     // #27272a - Cards, buttons
    subtle: 'bg-zinc-900/90',    // With transparency
    overlay: 'bg-black/80',      // Cooldown overlays
  },

  // Borders
  border: {
    default: 'border-zinc-700',  // #3f3f46
    subtle: 'border-zinc-800',   // #27272a
    strong: 'border-zinc-600',   // #52525b
  },

  // Text
  text: {
    primary: 'text-zinc-100',    // #f4f4f5 - Headings
    secondary: 'text-zinc-300',  // #d4d4d8 - Body
    tertiary: 'text-zinc-400',   // #a1a1aa - Labels
    muted: 'text-zinc-500',      // #71717a - Hints
    disabled: 'text-zinc-600',   // #52525b
  },
};
```

### Accent Colors

```typescript
const ACCENTS = {
  // Health (Red)
  health: {
    bar: 'bg-red-500',           // #ef4444
    barGradient: 'from-red-600 to-red-400',
    text: 'text-red-400',
    border: 'border-red-500',
    glow: 'shadow-red-500/30',
  },

  // Chakra (Cyan)
  chakra: {
    bar: 'bg-cyan-500',          // #06b6d4
    barGradient: 'from-cyan-600 to-cyan-400',
    text: 'text-cyan-400',
    border: 'border-cyan-500',
    glow: 'shadow-cyan-500/30',
  },

  // XP (Amber)
  xp: {
    bar: 'bg-amber-500',         // #f59e0b
    barGradient: 'from-amber-600 to-amber-400',
    text: 'text-amber-400',
  },

  // Selection/Active (Amber/Gold)
  selection: {
    border: 'border-amber-400',
    ring: 'ring-amber-400/40',
    text: 'text-amber-400',
    glow: 'shadow-[0_0_20px_rgba(251,191,36,0.3)]',
  },

  // SIDE skills (Blue)
  side: {
    border: 'border-blue-600',
    borderHover: 'hover:border-blue-400',
    text: 'text-blue-400',
    bg: 'bg-blue-950/30',
  },

  // TOGGLE skills (Amber)
  toggle: {
    border: 'border-amber-600',
    borderActive: 'border-amber-500',
    ring: 'ring-amber-500/30',
    text: 'text-amber-400',
  },

  // Damage types
  damage: {
    physical: 'text-orange-400',  // #fb923c
    elemental: 'text-purple-400', // #c084fc
    mental: 'text-indigo-400',    // #818cf8
    true: 'text-white',
  },
};
```

### Element Colors

```typescript
const ELEMENTS = {
  FIRE: {
    primary: 'text-red-400',
    bg: 'bg-red-500/20',
    border: 'border-red-500/50',
    icon: '🔥',
  },
  WATER: {
    primary: 'text-blue-400',
    bg: 'bg-blue-500/20',
    border: 'border-blue-500/50',
    icon: '💧',
  },
  LIGHTNING: {
    primary: 'text-yellow-400',
    bg: 'bg-yellow-500/20',
    border: 'border-yellow-500/50',
    icon: '⚡',
  },
  EARTH: {
    primary: 'text-amber-600',
    bg: 'bg-amber-600/20',
    border: 'border-amber-600/50',
    icon: '🪨',
  },
  WIND: {
    primary: 'text-emerald-400',
    bg: 'bg-emerald-500/20',
    border: 'border-emerald-500/50',
    icon: '🌀',
  },
  PHYSICAL: {
    primary: 'text-orange-400',
    bg: 'bg-orange-500/20',
    border: 'border-orange-500/50',
    icon: '👊',
  },
  MENTAL: {
    primary: 'text-pink-400',
    bg: 'bg-pink-500/20',
    border: 'border-pink-500/50',
    icon: '👁️',
  },
};
```

### Rarity Colors

```typescript
const RARITY = {
  COMMON: {
    border: 'border-zinc-500',
    text: 'text-zinc-400',
    bg: 'bg-zinc-800',
  },
  RARE: {
    border: 'border-blue-500',
    text: 'text-blue-400',
    bg: 'bg-blue-950/50',
  },
  EPIC: {
    border: 'border-purple-500',
    text: 'text-purple-400',
    bg: 'bg-purple-950/50',
  },
  LEGENDARY: {
    border: 'border-amber-400',
    text: 'text-amber-400',
    bg: 'bg-amber-950/50',
    glow: 'shadow-[0_0_15px_rgba(251,191,36,0.3)]',
  },
  CURSED: {
    border: 'border-red-600',
    text: 'text-red-400',
    bg: 'bg-red-950/50',
  },
};
```

### Buff/Debuff Colors

```typescript
const EFFECTS = {
  positive: {
    bg: 'bg-green-950/80',
    border: 'border-green-500/30',
    text: 'text-green-200',
  },
  negative: {
    bg: 'bg-red-950/80',
    border: 'border-red-500/30',
    text: 'text-red-200',
  },
  neutral: {
    bg: 'bg-zinc-800/80',
    border: 'border-zinc-600/30',
    text: 'text-zinc-200',
  },
};
```

---

## Typography

### Font Families

```typescript
const FONTS = {
  heading: 'font-sans',           // System UI / Inter
  body: 'font-sans',
  mono: 'font-mono',              // JetBrains Mono / monospace
};
```

### Font Sizes

```typescript
const TEXT_SIZES = {
  xs: 'text-xs',      // 12px
  sm: 'text-sm',      // 14px
  base: 'text-base',  // 16px
  lg: 'text-lg',      // 18px
  xl: 'text-xl',      // 20px
  '2xl': 'text-2xl',  // 24px
  '3xl': 'text-3xl',  // 30px
  '4xl': 'text-4xl',  // 36px
};
```

### Font Weights

```typescript
const FONT_WEIGHTS = {
  normal: 'font-normal',    // 400
  medium: 'font-medium',    // 500
  semibold: 'font-semibold', // 600
  bold: 'font-bold',        // 700
  black: 'font-black',      // 900
};
```

### Common Text Styles

```typescript
const TEXT_STYLES = {
  // Headings
  h1: 'text-2xl font-bold text-zinc-100',
  h2: 'text-xl font-semibold text-zinc-100',
  h3: 'text-lg font-semibold text-zinc-200',

  // Body
  body: 'text-base text-zinc-300',
  small: 'text-sm text-zinc-400',

  // Labels
  label: 'text-xs font-medium uppercase tracking-wider text-zinc-500',
  badge: 'text-[10px] font-mono uppercase tracking-wider',

  // Numbers
  statNumber: 'text-2xl font-bold font-mono tabular-nums',
  damageNumber: 'text-3xl font-black',
  smallNumber: 'text-sm font-mono',
};
```

---

## Spacing

### Padding

```typescript
const PADDING = {
  none: 'p-0',
  xs: 'p-1',      // 4px
  sm: 'p-2',      // 8px
  md: 'p-3',      // 12px
  base: 'p-4',    // 16px
  lg: 'p-6',      // 24px
  xl: 'p-8',      // 32px

  // Asymmetric
  panelX: 'px-4',
  panelY: 'py-3',
  cardX: 'px-3',
  cardY: 'py-2',
};
```

### Gaps

```typescript
const GAPS = {
  none: 'gap-0',
  xs: 'gap-1',    // 4px
  sm: 'gap-2',    // 8px
  md: 'gap-3',    // 12px
  base: 'gap-4',  // 16px
  lg: 'gap-6',    // 24px
};
```

### Margins

```typescript
const MARGINS = {
  section: 'mt-4',  // Between sections
  item: 'mt-2',     // Between items
  tight: 'mt-1',    // Tight spacing
};
```

---

## Borders & Shadows

### Border Radius

```typescript
const RADIUS = {
  none: 'rounded-none',
  sm: 'rounded-sm',     // 2px
  base: 'rounded',      // 4px
  md: 'rounded-md',     // 6px
  lg: 'rounded-lg',     // 8px
  xl: 'rounded-xl',     // 12px
  full: 'rounded-full', // 9999px
};
```

### Border Widths

```typescript
const BORDER_WIDTH = {
  none: 'border-0',
  default: 'border',     // 1px
  thick: 'border-2',     // 2px
};
```

### Box Shadows

```typescript
const SHADOWS = {
  none: 'shadow-none',
  sm: 'shadow-sm',
  base: 'shadow',
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: 'shadow-xl',

  // Glow effects
  glowRed: 'shadow-[0_0_10px_rgba(239,68,68,0.3)]',
  glowCyan: 'shadow-[0_0_10px_rgba(6,182,212,0.3)]',
  glowAmber: 'shadow-[0_0_10px_rgba(245,158,11,0.3)]',
  glowPurple: 'shadow-[0_0_10px_rgba(168,85,247,0.3)]',

  // Inner shadows
  inner: 'shadow-inner',
  innerDark: 'shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]',
};
```

---

## Component Presets

### Panel Styles

```typescript
const PANELS = {
  // Character panel
  character: `
    bg-zinc-900/95
    border border-zinc-700
    rounded-lg
    p-4
    backdrop-blur-sm
  `,

  // Header bar
  header: `
    bg-zinc-900/90
    border-b border-zinc-700
    px-4 py-2
  `,

  // Action dock
  dock: `
    bg-zinc-900/95
    border-t border-zinc-700
    px-4 py-3
  `,

  // Stats container
  stats: `
    bg-zinc-900/80
    border border-zinc-700
    rounded-lg
    px-4 py-3
  `,
};
```

### Card Styles

```typescript
const CARDS = {
  // Quick action card (SIDE/TOGGLE)
  quick: `
    w-16 h-16
    rounded-lg
    border
    bg-zinc-800/80
    flex items-center justify-center
    transition-all duration-200
    cursor-pointer
  `,

  // Main action card
  main: `
    min-w-[140px]
    aspect-[7/5]
    rounded-lg
    border
    bg-zinc-800/90
    overflow-hidden
    relative
    transition-all duration-200
    cursor-pointer
  `,

  // Buff icon
  buff: `
    px-2 py-1
    rounded
    text-[10px]
    font-mono
    uppercase
    tracking-wider
    backdrop-blur-sm
  `,
};
```

### Button Styles

```typescript
const BUTTONS = {
  // Primary action
  primary: `
    px-4 py-2
    bg-amber-600
    hover:bg-amber-500
    text-white
    font-semibold
    rounded-lg
    transition-colors duration-200
  `,

  // Secondary action
  secondary: `
    px-4 py-2
    bg-zinc-700
    hover:bg-zinc-600
    text-zinc-200
    rounded-lg
    border border-zinc-600
    transition-colors duration-200
  `,

  // Ghost button
  ghost: `
    px-3 py-1.5
    hover:bg-zinc-800
    text-zinc-400
    hover:text-zinc-200
    rounded
    transition-colors duration-200
  `,

  // Disabled state
  disabled: `
    opacity-50
    cursor-not-allowed
    pointer-events-none
  `,
};
```

### Bar Styles

```typescript
const BARS = {
  // Resource bar container
  container: `
    w-full
    h-5
    bg-zinc-800
    rounded
    overflow-hidden
    relative
    border border-zinc-700
  `,

  // HP bar fill
  hpFill: `
    h-full
    bg-gradient-to-r from-red-600 to-red-400
    transition-all duration-300 ease-out
  `,

  // CP bar fill
  cpFill: `
    h-full
    bg-gradient-to-r from-cyan-600 to-cyan-400
    transition-all duration-300 ease-out
  `,

  // XP bar fill
  xpFill: `
    h-full
    bg-gradient-to-r from-amber-600 to-amber-400
    transition-all duration-300 ease-out
  `,

  // Damage preview ghost
  damagePreview: `
    absolute top-0 right-0
    h-full
    bg-red-400/30
    transition-all duration-200
  `,
};
```

---

## Utility Classes

### Transparency

```typescript
const TRANSPARENCY = {
  '90': '/90',  // 90% opacity
  '80': '/80',
  '70': '/70',
  '50': '/50',
  '30': '/30',
  '20': '/20',
  '10': '/10',
};
```

### Backdrop Effects

```typescript
const BACKDROP = {
  blur: 'backdrop-blur-sm',
  blurMd: 'backdrop-blur-md',
  blurLg: 'backdrop-blur-lg',
};
```

### Transitions

```typescript
const TRANSITIONS = {
  fast: 'transition-all duration-150 ease-out',
  normal: 'transition-all duration-200 ease-out',
  slow: 'transition-all duration-300 ease-out',
  colors: 'transition-colors duration-200',
  transform: 'transition-transform duration-200',
};
```

### Hover Effects

```typescript
const HOVER = {
  scale: 'hover:scale-[1.02]',
  scaleUp: 'hover:scale-105',
  brighten: 'hover:brightness-110',
  glow: 'hover:shadow-lg',
};
```

---

## Responsive Prefixes

```typescript
// Apply styles at breakpoints
const BREAKPOINTS = {
  sm: 'sm:',    // 640px+
  md: 'md:',    // 768px+
  lg: 'lg:',    // 1024px+
  xl: 'xl:',    // 1280px+
};

// Example usage
const responsiveGrid = 'grid-cols-2 sm:grid-cols-4 md:grid-cols-6';
const responsiveText = 'text-sm md:text-base lg:text-lg';
const responsiveHidden = 'hidden md:flex'; // Hide on mobile
```
