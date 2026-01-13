---
name: frontend-aesthetics
description: Use when creating UI designs to avoid generic "AI slop" aesthetics. Enforces distinctive typography, cohesive color systems, purposeful motion, and atmospheric backgrounds. Critical for landing pages, dashboards, and branded interfaces.
allowed-tools: Read, Grep, Glob
---

# Frontend Aesthetics Skill

## When to Use

**ALWAYS use this skill when:**
- Creating landing pages or marketing sites
- Designing dashboards or admin interfaces
- Building branded UI components
- Reviewing designs for distinctiveness
- Implementing visual polish and animations

**DO NOT use when:**
- Working on backend/API code
- Writing tests
- Quick prototypes that won't ship

## The Problem: Distributional Convergence

Claude defaults to generic designs because safe, universally-acceptable choices dominate training data. This creates the "AI slop aesthetic":
- Inter/Roboto fonts everywhere
- Purple/blue gradients
- Minimal animations
- Flat, lifeless backgrounds
- Evenly-distributed color palettes

**This skill provides specific alternatives to break free from defaults.**

## Core Principles

- **True dark themes** (not gray - actual dark tones)
- **Single accent color** - pick one and use it consistently
- **Professional, actionable UI** - data-dense, not decorative
- **Subtle depth** - layered backgrounds, not flat

## Four Design Vectors

### 1. Typography

**Avoid:** Inter, Roboto, Arial as PRIMARY fonts (they're fine as fallbacks)

**Distinctive Alternatives:**
```css
/* Headings: Bold, distinctive */
--font-heading: 'Plus Jakarta Sans', 'Bricolage Grotesque', sans-serif;

/* Body: Clean, readable */
--font-body: 'Inter Variable', system-ui;

/* Code/Data: Monospace with character */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Other distinctive options */
/* Modern/Tech: Space Grotesk, Outfit, Manrope */
/* Premium: Playfair Display, Cormorant */
/* Friendly: Nunito, Quicksand, Poppins */
```

**Weight Contrasts:**
```typescript
// DO: Extreme weight variation
<h1 className="text-4xl font-black">Dashboard</h1>  // 900
<p className="text-base font-light">Subtitle</p>    // 300

// DON'T: Minimal variation
<h1 className="text-2xl font-semibold">Dashboard</h1>  // 600
<p className="text-base font-medium">Subtitle</p>      // 500
```

**Size Hierarchy:**
```typescript
// DO: Clear visual hierarchy
<h1 className="text-5xl">Main Heading</h1>   // 48px
<h2 className="text-2xl">Section</h2>        // 24px
<p className="text-sm">Body text</p>         // 14px

// DON'T: Unclear hierarchy
<h1 className="text-xl">Main Heading</h1>    // Too small
<h2 className="text-lg">Section</h2>         // Too similar
```

### 2. Color System

**Principles:**
- **True dark base** - Use near-black, not gray (avoid gray-900, slate-900)
- **Single accent color** - Pick ONE brand color for primary actions
- **Semantic colors** - Green=success, Amber=warning, Red=error
- **Text hierarchy** - Primary (bright), secondary (muted), disabled (dim)

**Color Application:**
```typescript
// DO: Dominant background + single accent
<div className="bg-neutral-950">
  <Button className="bg-brand-500 hover:bg-brand-400">
    Primary Action
  </Button>
</div>

// DON'T: Evenly distributed colors (rainbow soup)
<div className="bg-gray-900">
  <Button className="bg-blue-500">Action 1</Button>
  <Button className="bg-green-500">Action 2</Button>
  <Button className="bg-purple-500">Action 3</Button>
</div>

// DO: Define CSS variables for your brand
:root {
  --bg-base: /* your true dark */;
  --bg-surface: /* slightly lighter */;
  --accent: /* your brand color */;
  --accent-hover: /* lighter variant */;
}
```

### 3. Motion & Animation

**Principles:**
- Use CSS for simple transitions
- Use Framer Motion for orchestrated animations
- Focus on high-impact moments (page load, state changes)
- Stagger reveals for lists

**CSS-Only Patterns:**
```typescript
// DO: Smooth, purposeful transitions
<Button className="transition-all duration-200 ease-out hover:scale-105 hover:shadow-lg hover:shadow-brand-500/20">
  Hover Me
</Button>

// DO: Staggered list reveals
<div className="animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100">
  Item 1
</div>
<div className="animate-in fade-in slide-in-from-bottom-4 duration-500 delay-200">
  Item 2
</div>
```

**Framer Motion Patterns:**
```typescript
import { motion } from 'framer-motion'

// DO: Orchestrated page load
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

<motion.div variants={container} initial="hidden" animate="show">
  {items.map(i => (
    <motion.div key={i} variants={item}>{i}</motion.div>
  ))}
</motion.div>

// DON'T: Static, lifeless pages
<div>{items.map(i => <div key={i}>{i}</div>)}</div>
```

### 4. Backgrounds & Depth

**Avoid:** Solid colors, flat backgrounds

**Patterns:**
```typescript
// DO: Layered gradients with atmospheric depth
<div className="relative bg-neutral-950">
  {/* Gradient orb using brand color */}
  <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl" />

  {/* Secondary subtle orb */}
  <div className="absolute bottom-0 left-0 w-64 h-64 bg-brand-500/5 rounded-full blur-2xl" />

  {/* Content */}
  <div className="relative z-10">
    {children}
  </div>
</div>

// DO: Subtle grid patterns
<div className="bg-neutral-950 bg-[linear-gradient(to_right,rgb(255_255_255/5%)_1px,transparent_1px),linear-gradient(to_bottom,rgb(255_255_255/5%)_1px,transparent_1px)] bg-[size:64px_64px]">
  {children}
</div>

// DO: Card elevation with glow
<Card className="bg-neutral-900 border border-white/5 shadow-xl shadow-black/50 hover:shadow-brand-500/10 transition-shadow">
  {content}
</Card>
```

## Anti-Patterns (The "Slop" List)

**NEVER do these:**

| Anti-Pattern | Why It's Bad | What To Do Instead |
|--------------|--------------|-------------------|
| Inter font everywhere | Generic, immediately recognizable as AI | Use distinctive fonts (Plus Jakarta Sans, etc.) |
| `bg-gray-900` | Gray, not true dark | Use `bg-neutral-950` or custom true dark |
| Purple/blue gradients | Overused AI aesthetic | Use single brand accent, solid colors |
| Equal color distribution | No visual hierarchy | Dominant color + one accent |
| No animations | Lifeless, static | Add purposeful micro-interactions |
| Rounded-full everywhere | Childish, unprofessional | Mix rounded-lg with sharp corners |
| White cards on dark bg | Too much contrast | Use subtle elevation with soft borders |
| Generic icons | No brand identity | Use Lucide with consistent stroke width |

## Component Styling Examples

### Dashboard Card
```typescript
// Professional dashboard style (use your brand color for accent)
<Card className="bg-neutral-900 border border-white/5 rounded-xl p-6 hover:border-brand-500/20 transition-colors">
  <CardHeader className="pb-2">
    <CardTitle className="text-lg font-semibold text-white flex items-center gap-2">
      <Activity className="w-5 h-5 text-brand-400" />
      System Status
    </CardTitle>
  </CardHeader>
  <CardContent>
    <div className="text-3xl font-bold text-white">98.7%</div>
    <p className="text-sm text-zinc-400">Uptime this month</p>
  </CardContent>
</Card>
```

### Button Hierarchy
```typescript
// Primary - brand color, prominent
<Button className="bg-brand-500 hover:bg-brand-400 text-white font-medium">
  Create Project
</Button>

// Secondary - ghost with border
<Button variant="outline" className="border-white/10 hover:bg-white/5 text-zinc-300">
  Cancel
</Button>

// Destructive - red, serious (semantic color)
<Button variant="destructive" className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20">
  Delete
</Button>
```

### Data Table
```typescript
// Professional data display
<Table className="bg-neutral-900 rounded-xl border border-white/5">
  <TableHeader>
    <TableRow className="border-white/5 hover:bg-white/5">
      <TableHead className="text-zinc-400 font-medium">Project</TableHead>
      <TableHead className="text-zinc-400 font-medium">Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow className="border-white/5 hover:bg-white/5">
      <TableCell className="text-white font-medium">My Project</TableCell>
      <TableCell>
        <Badge className="bg-green-500/10 text-green-400 border-green-500/20">
          Active
        </Badge>
      </TableCell>
    </TableRow>
  </TableBody>
</Table>
```

## Validation Checklist

Before completing any UI work, verify:

- [ ] **Typography**: Not using Inter/Roboto as primary font
- [ ] **Colors**: Using true dark, not gray (gray-900, slate-900)
- [ ] **Accents**: Single brand color used consistently for actions
- [ ] **Motion**: Page has at least one meaningful animation
- [ ] **Depth**: Background has gradients or patterns, not flat
- [ ] **Hierarchy**: Clear visual weight differences (text, buttons)
- [ ] **Consistency**: All components follow established design system

## Supporting Files

- `typography-guide.md` - Complete font pairing reference
- `motion-patterns.md` - Framer Motion recipes and CSS animations
- `anti-patterns.md` - Expanded examples of what to avoid

## Design Token Standard

This skill aligns with **DTCG 2025.10** (Design Tokens Community Group) format:
- File extension: `.tokens.json`
- Properties prefixed with `$` (`$value`, `$type`, `$description`)
- Three-tier architecture: Core → Semantic → Component

See [W3C DTCG Specification](https://www.designtokens.org/tr/drafts/format/)

## Resources

- [W3C Design Tokens Spec](https://www.designtokens.org/) - Industry standard (2025.10)
- [Style Dictionary](https://styledictionary.com/) - Token build system
- [ShadCN UI Components](https://ui.shadcn.com)
- [Framer Motion](https://www.framer.com/motion/)
- [Tailwind CSS](https://tailwindcss.com)
- [Google Fonts](https://fonts.google.com) - For distinctive typography
