---
name: combat-ui-pattern-a
description: Implement Split-Panel Combat UI (Pattern A) for SHINOBI WAY game. Use when user wants to create the horizontal confrontation combat layout, character panels, action dock, phase header, VS divider, or any component from the Pattern A combat UI system. Guides through component creation following the established architecture.
---

# Combat UI Pattern A - Split-Panel Implementation

This skill guides implementation of the Split-Panel Combat UI, transforming the vertical theater mode into a horizontal confrontation layout.

## Architecture Overview

```
┌───────────────────────────────────────────────────┐
│  TURN INDICATOR  │  PHASE PIPELINE  │  MODIFIERS  │  ← PhaseHeader
├──────────────────┴───────┬───────────┴────────────┤
│                          │                        │
│     PLAYER PANEL         │     ENEMY PANEL        │  ← ConfrontationZone
│     (CharacterPanel)     │     (CharacterPanel)   │
│                          │                        │
├──────────────────────────┴────────────────────────┤
│  QUICK ACTIONS (SIDE/TOGGLE)  │   MAIN ACTIONS    │  ← ActionDock
└───────────────────────────────┴───────────────────┘
```

## Component Hierarchy

```
Combat.tsx (scene orchestrator)
├── CombatLayout.tsx (CSS Grid container)
│   ├── PhaseHeader.tsx (top status bar)
│   │   ├── TurnIndicator
│   │   ├── PhasePipeline
│   │   ├── SideActionCounter
│   │   └── ApproachModifier
│   │
│   ├── ConfrontationZone.tsx (battle area)
│   │   ├── CharacterPanel.tsx (player variant)
│   │   │   ├── CharacterSprite
│   │   │   ├── IdentityBar
│   │   │   ├── ResourceBars (HP/CP)
│   │   │   └── BuffBar
│   │   │
│   │   ├── VSDivider.tsx (center emblem)
│   │   │
│   │   └── CharacterPanel.tsx (enemy variant)
│   │       ├── CharacterSprite
│   │       ├── IdentityBar (name, tier, element)
│   │       ├── HealthBar
│   │       ├── DefenseStats
│   │       └── BuffBar
│   │
│   └── ActionDock.tsx (skill bar)
│       ├── QuickActionsSection
│       │   ├── QuickActionCard (SIDE skills)
│       │   └── QuickActionCard (TOGGLE skills)
│       ├── MainActionsSection
│       │   └── MainActionCard (MAIN skills)
│       └── ControlButtons (Auto, End Turn)
│
└── FloatingTextLayer (z-50, unchanged)
```

## File Structure

```
src/components/combat/
├── index.ts                  # Barrel exports
├── CombatLayout.tsx          # Grid container
├── PhaseHeader.tsx           # Top status bar
├── ConfrontationZone.tsx     # Player vs Enemy area
├── CharacterPanel.tsx        # Reusable character display
├── VSDivider.tsx             # Center VS emblem
├── ActionDock.tsx            # Bottom skill bar
├── QuickActionCard.tsx       # Compact SIDE/TOGGLE card
└── MainActionCard.tsx        # Large MAIN skill card
```

## Implementation Workflow

### Step 1: Identify Target Component

Ask user which component to implement:

1. **CombatLayout** - Start here for new implementation
2. **PhaseHeader** - Top status bar
3. **ConfrontationZone** - Battle area with both panels
4. **CharacterPanel** - Individual character display
5. **VSDivider** - Center emblem and effects
6. **ActionDock** - Bottom skill bar
7. **QuickActionCard** - Compact skill card variant
8. **MainActionCard** - Large skill card variant

### Step 2: Load Component Reference

Based on selection, load the appropriate reference:

- **Layout/Structure**: See [layout-specs.md](references/layout-specs.md)
- **Component Props**: See [component-interfaces.md](references/component-interfaces.md)
- **Styling Guide**: See [styling-tokens.md](references/styling-tokens.md)
- **Animation Specs**: See [animations.md](references/animations.md)

### Step 3: Generate Component Code

Follow the component template pattern:

```typescript
import React from 'react';
import { cn } from '@/lib/utils'; // if using cn utility

interface ComponentNameProps {
  // Props from component-interfaces.md
}

export const ComponentName: React.FC<ComponentNameProps> = ({
  // destructured props
}) => {
  return (
    <div className={cn(
      // Base styles from styling-tokens.md
      // Conditional styles
    )}>
      {/* Component content */}
    </div>
  );
};
```

### Step 4: Wire to Combat.tsx

After component creation:

1. Export from `components/combat/index.ts`
2. Import in `Combat.tsx`
3. Replace corresponding section
4. Pass required props from existing state

## Quick Implementation Commands

### Create All Files (Scaffolding)

```bash
# Create directory
mkdir -p src/components/combat

# Create all component files
touch src/components/combat/{index,CombatLayout,PhaseHeader,ConfrontationZone,CharacterPanel,VSDivider,ActionDock,QuickActionCard,MainActionCard}.tsx
```

### Barrel Export Template

```typescript
// src/components/combat/index.ts
export { CombatLayout } from './CombatLayout';
export { PhaseHeader } from './PhaseHeader';
export { ConfrontationZone } from './ConfrontationZone';
export { CharacterPanel } from './CharacterPanel';
export { VSDivider } from './VSDivider';
export { ActionDock } from './ActionDock';
export { QuickActionCard } from './QuickActionCard';
export { MainActionCard } from './MainActionCard';
```

## Props Mapping from Existing Code

### From App.tsx → Combat.tsx (unchanged)

```typescript
player: Player
enemy: Enemy
turnState: 'PLAYER' | 'ENEMY_TURN'
turnPhase: TurnPhaseState
combatState: CombatState
onUseSkill: (skill: Skill) => void
onPassTurn: () => void
onToggleAutoCombat: () => void
autoCombatEnabled: boolean
```

### Combat.tsx → New Components

```typescript
// PhaseHeader
turnState, turnPhase, combatState.approach

// ConfrontationZone
player, enemy, playerStats, enemyStats

// CharacterPanel (player)
character: player, stats: playerStats, variant: 'player'

// CharacterPanel (enemy)
character: enemy, stats: enemyStats, variant: 'enemy'

// ActionDock
skills: player.skills, turnPhase, onUseSkill, onPassTurn
```

## Migration Strategy

### Phase 1: Layout Foundation
1. Create `CombatLayout.tsx` with CSS Grid
2. Create placeholder components
3. Add feature flag in Combat.tsx

### Phase 2: Component Extraction
4. Implement `CharacterPanel` (extract from PlayerHUD + CinematicViewscreen)
5. Implement `ActionDock` (extract from skill grids)
6. Implement `PhaseHeader` (extract from inline indicators)

### Phase 3: Visual Polish
7. Add `VSDivider` with effects
8. Implement animations
9. Adjust floating text positions

### Phase 4: Cleanup
10. Remove old theater mode code
11. Remove feature flag
12. Update tests

## Reference Files

- [layout-specs.md](references/layout-specs.md) - CSS Grid structure, responsive breakpoints
- [component-interfaces.md](references/component-interfaces.md) - TypeScript interfaces for all components
- [styling-tokens.md](references/styling-tokens.md) - Colors, spacing, typography tokens
- [animations.md](references/animations.md) - Animation keyframes and transitions

## Output Format

Generate TypeScript React components with:

1. **TypeScript interface** for props
2. **Tailwind CSS** for styling (matching existing codebase)
3. **Responsive classes** (mobile fallback to vertical)
4. **Memoization** where appropriate (React.memo for cards)
5. **Accessibility** attributes (aria-labels, roles)

## Existing Code References

When implementing, reference these existing files:

| New Component | Reference From |
|---------------|----------------|
| CharacterPanel (player) | `src/components/PlayerHUD.tsx` |
| CharacterPanel (enemy) | `src/scenes/Combat.tsx` lines 113-305 |
| ActionDock | `src/scenes/Combat.tsx` lines 308-607 |
| QuickActionCard | `src/components/SkillCard.tsx` |
| MainActionCard | `src/components/SkillCard.tsx` |
| PhaseHeader | `src/scenes/Combat.tsx` lines 311-328 |
