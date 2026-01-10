# Glassmorphism Class Mapping Guide

Complete reference for mapping HTML prototype classes to production React components.

---

## Core Glass Effects

| HTML Class | React className | Use Case |
|------------|-----------------|----------|
| `glass-card` | `glass-card` | Interactive cards with hover effects |
| `glass-card-static` | `glass-card-static` | Containers and forms (no hover) |
| `glass-header` | `glass-header` | Navigation headers |

**Properties**:
- `backdrop-filter: blur(20px)` - Frosted glass effect
- `background: rgba(255, 255, 255, 0.05)` - Semi-transparent
- `border: 1px solid rgba(255, 255, 255, 0.1)` - Subtle border

---

## Button Variants

| HTML Class | React className | shadcn Component | Use Case |
|------------|-----------------|------------------|----------|
| `btn-glass` | `btn-glass` | `<Button className="btn-glass">` | Secondary actions |
| `btn-primary-glass` | `btn-primary-glass` | `<Button className="btn-primary-glass">` | Primary CTAs |

**Example**:
```tsx
// HTML: <button class="btn-glass">Cancel</button>
// React:
<Button className="btn-glass" onClick={handleCancel}>Cancel</Button>
```

---

## Neon Glow Effects

| HTML Class | React className | Color | Use Case |
|------------|-----------------|-------|----------|
| `neon-glow` | `neon-glow` | Primary (purple) | Default emphasis |
| `neon-glow-purple` | `neon-glow-purple` | Purple (#7877c6) | Primary brand color |
| `neon-glow-pink` | `neon-glow-pink` | Pink (#ff77c6) | Accent elements |
| `neon-glow-cyan` | `neon-glow-cyan` | Cyan (#78dbff) | Info/highlights |
| `neon-glow-green` | `neon-glow-green` | Green | Success states |
| `neon-glow-red` | `neon-glow-red` | Red | Error states |

**Example**:
```tsx
// HTML: <div class="glass-card neon-glow-purple">Content</div>
// React:
<Card className="glass-card neon-glow-purple">
  <CardContent>Content</CardContent>
</Card>
```

---

## Text Effects

| HTML Class | React className | Effect | Use Case |
|------------|-----------------|--------|----------|
| `gradient-text` | `gradient-text` | Animated gradient | Headings, hero titles |
| `text-glow` | `text-glow` | Soft text shadow | Labels, emphasis |
| `icon-glow` | `icon-glow` | Icon drop-shadow | Icons, logos |

**Example**:
```tsx
// HTML: <h1 class="gradient-text">DevPrep AI</h1>
// React:
<h1 className="gradient-text">DevPrep AI</h1>
```

---

## Animation Classes

| HTML Class | React className | Animation | Duration | Use Case |
|------------|-----------------|-----------|----------|----------|
| `fade-in` | `fade-in` | Opacity 0→1 | 600ms | Content reveal |
| `slide-up` | `slide-up` | Translate Y + fade | 600ms | Entry animations |
| `pulse-glow` | `pulse-glow` | Pulsing glow | 2s loop | Call-to-action |

**Example**:
```tsx
// HTML: <div class="glass-card fade-in">Content</div>
// React:
<Card className="glass-card fade-in">
  <CardContent>Content</CardContent>
</Card>
```

---

## Layout Utilities

| HTML Class | React className | Purpose |
|------------|-----------------|---------|
| `container-sm` | `container-sm` | Max-width 640px |
| `container-md` | `container-md` | Max-width 768px |
| `container-lg` | `container-lg` | Max-width 1024px |
| `container-xl` | `container-xl` | Max-width 1280px |

---

## Common Combinations

### Interactive Card with Glow
```tsx
<Card className="glass-card neon-glow-purple fade-in">
  <CardHeader>
    <CardTitle className="text-glow">Title</CardTitle>
  </CardHeader>
  <CardContent>
    <Button className="btn-primary-glass">Action</Button>
  </CardContent>
</Card>
```

### Hero Section
```tsx
<section className="glass-card-static">
  <div className="container-xl">
    <h1 className="gradient-text text-5xl font-bold">
      Hero Title
    </h1>
    <Button className="btn-primary-glass pulse-glow">
      Get Started
    </Button>
  </div>
</section>
```

### Stat Display
```tsx
<Card className="glass-card neon-glow-cyan">
  <CardContent>
    <div className="text-4xl font-bold text-glow">5,000+</div>
    <div className="text-sm text-[rgba(229,229,255,0.7)]">Users</div>
  </CardContent>
</Card>
```

---

## Invalid Classes (Do Not Use)

These are NOT valid DevPrep AI glassmorphism classes:
- ❌ `glass-button` (use `btn-glass`)
- ❌ `glass-container` (use `glass-card-static`)
- ❌ `neon-blue` (use `neon-glow-cyan`)
- ❌ `glass-effect` (use `glass-card`)

**Always validate against**: `frontend/src/styles/glassmorphism.css`
