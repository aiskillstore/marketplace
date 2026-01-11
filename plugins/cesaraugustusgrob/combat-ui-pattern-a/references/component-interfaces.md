# Component Interfaces - Pattern A Split-Panel Combat UI

## Type Imports

```typescript
import {
  Player,
  Enemy,
  Skill,
  CharacterStats,
  TurnPhaseState,
  CombatState,
  ActiveEffect,
  ElementType,
  ActionType,
  SkillTier,
  Clan,
} from '@/game/types';
```

---

## CombatLayout

### Props Interface

```typescript
interface CombatLayoutProps {
  children: React.ReactNode;
  className?: string;
}
```

### Usage

```typescript
<CombatLayout>
  <PhaseHeader {...headerProps} />
  <ConfrontationZone {...zoneProps} />
  <ActionDock {...dockProps} />
</CombatLayout>
```

---

## PhaseHeader

### Props Interface

```typescript
interface PhaseHeaderProps {
  // Turn state
  turnNumber: number;
  turnState: 'PLAYER' | 'ENEMY_TURN';
  turnPhase: TurnPhaseState;

  // Approach (optional)
  approach?: {
    type: string;
    damageModifier: number;
    defenseModifier: number;
  };

  // Styling
  className?: string;
}

interface TurnPhaseState {
  phase: 'UPKEEP' | 'SIDE' | 'MAIN' | 'END';
  sideActionsUsed: number;
  maxSideActions: number;
  upkeepProcessed: boolean;
}
```

### Sub-Components

```typescript
// TurnIndicator
interface TurnIndicatorProps {
  turnNumber: number;
  currentActor: 'PLAYER' | 'ENEMY_TURN';
}

// PhasePipeline
interface PhasePipelineProps {
  currentPhase: 'UPKEEP' | 'SIDE' | 'MAIN' | 'END';
  completedPhases: string[];
}

// SideActionCounter
interface SideActionCounterProps {
  used: number;
  max: number;
}

// ApproachBadge
interface ApproachBadgeProps {
  type: string;
  damageModifier: number;
  defenseModifier: number;
}
```

---

## ConfrontationZone

### Props Interface

```typescript
interface ConfrontationZoneProps {
  // Player data
  player: Player;
  playerStats: CharacterStats;

  // Enemy data
  enemy: Enemy;
  enemyStats: CharacterStats;

  // Refs for floating text positioning
  playerRef?: React.RefObject<HTMLDivElement>;
  enemyRef?: React.RefObject<HTMLDivElement>;

  // Styling
  className?: string;
}
```

### Usage

```typescript
<ConfrontationZone
  player={player}
  playerStats={playerStats}
  enemy={enemy}
  enemyStats={enemyStats}
  playerRef={playerPanelRef}
  enemyRef={enemyPanelRef}
/>
```

---

## CharacterPanel

### Props Interface

```typescript
interface CharacterPanelProps {
  // Variant determines layout alignment
  variant: 'player' | 'enemy';

  // Character data (Player or Enemy)
  character: Player | Enemy;
  stats: CharacterStats;

  // Visual
  spriteUrl?: string;
  auraColor?: string;

  // Ref for floating text
  panelRef?: React.RefObject<HTMLDivElement>;

  // Styling
  className?: string;
}
```

### Player-Specific Props

```typescript
interface PlayerPanelProps extends CharacterPanelProps {
  variant: 'player';
  character: Player;

  // Player-specific
  clan: Clan;
  level: number;
  xp: { current: number; max: number };
  chakra: { current: number; max: number };
}
```

### Enemy-Specific Props

```typescript
interface EnemyPanelProps extends CharacterPanelProps {
  variant: 'enemy';
  character: Enemy;

  // Enemy-specific
  tier: 'NORMAL' | 'ELITE' | 'BOSS';
  element: ElementType;
  defenseStats?: {
    flatDefense: number;
    percentDefense: number;
  };
}
```

### Sub-Components

```typescript
// CharacterSprite
interface CharacterSpriteProps {
  src: string;
  alt: string;
  facing: 'left' | 'right';
  auraColor?: string;
  isAttacking?: boolean;
  isDamaged?: boolean;
}

// IdentityBar
interface IdentityBarProps {
  name: string;
  level?: number;
  tier?: 'NORMAL' | 'ELITE' | 'BOSS';
  element?: ElementType;
  clan?: Clan;
  align: 'left' | 'right';
}

// ResourceBar (HP/CP)
interface ResourceBarProps {
  type: 'hp' | 'cp' | 'xp';
  current: number;
  max: number;
  showLabel?: boolean;
  showValues?: boolean;
  previewDamage?: number;  // Ghost segment for damage preview
  size?: 'sm' | 'md' | 'lg';
}

// BuffBar
interface BuffBarProps {
  buffs: ActiveEffect[];
  maxVisible?: number;
  align: 'left' | 'right';
  onBuffClick?: (buff: ActiveEffect) => void;
}

// BuffIcon
interface BuffIconProps {
  effect: ActiveEffect;
  isPositive: boolean;
  onClick?: () => void;
}
```

---

## VSDivider

### Props Interface

```typescript
interface VSDividerProps {
  // Animation state
  isClashing?: boolean;
  clashIntensity?: 'low' | 'medium' | 'high';

  // Colors for aura clash
  playerAuraColor?: string;
  enemyAuraColor?: string;

  // Styling
  className?: string;
}
```

### Sub-Components

```typescript
// ClashEffect
interface ClashEffectProps {
  intensity: 'low' | 'medium' | 'high';
  playerColor: string;
  enemyColor: string;
  isActive: boolean;
}

// KunaiCrossed (SVG component)
interface KunaiCrossedProps {
  className?: string;
  color?: string;
}
```

---

## ActionDock

### Props Interface

```typescript
interface ActionDockProps {
  // Skills grouped by type
  skills: Skill[];

  // Turn state for enabling/disabling
  turnState: 'PLAYER' | 'ENEMY_TURN';
  turnPhase: TurnPhaseState;

  // Player stats for damage calculation
  playerStats: CharacterStats;
  enemyStats: CharacterStats;
  playerElement: ElementType;
  enemyElement: ElementType;

  // Callbacks
  onUseSkill: (skill: Skill) => void;
  onPassTurn: () => void;
  onToggleAutoCombat: () => void;

  // State
  autoCombatEnabled: boolean;

  // Styling
  className?: string;
}
```

### Derived Data

```typescript
// Split skills by action type
const sideSkills = skills.filter(s => s.actionType === ActionType.SIDE);
const toggleSkills = skills.filter(s => s.actionType === ActionType.TOGGLE);
const mainSkills = skills.filter(s => s.actionType === ActionType.MAIN);
const passiveSkills = skills.filter(s => s.actionType === ActionType.PASSIVE);
```

### Sub-Components

```typescript
// QuickActionsSection
interface QuickActionsSectionProps {
  sideSkills: Skill[];
  toggleSkills: Skill[];
  sideActionsUsed: number;
  maxSideActions: number;
  onUseSkill: (skill: Skill) => void;
  disabled: boolean;
}

// MainActionsSection
interface MainActionsSectionProps {
  mainSkills: Skill[];
  playerStats: CharacterStats;
  enemyStats: CharacterStats;
  onUseSkill: (skill: Skill) => void;
  disabled: boolean;
}

// ControlButtons
interface ControlButtonsProps {
  autoCombatEnabled: boolean;
  onToggleAutoCombat: () => void;
  onPassTurn: () => void;
  disabled: boolean;
}
```

---

## QuickActionCard

### Props Interface

```typescript
interface QuickActionCardProps {
  skill: Skill;

  // State
  isUsable: boolean;
  isOnCooldown: boolean;
  cooldownRemaining?: number;
  isToggleActive?: boolean;  // For TOGGLE skills

  // Callbacks
  onClick: () => void;

  // Styling
  variant: 'side' | 'toggle';
  size?: 'sm' | 'md';
  className?: string;
}
```

### Visual States

```typescript
type QuickCardState =
  | 'usable'           // Normal, clickable
  | 'disabled'         // Can't use (not enough resources)
  | 'cooldown'         // On cooldown
  | 'toggle-active'    // Toggle is ON (glowing)
  | 'toggle-inactive'; // Toggle is OFF

// Border colors by state
const QUICK_CARD_BORDERS = {
  'side-usable': 'border-blue-600 hover:border-blue-400',
  'side-disabled': 'border-zinc-700 opacity-50',
  'side-cooldown': 'border-zinc-800',
  'toggle-active': 'border-amber-500 ring-2 ring-amber-500/30',
  'toggle-inactive': 'border-amber-600/70 hover:border-amber-500',
};
```

---

## MainActionCard

### Props Interface

```typescript
interface MainActionCardProps {
  skill: Skill;

  // Damage prediction
  predictedDamage?: number;
  isCritPossible?: boolean;
  isEffective?: boolean;  // Element advantage
  effectivenessLabel?: 'SUPER EFFECTIVE' | 'NOT VERY EFFECTIVE' | null;

  // State
  isUsable: boolean;
  isOnCooldown: boolean;
  cooldownRemaining?: number;
  isSelected?: boolean;

  // Callbacks
  onClick: () => void;

  // Styling
  size?: 'md' | 'lg';
  className?: string;
}
```

### Visual States

```typescript
type MainCardState =
  | 'usable'          // Normal, clickable
  | 'selected'        // Currently selected (golden glow)
  | 'disabled'        // Can't use
  | 'cooldown'        // On cooldown
  | 'effective';      // Has element advantage

// Border/effect by state
const MAIN_CARD_STYLES = {
  usable: 'border-zinc-700 hover:border-zinc-500 hover:scale-[1.02]',
  selected: 'border-amber-400 ring-2 ring-amber-400/40 scale-105',
  disabled: 'border-zinc-800 opacity-50 grayscale cursor-not-allowed',
  cooldown: 'border-zinc-800 relative',
  effective: 'ring-1 ring-yellow-500/50',
};
```

### Card Content Structure

```typescript
// MainActionCard internal layout
<div className="relative">
  {/* Background image */}
  <div className="absolute inset-0 opacity-30">
    <img src={skill.image} />
  </div>

  {/* Content overlay */}
  <div className="relative z-10 p-3">
    {/* Header: Name + Tier */}
    <div className="flex justify-between">
      <span>{skill.name}</span>
      <TierBadge tier={skill.tier} />
    </div>

    {/* Damage number */}
    <div className="text-2xl font-bold text-right">
      {predictedDamage}
      <ElementIcon element={skill.element} />
    </div>

    {/* Footer: Costs */}
    <div className="flex gap-2 text-xs">
      {skill.chakraCost > 0 && <span>{skill.chakraCost} CP</span>}
      {skill.hpCost > 0 && <span>{skill.hpCost} HP</span>}
    </div>
  </div>

  {/* Cooldown overlay */}
  {isOnCooldown && (
    <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
      <span className="text-4xl font-bold">{cooldownRemaining}</span>
    </div>
  )}
</div>
```

---

## FloatingText (Unchanged)

### Props Interface (Reference)

```typescript
interface FloatingTextProps {
  id: string;
  value: string;
  type: 'damage' | 'crit' | 'heal' | 'miss' | 'block' | 'status' | 'chakra';
  position: { x: number; y: number };
  onComplete: (id: string) => void;
}
```

---

## Utility Types

```typescript
// Shared character stats shape
interface CharacterStats {
  effectivePrimary: Record<PrimaryStat, number>;
  derived: {
    maxHp: number;
    maxChakra: number;
    physicalAtk: number;
    elementalAtk: number;
    mentalAtk: number;
    flatDefense: number;
    percentDefense: number;
    critRate: number;
    critDamage: number;
    speed: number;
    accuracy: number;
    evasion: number;
  };
}

// Active effect on character
interface ActiveEffect {
  type: EffectType;
  value: number;
  duration: number;
  source?: string;
  targetStat?: PrimaryStat;
}
```

---

## Event Handlers

```typescript
// Combat callbacks from App.tsx
interface CombatCallbacks {
  onUseSkill: (skill: Skill) => void;
  onPassTurn: () => void;
  onToggleAutoCombat: () => void;
  onEscape?: () => void;  // For elite challenges
}

// Floating text spawn function
interface FloatingTextSpawner {
  spawnFloatingText: (
    target: 'player' | 'enemy',
    value: string,
    type: FloatingTextProps['type']
  ) => void;
}
```

---

## Component Ref Types

```typescript
// For imperative handle exposure
interface CombatRef {
  spawnFloatingText: FloatingTextSpawner['spawnFloatingText'];
  shakeScreen: () => void;
  flashPanel: (target: 'player' | 'enemy') => void;
}

// Panel refs for positioning
type PanelRef = React.RefObject<HTMLDivElement>;
```
