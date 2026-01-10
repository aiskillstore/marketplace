# Frontend Anti-Patterns (The "AI Slop" Catalog)

This document catalogs common AI-generated design patterns that make interfaces immediately recognizable as machine-generated. **Avoid all of these.**

## Typography Anti-Patterns

### Generic Font Stack
```css
/* BAD - Immediately recognizable as AI-generated */
font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* GOOD - Distinctive, branded */
font-family: 'Plus Jakarta Sans', 'Inter Variable', sans-serif;
```

### Weak Weight Contrast
```typescript
// BAD - Minimal visual hierarchy
<h1 className="text-xl font-semibold">Title</h1>      // 600
<p className="text-base font-medium">Body</p>         // 500

// GOOD - Clear hierarchy through weight
<h1 className="text-4xl font-black">Title</h1>        // 900
<p className="text-base font-normal">Body</p>         // 400
```

### Inconsistent Size Scale
```typescript
// BAD - Random sizes, no system
<h1 className="text-2xl">Main</h1>    // 24px
<h2 className="text-xl">Sub</h2>      // 20px - too close
<h3 className="text-lg">Minor</h3>    // 18px - too close

// GOOD - Clear typographic scale
<h1 className="text-5xl">Main</h1>    // 48px
<h2 className="text-3xl">Sub</h2>     // 30px - clear step
<h3 className="text-xl">Minor</h3>    // 20px - clear step
```

## Color Anti-Patterns

### Gray Instead of True Dark
```typescript
// BAD - Gray dark mode (common AI default)
<div className="bg-gray-900">              // #111827 - gray tint
<div className="bg-slate-900">             // #0f172a - blue tint
<div className="bg-zinc-900">              // #18181b - still gray

// GOOD - True dark (pick based on your brand)
<div className="bg-neutral-950">           // Closest Tailwind to true dark
<div className="bg-black">                 // Pure black
<div className="bg-[var(--bg-base)]">      // Custom CSS variable
```

### Purple/Blue Gradient Overuse
```typescript
// BAD - The AI gradient cliche
<div className="bg-gradient-to-r from-purple-500 to-blue-500">

// BAD - Gradient backgrounds everywhere
<Button className="bg-gradient-to-r from-violet-600 to-indigo-600">

// GOOD - Solid colors with subtle depth
<Button className="bg-violet-500 hover:bg-violet-400 shadow-lg shadow-violet-500/20">
```

### Rainbow Distribution
```typescript
// BAD - Every element a different color
<Badge className="bg-blue-500">Users</Badge>
<Badge className="bg-green-500">Active</Badge>
<Badge className="bg-yellow-500">Pending</Badge>
<Badge className="bg-red-500">Errors</Badge>
<Badge className="bg-purple-500">System</Badge>

// GOOD - Semantic color usage (brand + semantic only)
<Badge className="bg-brand-500/10 text-brand-400">Primary</Badge>
<Badge className="bg-green-500/10 text-green-400">Success</Badge>
<Badge className="bg-red-500/10 text-red-400">Error</Badge>
```

### Low Contrast Text
```typescript
// BAD - Hard to read
<p className="text-gray-400">Important info</p>      // Too light
<p className="text-zinc-600">On dark bg</p>          // Invisible

// GOOD - Accessible contrast
<p className="text-zinc-100">Primary text</p>        // High contrast
<p className="text-zinc-400">Secondary text</p>      // Still readable
```

## Layout Anti-Patterns

### Excessive Rounded Corners
```typescript
// BAD - Everything is pill-shaped
<Card className="rounded-full">
<Button className="rounded-full">
<Avatar className="rounded-full">
<Input className="rounded-full">

// GOOD - Mix of shapes for hierarchy
<Card className="rounded-xl">           // Large elements
<Button className="rounded-lg">         // Interactive
<Avatar className="rounded-full">       // Only avatars
<Input className="rounded-md">          // Form elements
```

### Centered Everything
```typescript
// BAD - No visual tension
<div className="flex flex-col items-center justify-center text-center">
  <h1>Title</h1>
  <p>Description</p>
  <Button>Action</Button>
</div>

// GOOD - Asymmetry creates interest
<div className="flex flex-col items-start">
  <h1 className="text-left">Title</h1>
  <p className="text-left max-w-md">Description</p>
  <Button className="mt-4">Action</Button>
</div>
```

### Card Soup
```typescript
// BAD - Grid of identical cards with no hierarchy
<div className="grid grid-cols-3 gap-4">
  <Card>Item 1</Card>
  <Card>Item 2</Card>
  <Card>Item 3</Card>
  <Card>Item 4</Card>
  <Card>Item 5</Card>
  <Card>Item 6</Card>
</div>

// GOOD - Visual hierarchy with featured items
<div className="grid grid-cols-3 gap-4">
  <Card className="col-span-2 row-span-2 bg-violet-500/5 border-violet-500/20">
    Featured Item
  </Card>
  <Card>Item 2</Card>
  <Card>Item 3</Card>
  <Card>Item 4</Card>
</div>
```

## Animation Anti-Patterns

### No Animation (Static Pages)
```typescript
// BAD - Lifeless, static
<div>{items.map(item => <Card>{item}</Card>)}</div>

// GOOD - Staggered reveal
<motion.div variants={container} initial="hidden" animate="show">
  {items.map((item, i) => (
    <motion.div key={i} variants={item}>{item}</motion.div>
  ))}
</motion.div>
```

### Bounce Overuse
```typescript
// BAD - Childish, unprofessional
<Button className="animate-bounce">Click me!</Button>
<Icon className="animate-bounce" />

// GOOD - Subtle, purposeful motion
<Button className="transition-transform hover:scale-105">Click me</Button>
<Icon className="transition-opacity hover:opacity-80" />
```

### Jarring Transitions
```typescript
// BAD - No easing, feels mechanical
<div className="transition-all duration-100">
<div className="transition-none">

// GOOD - Smooth, natural easing
<div className="transition-all duration-200 ease-out">
<div className="transition-all duration-300 ease-in-out">
```

## Background Anti-Patterns

### Flat Solid Backgrounds
```typescript
// BAD - No depth, flat
<div className="bg-black">
<main className="bg-gray-900">

// GOOD - Atmospheric depth (use your brand color)
<div className="relative bg-neutral-950">
  <div className="absolute inset-0 bg-gradient-to-b from-brand-500/5 to-transparent" />
  <div className="relative z-10">{children}</div>
</div>
```

### Heavy Patterns
```typescript
// BAD - Distracting, busy
<div className="bg-[url('/noise.png')] opacity-50">
<div className="bg-[repeating-linear-gradient(45deg,#000,#000_10px,#111_10px,#111_20px)]">

// GOOD - Subtle, atmospheric
<div className="bg-[linear-gradient(to_right,#1f1f1f_1px,transparent_1px)] bg-[size:64px]">
```

### White Cards on Dark
```typescript
// BAD - Jarring contrast
<div className="bg-black">
  <Card className="bg-white text-black">Content</Card>
</div>

// GOOD - Subtle elevation
<div className="bg-neutral-950">
  <Card className="bg-neutral-900 border border-white/5">Content</Card>
</div>
```

## Icon Anti-Patterns

### Inconsistent Stroke Weights
```typescript
// BAD - Mixed icon styles
<HeroiconOutline />  // 1.5px stroke
<LucideIcon />       // 2px stroke
<FeatherIcon />      // 2px stroke
<FontAwesome />      // Solid fill

// GOOD - Consistent icon family
import { Home, Settings, User, Bell } from 'lucide-react'

// All Lucide with consistent 2px stroke
<Home className="w-5 h-5" strokeWidth={2} />
<Settings className="w-5 h-5" strokeWidth={2} />
```

### Colorful Icons
```typescript
// BAD - Rainbow icons
<HomeIcon className="text-blue-500" />
<SettingsIcon className="text-green-500" />
<UserIcon className="text-purple-500" />

// GOOD - Consistent, muted icons
<HomeIcon className="text-zinc-400" />
<SettingsIcon className="text-zinc-400" />
<UserIcon className="text-zinc-400" />

// Accent only for active/important
<BellIcon className="text-violet-400" />  // Notifications active
```

## Button Anti-Patterns

### Gradient Buttons
```typescript
// BAD - Gradient overload
<Button className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600">
  Submit
</Button>

// GOOD - Clean, solid
<Button className="bg-violet-500 hover:bg-violet-400">
  Submit
</Button>
```

### Multiple Primary Buttons
```typescript
// BAD - No clear hierarchy
<div className="flex gap-2">
  <Button variant="default">Save</Button>
  <Button variant="default">Publish</Button>
  <Button variant="default">Share</Button>
</div>

// GOOD - Clear primary action
<div className="flex gap-2">
  <Button variant="default">Publish</Button>
  <Button variant="outline">Save Draft</Button>
  <Button variant="ghost">Share</Button>
</div>
```

## Form Anti-Patterns

### Floating Labels Only
```typescript
// BAD - Confusing when filled
<Input placeholder="Email" />  // Label disappears

// GOOD - Persistent labels
<div>
  <Label>Email</Label>
  <Input placeholder="you@example.com" />
</div>
```

### Generic Validation Messages
```typescript
// BAD - Unhelpful errors
<FormMessage>Invalid input</FormMessage>
<FormMessage>Error</FormMessage>

// GOOD - Specific, actionable
<FormMessage>Email must include @ symbol</FormMessage>
<FormMessage>Password needs at least 8 characters</FormMessage>
```

## Quick Reference: What To Avoid

| Category | Avoid | Use Instead |
|----------|-------|-------------|
| Fonts | Inter, Roboto, Arial | Plus Jakarta Sans, Bricolage Grotesque, etc. |
| Dark BG | `gray-900`, `slate-900` | `neutral-950` or custom true dark |
| Accents | Purple/blue gradients | Single solid brand color |
| Corners | `rounded-full` everywhere | Mix of `rounded-xl`, `rounded-lg` |
| Motion | None or bounce | Subtle ease-out transitions |
| Icons | Mixed families | Lucide with consistent stroke |
| Cards | White on dark | Subtle elevation with white/5 border |
| Buttons | Gradients, multiple primaries | Solid colors, clear hierarchy |
