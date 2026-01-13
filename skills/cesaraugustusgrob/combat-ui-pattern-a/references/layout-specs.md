# Layout Specifications - Pattern A Split-Panel Combat UI

## CSS Grid Structure

### CombatLayout Grid Definition

```typescript
// CombatLayout.tsx
<div className="
  h-screen w-full
  grid
  grid-rows-[auto_1fr_auto]
  grid-cols-1
  bg-zinc-950
">
  {/* Row 1: PhaseHeader */}
  {/* Row 2: ConfrontationZone */}
  {/* Row 3: ActionDock */}
</div>
```

### Grid Template

```css
.combat-layout {
  display: grid;
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 1fr;
  height: 100vh;
  height: 100dvh; /* Dynamic viewport for mobile */
  width: 100%;
  background: #09090b; /* zinc-950 */
}
```

### Row Specifications

| Row | Content | Height | Behavior |
|-----|---------|--------|----------|
| 1 | PhaseHeader | `auto` (~48-56px) | Fixed content height |
| 2 | ConfrontationZone | `1fr` | Fills remaining space |
| 3 | ActionDock | `auto` (~180-220px) | Content-based height |

---

## ConfrontationZone Layout

### Two-Column Split

```typescript
// ConfrontationZone.tsx
<div className="
  w-full h-full
  grid
  grid-cols-[1fr_auto_1fr]
  gap-0
  px-4
  py-4
">
  {/* Col 1: PlayerPanel */}
  {/* Col 2: VSDivider */}
  {/* Col 3: EnemyPanel */}
</div>
```

### Column Specifications

| Column | Content | Width | Notes |
|--------|---------|-------|-------|
| 1 | CharacterPanel (player) | `1fr` | Equal to enemy |
| 2 | VSDivider | `auto` (~80-120px) | Fixed emblem width |
| 3 | CharacterPanel (enemy) | `1fr` | Equal to player |

### Mobile Fallback (< 768px)

```typescript
// Responsive: Stack vertically on mobile
<div className="
  grid
  grid-cols-1 md:grid-cols-[1fr_auto_1fr]
  grid-rows-[1fr_auto_1fr] md:grid-rows-1
">
```

---

## CharacterPanel Layout

### Internal Structure

```typescript
// CharacterPanel.tsx
<div className="
  h-full
  flex flex-col
  justify-between
  p-4
">
  {/* Top: Character Sprite (flex-1) */}
  <div className="flex-1 flex items-center justify-center">
    <CharacterSprite />
  </div>

  {/* Bottom: Stats Panel (auto) */}
  <div className="mt-4">
    <IdentityBar />
    <ResourceBars />
    <BuffBar />
  </div>
</div>
```

### Player Panel (Left) Alignment

```typescript
// Player faces RIGHT → content aligned LEFT
<div className="
  flex flex-col
  items-start        // Align to left
  text-left
">
```

### Enemy Panel (Right) Alignment

```typescript
// Enemy faces LEFT → content aligned RIGHT
<div className="
  flex flex-col
  items-end          // Align to right
  text-right
">
```

### Sprite Container Dimensions

```typescript
// Responsive sprite sizing
<div className="
  w-full
  max-w-[280px] md:max-w-[320px] lg:max-w-[400px]
  aspect-[3/4]       // Portrait orientation
  relative
">
  <img className="object-contain w-full h-full" />
</div>
```

---

## ActionDock Layout

### Two-Section Split

```typescript
// ActionDock.tsx
<div className="
  w-full
  bg-zinc-900/95
  border-t border-zinc-700
  px-4 py-3
">
  {/* Skills Container */}
  <div className="
    flex
    flex-col md:flex-row
    gap-4
    max-w-6xl mx-auto
  ">
    {/* Quick Actions Section */}
    <div className="flex-shrink-0">
      <QuickActionsSection />
    </div>

    {/* Main Actions Section */}
    <div className="flex-1">
      <MainActionsSection />
    </div>
  </div>

  {/* Control Buttons */}
  <div className="flex justify-end gap-2 mt-3">
    <AutoCombatButton />
    <EndTurnButton />
  </div>
</div>
```

### Quick Actions Grid

```typescript
// 4-6 compact cards in a row
<div className="
  grid
  grid-cols-4 sm:grid-cols-6
  gap-2
">
  {sideSkills.map(skill => <QuickActionCard />)}
  {toggleSkills.map(skill => <QuickActionCard />)}
</div>
```

### Main Actions Grid

```typescript
// 2-4 large cards
<div className="
  grid
  grid-cols-2 md:grid-cols-3 lg:grid-cols-4
  gap-3 md:gap-4
">
  {mainSkills.map(skill => <MainActionCard />)}
</div>
```

---

## PhaseHeader Layout

### Horizontal Strip

```typescript
// PhaseHeader.tsx
<div className="
  w-full
  h-12 md:h-14
  bg-zinc-900/90
  border-b border-zinc-700
  px-4
  flex items-center justify-between
">
  {/* Left: Turn Info */}
  <div className="flex items-center gap-4">
    <TurnCounter />
    <CurrentActor />
  </div>

  {/* Center: Phase Pipeline */}
  <div className="hidden md:flex">
    <PhasePipeline />
  </div>

  {/* Right: Modifiers */}
  <div className="flex items-center gap-4">
    <SideActionCounter />
    <ApproachBadge />
  </div>
</div>
```

---

## VSDivider Layout

### Center Column

```typescript
// VSDivider.tsx
<div className="
  w-20 md:w-24 lg:w-28
  h-full
  flex flex-col
  items-center justify-center
  relative
">
  {/* Vertical Line (Top) */}
  <div className="
    w-px h-1/3
    bg-gradient-to-b from-transparent to-amber-500/50
  " />

  {/* VS Emblem */}
  <div className="
    w-16 h-16 md:w-20 md:h-20
    flex items-center justify-center
    relative
  ">
    <span className="text-2xl md:text-3xl font-black text-amber-500">
      VS
    </span>
    {/* Crossed kunai behind */}
    <KunaiCrossed className="absolute inset-0 opacity-30" />
  </div>

  {/* Vertical Line (Bottom) */}
  <div className="
    w-px h-1/3
    bg-gradient-to-t from-transparent to-amber-500/50
  " />

  {/* Clash Effect */}
  <ClashEffect className="absolute inset-0 pointer-events-none" />
</div>
```

---

## Responsive Breakpoints

### Breakpoint Definitions

| Breakpoint | Width | Layout Mode |
|------------|-------|-------------|
| `base` | < 640px | Mobile (stacked) |
| `sm` | 640px+ | Small tablet |
| `md` | 768px+ | Tablet (split begins) |
| `lg` | 1024px+ | Desktop (full split) |
| `xl` | 1280px+ | Large desktop |

### Layout Changes by Breakpoint

```typescript
// Mobile (< 768px): Vertical stack fallback
grid-cols-1
grid-rows-[1fr_auto_1fr]

// Tablet+ (768px+): Horizontal split
md:grid-cols-[1fr_auto_1fr]
md:grid-rows-1

// Desktop (1024px+): Full experience
lg:gap-6
lg:px-8
```

### Component Visibility

| Component | Mobile | Tablet | Desktop |
|-----------|--------|--------|---------|
| PhaseHeader | Compact | Standard | Full |
| PhasePipeline | Hidden | Visible | Full icons |
| VSDivider | Horizontal | Vertical | Full FX |
| QuickActions | 4 cols | 5 cols | 6 cols |
| MainActions | 2 cols | 3 cols | 4 cols |

---

## Z-Index Stack

```typescript
const Z_INDEX = {
  base: 0,           // CombatLayout
  panels: 10,        // CharacterPanels
  vsDivider: 15,     // VSDivider
  actionDock: 20,    // ActionDock
  tooltips: 30,      // Tooltip portals
  floatingText: 50,  // Damage numbers
  modals: 100,       // Any modals
};
```

---

## Spacing Tokens

```typescript
const SPACING = {
  // Padding
  panelPadding: 'p-4',           // 16px
  dockPadding: 'px-4 py-3',      // 16px x, 12px y
  headerPadding: 'px-4',         // 16px

  // Gaps
  sectionGap: 'gap-4',           // 16px
  cardGap: 'gap-2',              // 8px (quick actions)
  mainCardGap: 'gap-3 md:gap-4', // 12-16px

  // Margins
  statsMargin: 'mt-4',           // 16px
  controlsMargin: 'mt-3',        // 12px
};
```

---

## Container Constraints

```typescript
const CONSTRAINTS = {
  // Max widths
  maxLayoutWidth: 'max-w-7xl',    // 1280px
  maxDockWidth: 'max-w-6xl',      // 1152px
  maxPanelWidth: 'max-w-[400px]', // 400px per panel

  // Min heights
  minPanelHeight: 'min-h-[300px]',
  minDockHeight: 'min-h-[180px]',

  // Aspect ratios
  spriteAspect: 'aspect-[3/4]',   // Portrait
  quickCardAspect: 'aspect-square', // 1:1
  mainCardAspect: 'aspect-[7/5]',  // Landscape
};
```
