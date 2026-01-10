# TaskFlow Theme - Industrial-Kinetic Futurism

Adapted from RoboLearn's IFK design system for TaskFlow's task management UI.

## Design Philosophy

**Industrial-Kinetic Futurism (IFK)**: Dark industrial backgrounds with kinetic cyan + amber accents. Feels like a mission control center for human-agent collaboration.

## Color Palette

### Dark Theme (Primary)

```css
/* CSS Variables for globals.css */
:root {
  /* Background Hierarchy */
  --background: 222 15% 8%;        /* #141418 - Deep industrial */
  --background-secondary: 222 11% 11%;  /* #1a1a1e - Elevated surfaces */
  --background-tertiary: 222 8% 14%;    /* #222226 - Cards, inputs */

  /* Foreground/Text */
  --foreground: 0 0% 100%;         /* #ffffff - Primary text */
  --foreground-secondary: 0 0% 72%;     /* #b8b8b8 - Secondary text */
  --foreground-muted: 0 0% 53%;         /* #888888 - Muted text */

  /* Primary: Kinetic Cyan (sensor/HUD feel) */
  --primary: 191 100% 50%;         /* #00d4ff - Main actions */
  --primary-foreground: 222 15% 8%;     /* Dark text on cyan */
  --primary-glow: rgba(0, 212, 255, 0.4);

  /* Secondary: Humanoid Amber (warmth, warnings) */
  --secondary: 35 100% 50%;        /* #ff9500 - Secondary actions */
  --secondary-foreground: 222 15% 8%;
  --secondary-glow: rgba(255, 149, 0, 0.3);

  /* Accent (same as primary for consistency) */
  --accent: 191 100% 50%;
  --accent-foreground: 222 15% 8%;

  /* Status Colors */
  --success: 145 80% 42%;          /* #22c55e - Completed, online */
  --warning: 35 100% 50%;          /* #ff9500 - Amber for warnings */
  --destructive: 0 84% 60%;        /* #ef4444 - Errors, delete */
  --destructive-foreground: 0 0% 100%;

  /* UI Elements */
  --border: 0 0% 100% / 0.1;       /* Subtle borders */
  --input: 222 8% 14%;             /* Input backgrounds */
  --ring: 191 100% 50%;            /* Focus rings - cyan */

  /* Cards & Popovers */
  --card: 222 11% 11%;
  --card-foreground: 0 0% 100%;
  --popover: 222 11% 11%;
  --popover-foreground: 0 0% 100%;

  /* Muted backgrounds */
  --muted: 222 8% 14%;
  --muted-foreground: 0 0% 53%;
}
```

### Light Theme

```css
.light {
  --background: 0 0% 100%;         /* #ffffff */
  --background-secondary: 0 0% 96%;     /* #f5f5f7 */
  --background-tertiary: 0 0% 91%;      /* #e8e8ed */

  --foreground: 0 0% 11%;          /* #1d1d1f */
  --foreground-secondary: 0 0% 32%;     /* #515154 */
  --foreground-muted: 0 0% 53%;         /* #86868b */

  /* Adjusted cyan for light backgrounds */
  --primary: 204 100% 40%;         /* #0077cc */
  --primary-foreground: 0 0% 100%;

  /* Adjusted amber for light backgrounds */
  --secondary: 30 100% 40%;        /* #cc6600 */
  --secondary-foreground: 0 0% 100%;

  --border: 0 0% 0% / 0.1;
  --input: 0 0% 96%;
}
```

## Typography

### Font Stack

```css
:root {
  /* Display: Technical, monospace for headings and labels */
  --font-display: 'JetBrains Mono', 'IBM Plex Mono', 'Courier New', monospace;

  /* Body: Clean, modern sans-serif */
  --font-body: 'Space Grotesk', 'Syne', system-ui, -apple-system, sans-serif;
}
```

### Installation

```bash
# Add to your Next.js project
npm install @fontsource/jetbrains-mono @fontsource/space-grotesk
```

```tsx
// app/layout.tsx
import '@fontsource/jetbrains-mono/400.css'
import '@fontsource/jetbrains-mono/500.css'
import '@fontsource/jetbrains-mono/600.css'
import '@fontsource/space-grotesk/400.css'
import '@fontsource/space-grotesk/500.css'
import '@fontsource/space-grotesk/600.css'
```

### Usage

```tsx
// Headings use display font
<h1 className="font-mono text-2xl font-semibold tracking-tight">
  Task Dashboard
</h1>

// Body text uses sans font
<p className="font-sans text-sm text-muted-foreground">
  Manage tasks across humans and agents
</p>

// Status labels use display font
<span className="font-mono text-xs uppercase tracking-wider text-primary">
  IN PROGRESS
</span>
```

## Tailwind Configuration

```ts
// tailwind.config.ts
import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // IFK Color System
        ifk: {
          cyan: "hsl(191, 100%, 50%)",
          "cyan-light": "hsl(191, 100%, 60%)",
          "cyan-dark": "hsl(191, 100%, 40%)",
          amber: "hsl(35, 100%, 50%)",
          "amber-light": "hsl(35, 100%, 60%)",
          "amber-dark": "hsl(35, 100%, 40%)",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "IBM Plex Mono", "monospace"],
        sans: ["Space Grotesk", "Syne", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in-up": "fadeInUp 0.6s ease forwards",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "scan-line": "scanLine 4s linear infinite",
      },
      keyframes: {
        fadeInUp: {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        scanLine: {
          "0%": { transform: "translateY(-100%)", opacity: "0" },
          "10%": { opacity: "1" },
          "90%": { opacity: "1" },
          "100%": { transform: "translateY(100vh)", opacity: "0" },
        },
      },
      boxShadow: {
        "cyan-glow": "0 0 20px rgba(0, 212, 255, 0.4)",
        "amber-glow": "0 0 20px rgba(255, 149, 0, 0.3)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config
```

## Component Customizations

### Button Variants

```tsx
// components/ui/button.tsx - Add IFK variants
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 font-mono text-sm font-medium uppercase tracking-wider transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-cyan-glow/50",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-white/10 bg-transparent hover:bg-white/5 hover:border-white/20",
        ghost: "hover:bg-accent/10 hover:text-accent",
        link: "text-primary underline-offset-4 hover:underline",
        // IFK-specific variants
        cyan: "bg-ifk-cyan text-background hover:bg-ifk-cyan-light shadow-cyan-glow/30 hover:shadow-cyan-glow",
        amber: "bg-ifk-amber text-background hover:bg-ifk-amber-light shadow-amber-glow/30 hover:shadow-amber-glow",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3",
        lg: "h-12 px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

### Card with Glow Effect

```tsx
// Task card with IFK styling
<Card className="group relative border-white/10 bg-background-secondary transition-all hover:border-primary hover:shadow-cyan-glow/20">
  {/* Accent line on hover */}
  <div className="absolute bottom-0 left-1/2 h-0.5 w-0 -translate-x-1/2 bg-gradient-to-r from-primary to-secondary transition-all group-hover:w-3/5" />

  <CardHeader>
    <div className="flex items-center justify-between">
      <CardTitle className="font-mono text-lg tracking-tight">
        {task.title}
      </CardTitle>
      <Badge variant={getStatusVariant(task.status)}>
        {task.status}
      </Badge>
    </div>
  </CardHeader>
  <CardContent>
    {/* ... */}
  </CardContent>
</Card>
```

### Badge Variants for TaskFlow

```tsx
// components/ui/badge.tsx - Status-specific variants
const badgeVariants = cva(
  "inline-flex items-center rounded px-2 py-0.5 font-mono text-xs font-medium uppercase tracking-wider transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary/20 text-primary border border-primary/30",
        secondary: "bg-secondary/20 text-secondary border border-secondary/30",
        // Task status variants
        pending: "bg-muted text-muted-foreground border border-white/10",
        "in-progress": "bg-primary/20 text-primary border border-primary/30",
        completed: "bg-success/20 text-success border border-success/30",
        blocked: "bg-destructive/20 text-destructive border border-destructive/30",
        // Actor type variants
        human: "bg-amber-500/20 text-amber-400 border border-amber-500/30",
        agent: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)
```

## Layout Patterns

### Dashboard Grid

```tsx
// IFK-styled dashboard layout
<div className="min-h-screen bg-background">
  {/* Grid background pattern */}
  <div
    className="pointer-events-none fixed inset-0 z-0"
    style={{
      backgroundImage: `
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px)
      `,
      backgroundSize: '60px 60px',
      maskImage: 'radial-gradient(ellipse at center, black 30%, transparent 70%)',
    }}
  />

  {/* Content */}
  <div className="relative z-10">
    <SidebarProvider>
      <AppSidebar />
      <main className="flex-1 p-6">
        {children}
      </main>
    </SidebarProvider>
  </div>
</div>
```

### Section Headers

```tsx
// IFK-styled section header
<div className="mb-8 text-center">
  <span className="mb-2 inline-block rounded border border-primary/20 bg-primary/10 px-3 py-1 font-mono text-xs font-semibold uppercase tracking-widest text-primary">
    Active Tasks
  </span>
  <h2 className="font-mono text-2xl font-bold tracking-tight">
    Mission Control
  </h2>
  <p className="mt-2 font-sans text-muted-foreground">
    Monitor and manage task assignments across your team
  </p>
</div>
```

## Status Indicators

### Pulse Dot

```tsx
// Status indicator with pulse animation
<span className="relative flex h-2 w-2">
  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
  <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
</span>
```

### Progress with Glow

```tsx
// Task progress with IFK styling
<div className="space-y-1">
  <div className="flex justify-between font-mono text-xs">
    <span>Progress</span>
    <span className="text-primary">{progress}%</span>
  </div>
  <div className="h-1.5 overflow-hidden rounded-full bg-muted">
    <div
      className="h-full rounded-full bg-gradient-to-r from-primary to-secondary shadow-cyan-glow/50 transition-all"
      style={{ width: `${progress}%` }}
    />
  </div>
</div>
```

## Globals.css Template

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Font imports */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

@layer base {
  :root {
    --background: 222 15% 8%;
    --foreground: 0 0% 100%;
    --card: 222 11% 11%;
    --card-foreground: 0 0% 100%;
    --popover: 222 11% 11%;
    --popover-foreground: 0 0% 100%;
    --primary: 191 100% 50%;
    --primary-foreground: 222 15% 8%;
    --secondary: 35 100% 50%;
    --secondary-foreground: 222 15% 8%;
    --muted: 222 8% 14%;
    --muted-foreground: 0 0% 53%;
    --accent: 191 100% 50%;
    --accent-foreground: 222 15% 8%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;
    --border: 0 0% 100% / 0.1;
    --input: 222 8% 14%;
    --ring: 191 100% 50%;
    --radius: 0.5rem;

    /* Success green */
    --success: 145 80% 42%;
  }

  .light {
    --background: 0 0% 100%;
    --foreground: 0 0% 11%;
    --card: 0 0% 96%;
    --card-foreground: 0 0% 11%;
    --popover: 0 0% 100%;
    --popover-foreground: 0 0% 11%;
    --primary: 204 100% 40%;
    --primary-foreground: 0 0% 100%;
    --secondary: 30 100% 40%;
    --secondary-foreground: 0 0% 100%;
    --muted: 0 0% 96%;
    --muted-foreground: 0 0% 45%;
    --accent: 204 100% 40%;
    --accent-foreground: 0 0% 100%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;
    --border: 0 0% 0% / 0.1;
    --input: 0 0% 96%;
    --ring: 204 100% 40%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground font-sans antialiased;
  }
  h1, h2, h3, h4, h5, h6 {
    @apply font-mono tracking-tight;
  }
}

/* Custom scrollbar for dark theme */
@layer utilities {
  .scrollbar-thin {
    scrollbar-width: thin;
    scrollbar-color: hsl(var(--primary) / 0.2) transparent;
  }

  .scrollbar-thin::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  .scrollbar-thin::-webkit-scrollbar-track {
    background: transparent;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb {
    background: hsl(var(--primary) / 0.2);
    border-radius: 3px;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: hsl(var(--primary) / 0.35);
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Quick Reference

| Element | Dark Theme | Light Theme |
|---------|------------|-------------|
| Background | `#141418` | `#ffffff` |
| Surface | `#1a1a1e` | `#f5f5f7` |
| Primary (Cyan) | `#00d4ff` | `#0077cc` |
| Secondary (Amber) | `#ff9500` | `#cc6600` |
| Success | `#22c55e` | `#22c55e` |
| Text Primary | `#ffffff` | `#1d1d1f` |
| Text Muted | `#888888` | `#86868b` |
| Border | `rgba(255,255,255,0.1)` | `rgba(0,0,0,0.1)` |

## Actor Type Styling

```tsx
// Human vs Agent visual distinction
const actorStyles = {
  human: {
    badge: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    icon: "text-amber-400",
    glow: "shadow-amber-glow",
  },
  agent: {
    badge: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
    icon: "text-cyan-400",
    glow: "shadow-cyan-glow",
  },
}

// Usage
<div className={cn("flex items-center gap-2", actorStyles[actorType].glow)}>
  {actorType === "agent" ? <Bot className={actorStyles.agent.icon} /> : <User className={actorStyles.human.icon} />}
  <Badge className={actorStyles[actorType].badge}>
    @{name}
  </Badge>
</div>
```