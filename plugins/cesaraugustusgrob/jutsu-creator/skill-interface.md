# Skill Interface Reference

This file contains all TypeScript types and enums needed for creating skills in SHINOBI WAY.

## Core Skill Interface

```typescript
interface Skill {
  id: string;                       // Unique identifier (lowercase_snake_case)
  name: string;                     // Display name
  tier: SkillTier;                  // Power tier (BASIC to KINJUTSU)
  description: string;              // Flavor text

  // ACTION TYPE - Determines when/how skill can be used
  actionType: ActionType;           // MAIN/TOGGLE/SIDE/PASSIVE
  sideActionLimit?: number;         // Max uses per turn (SIDE only, default 1)

  // Costs
  chakraCost: number;               // Chakra consumed on use
  hpCost: number;                   // HP sacrificed on use

  // Cooldown
  cooldown: number;                 // Turns before reuse
  currentCooldown: number;          // Always set to 0 for new skills

  // Damage Calculation
  damageMult: number;               // Base damage multiplier (1.0-10.0)
  scalingStat: PrimaryStat;         // Which stat scales damage
  damageType: DamageType;           // Physical/Elemental/Mental/True
  damageProperty: DamageProperty;   // Normal/Piercing/ArmorBreak
  attackMethod: AttackMethod;       // Melee/Ranged/Auto

  // Element (for elemental interactions)
  element: ElementType;

  // Toggle Skills (like Sharingan)
  isToggle?: boolean;               // True for stance skills
  isActive?: boolean;               // Runtime state
  upkeepCost?: number;              // CP or HP cost per turn while active

  // Effects applied on hit
  effects?: EffectDefinition[];

  // Bonuses
  critBonus?: number;               // Extra % crit chance
  penetration?: number;             // % defense ignored (0-1)

  // Requirements
  requirements?: SkillRequirements;

  // Passive Properties (for PASSIVE action type)
  passiveEffect?: PassiveSkillEffect;

  // Upgrade tracking
  level?: number;

  // Visual
  image?: string;                   // Path to skill background image
  icon?: string;                    // Emoji/icon for quick reference
}
```

## Enums

### ActionType (NEW)

Determines when and how a skill can be used in combat:

```typescript
enum ActionType {
  MAIN = 'Main',       // Ends your turn - primary attacks and jutsu
  TOGGLE = 'Toggle',   // Activate once (ends turn), pays upkeep per turn
  SIDE = 'Side',       // Free action BEFORE Main, max 2 per turn
  PASSIVE = 'Passive'  // Always active, no action required
}
```

**Action Type Rules:**
- **MAIN**: 1 per turn, ends your turn immediately after use
- **TOGGLE**: Activating ends turn, then pay upkeep cost each turn until deactivated
- **SIDE**: Up to 2 per turn, must be used BEFORE your MAIN action
- **PASSIVE**: Always in effect, no activation needed

### SkillTier

```typescript
enum SkillTier {
  BASIC = 'Basic',           // E-D Rank, INT 0-6
  ADVANCED = 'Advanced',     // C-B Rank, INT 8-12
  HIDDEN = 'Hidden',         // B-A Rank, INT 14-18
  FORBIDDEN = 'Forbidden',   // A-S Rank, INT 16-20
  KINJUTSU = 'Kinjutsu'      // S+ Rank, INT 20-24
}
```

### ElementType

Elemental cycle: **Fire > Wind > Lightning > Earth > Water > Fire**
- Strong against: 1.5x damage
- Weak against: 0.5x damage

```typescript
enum ElementType {
  FIRE = 'Fire',
  WIND = 'Wind',
  LIGHTNING = 'Lightning',
  EARTH = 'Earth',
  WATER = 'Water',
  PHYSICAL = 'Physical',
  MENTAL = 'Mental'           // For Genjutsu
}
```

### DamageType

Determines which defense stat mitigates the damage:

```typescript
enum DamageType {
  PHYSICAL = 'Physical',      // Mitigated by Strength
  ELEMENTAL = 'Elemental',    // Mitigated by Spirit
  MENTAL = 'Mental',          // Mitigated by Calmness
  TRUE = 'True'               // Bypasses ALL defenses (rare/forbidden)
}
```

### DamageProperty

How damage interacts with flat vs percentage defenses:

```typescript
enum DamageProperty {
  NORMAL = 'Normal',          // Subject to BOTH flat and % defenses
  PIERCING = 'Piercing',      // Ignores FLAT defense, only % applies
  ARMOR_BREAK = 'ArmorBreak'  // Ignores % defense, only flat applies
}
```

### AttackMethod

How hit/miss is calculated:

```typescript
enum AttackMethod {
  MELEE = 'Melee',            // Hit chance uses SPEED vs SPEED
  RANGED = 'Ranged',          // Hit chance uses ACCURACY vs SPEED
  AUTO = 'Auto'               // Always hits (genjutsu, some DoTs)
}
```

### PrimaryStat

The 9 core attributes for scaling:

```typescript
enum PrimaryStat {
  // THE BODY (Hardware)
  WILLPOWER = 'Willpower',    // Max HP, Guts chance
  CHAKRA = 'Chakra',          // Max Chakra capacity
  STRENGTH = 'Strength',      // Taijutsu Dmg, Physical Defense

  // THE MIND (Software)
  SPIRIT = 'Spirit',          // Elemental Dmg, Elemental Defense
  INTELLIGENCE = 'Intelligence', // Jutsu Requirements, Chakra Regen
  CALMNESS = 'Calmness',      // Genjutsu Defense, Status Resistance

  // THE TECHNIQUE (Application)
  SPEED = 'Speed',            // Initiative, Melee Hit, Evasion
  ACCURACY = 'Accuracy',      // Ranged Hit, Ranged Crit Multiplier
  DEXTERITY = 'Dexterity'     // Critical Hit Chance (all types)
}
```

### Clan

For clan-restricted skills:

```typescript
enum Clan {
  UZUMAKI = 'Uzumaki',
  UCHIHA = 'Uchiha',
  HYUGA = 'Hyuga',
  LEE = 'Lee Disciple',
  YAMANAKA = 'Yamanaka'
}
```

## Effect System

### EffectType

```typescript
enum EffectType {
  // Control
  STUN = 'Stun',              // Skip turns
  CONFUSION = 'Confusion',    // Random target selection
  SILENCE = 'Silence',        // Cannot use skills

  // Damage over Time
  DOT = 'DoT',                // Generic damage over time
  BLEED = 'Bleed',            // Physical DoT
  BURN = 'Burn',              // Fire DoT
  POISON = 'Poison',          // Ignores some defense

  // Stat Modification
  BUFF = 'Buff',              // Increase stat
  DEBUFF = 'Debuff',          // Decrease stat

  // Resource Manipulation
  HEAL = 'Heal',              // Restore HP
  DRAIN = 'Drain',            // Steal HP
  CHAKRA_DRAIN = 'ChakraDrain', // Drain chakra

  // Defensive
  SHIELD = 'Shield',          // Absorbs incoming damage
  INVULNERABILITY = 'Invuln', // Takes 0 damage
  REFLECTION = 'Reflect',     // Returns % of damage taken
  REGEN = 'Regen',            // Restores HP at turn start

  // Offensive Modifiers
  CURSE = 'Curse'             // Increases damage taken
}
```

### EffectDefinition

```typescript
interface EffectDefinition {
  type: EffectType;
  value?: number;             // Damage amount or stat multiplier
  duration: number;           // Turns (-1 for permanent/toggle)
  targetStat?: PrimaryStat;   // For Buff/Debuff
  chance: number;             // 0-1 probability
  damageType?: DamageType;    // For DoT effects
  damageProperty?: DamageProperty; // For DoT effects
}
```

## SkillRequirements

```typescript
interface SkillRequirements {
  intelligence?: number;      // Minimum INT to learn
  level?: number;             // Minimum player level
  clan?: Clan;                // Clan restriction
}
```

## PassiveSkillEffect (NEW)

For PASSIVE action type skills that provide permanent bonuses:

```typescript
interface PassiveSkillEffect {
  statBonus?: Partial<PrimaryAttributes>;  // Direct stat increases
  damageBonus?: number;       // % bonus to all damage dealt
  defenseBonus?: number;      // % bonus to all defense
  regenBonus?: {              // Per-turn regeneration
    hp?: number;
    chakra?: number;
  };
  specialEffect?: string;     // Unique effect identifier
}
```

## Common Effect Patterns

### DoT (Damage over Time)

```typescript
effects: [{
  type: EffectType.BURN,      // or BLEED, POISON
  value: 15,                  // Damage per tick
  duration: 3,                // Number of turns
  chance: 0.8,                // 80% to apply
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.NORMAL
}]
```

### Stun

```typescript
effects: [{
  type: EffectType.STUN,
  duration: 2,                // Turns stunned
  chance: 0.7                 // 70% to apply
}]
```

### Stat Buff

```typescript
effects: [{
  type: EffectType.BUFF,
  targetStat: PrimaryStat.STRENGTH,
  value: 0.3,                 // +30% to stat
  duration: 3,
  chance: 1.0                 // Guaranteed
}]
```

### Stat Debuff

```typescript
effects: [{
  type: EffectType.DEBUFF,
  targetStat: PrimaryStat.SPEED,
  value: 0.2,                 // -20% to stat
  duration: 2,
  chance: 0.5
}]
```

### Shield

```typescript
effects: [{
  type: EffectType.SHIELD,
  value: 50,                  // HP absorbed
  duration: 2,
  chance: 1.0
}]
```

### Chakra Drain

```typescript
effects: [{
  type: EffectType.CHAKRA_DRAIN,
  value: 20,                  // Chakra drained
  duration: 1,
  chance: 1.0
}]
```

## Action Type Guidelines

### MAIN Skills
- Primary damage dealers and attacks
- Always ends your turn
- Examples: Taijutsu, Fireball, Rasengan, Chidori

### TOGGLE Skills
- Stance abilities with ongoing effects
- Activation ends turn, then pay upkeep each subsequent turn
- Duration: -1 (permanent until deactivated or drained)
- Examples: Sharingan, Byakugan, Gate of Life

### SIDE Skills
- Setup and utility actions
- Use up to 2 per turn BEFORE your MAIN action
- Should NOT deal significant damage (exception: Phoenix Flower)
- Examples: Clone Jutsu, Smoke Bomb, Mud Wall, Brace

### PASSIVE Skills
- Always active, no action required
- Provide permanent bonuses while equipped
- Use `passiveEffect` property instead of `effects`
- Examples: Academy Training, Weapon Proficiency, Quick Reflexes
