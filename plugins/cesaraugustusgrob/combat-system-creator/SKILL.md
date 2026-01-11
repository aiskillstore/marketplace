---
name: combat-system-creator
description: Create and modify combat system components for SHINOBI WAY game following the dual-system architecture (CombatCalculationSystem + CombatWorkflowSystem). Use when user wants to add new combat mechanics, damage formulas, status effects, mitigation logic, turn phases, or refactor existing combat code. Guides through proper separation of pure calculations vs state management.
---

# Combat System Creator - SHINOBI WAY

Create combat system components following the **dual-system architecture**: pure calculations separated from state workflow.

## Architecture Principle

```
Player Action → CombatCalculationSystem (pure math) → CombatWorkflowSystem (apply to state)
```

**CombatCalculationSystem**: Pure functions, no mutations, returns complete results
**CombatWorkflowSystem**: State management, applies calculated results, controls flow

## When to Use

- Add new damage calculations or formulas
- Create new status effects or mitigation mechanics
- Add new combat phases or turn logic
- Refactor existing combat code
- Balance or modify combat math

## Quick Reference

### Damage Pipeline (5 Steps)

```
1. Hit Check    → MELEE: Speed vs Speed | RANGED: Accuracy vs Speed | AUTO: Always hits
2. Base Damage  → ScalingStat × damageMult
3. Element      → Super: 1.5× (+10% crit) | Resist: 0.5× | Neutral: 1.0×
4. Critical     → 8% + (DEX × 0.5) + bonuses, max 75%, multiplier 1.75×
5. Defense      → Flat (max 60% reduction) then % (soft cap 75%)
```

### Mitigation Pipeline (Priority Order)

```
1. INVULNERABILITY → Blocks ALL damage (return 0)
2. REFLECTION      → Calculate reflected damage (before curse)
3. CURSE           → Amplify: damage × (1 + curseValue)
4. SHIELD          → Absorb damage before HP
5. GUTS            → Survive at 1 HP if roll succeeds
```

### Defense Formulas

| Type | Flat | Percent (Soft Cap) |
|------|------|-------------------|
| Physical | `STR × 0.3` | `STR / (STR + 200)` |
| Elemental | `SPI × 0.3` | `SPI / (SPI + 200)` |
| Mental | `CAL × 0.25` | `CAL / (CAL + 150)` |

### Damage Properties

| Property | Flat Def | % Def |
|----------|----------|-------|
| NORMAL | ✅ (max 60%) | ✅ |
| PIERCING | ❌ | ✅ |
| ARMOR_BREAK | ✅ | ❌ |
| TRUE | ❌ | ❌ |

## Workflow: Adding New Mechanics

### Step 1: Identify System

Ask: **Is this pure math or state management?**

| CombatCalculationSystem | CombatWorkflowSystem |
|------------------------|---------------------|
| Damage formulas | Applying damage to HP |
| Hit/miss/evasion rolls | Turn order management |
| Crit calculations | Buff duration tracking |
| Defense reduction | Phase transitions |
| Effect chance rolls | Combat log generation |

### Step 2: Design the Calculation Interface

For new calculations, define the result interface:

```typescript
interface NewMechanicResult {
  // All values needed to apply this mechanic
  value: number;
  triggered: boolean;
  // Metadata for logging
  logs: CombatLogEntry[];
}
```

### Step 3: Implement Pure Function

```typescript
// In CombatCalculationSystem
function calculateNewMechanic(
  attackerStats: DerivedStats,
  defenderStats: DerivedStats,
  context: CombatContext
): NewMechanicResult {
  // Pure calculation - NO state mutation
  return { value, triggered, logs };
}
```

### Step 4: Implement Workflow Application

```typescript
// In CombatWorkflowSystem
function applyNewMechanic(
  state: CombatWorkflowState,
  result: NewMechanicResult
): CombatWorkflowState {
  // Apply result to state - returns NEW state
  return { ...state, /* updated values */ };
}
```

## Creating New Status Effects

### Effect Types Available

```typescript
// Damage Over Time
DOT, BLEED, BURN, POISON

// Crowd Control
STUN, CONFUSION, SILENCE

// Defensive
SHIELD, INVULNERABILITY, REFLECTION

// Stat Modifiers
BUFF, DEBUFF, CURSE

// Recovery
HEAL, REGEN, CHAKRA_DRAIN
```

### Effect Interface

```typescript
interface SkillEffect {
  type: EffectType;
  value: number;           // Damage/heal amount or multiplier
  duration: number;        // Turns (-1 = permanent)
  chance: number;          // 0.0-1.0 application chance
  targetStat?: PrimaryStat; // For BUFF/DEBUFF
  damageType?: DamageType;  // For DoTs
  damageProperty?: DamageProperty;
}
```

### DoT Damage Formula

```typescript
// DoTs get 50% defense mitigation
dotDamage = max(1, baseDamage - (flatDef × 0.5) - (damage × percentDef × 0.5))
```

## Creating New Combat Phases

### Existing Turn Phases

**Player Turn:**
1. TURN_START → Reset flags
2. UPKEEP → Toggle costs, passive regen
3. MAIN_ACTION → Skill execution
4. DEATH_CHECK → Victory/defeat
5. TURN_END → Mark turn complete

**Enemy Turn:**
1. DOT_ENEMY → Process enemy DoTs
2. DOT_PLAYER → Process player DoTs (through shield)
3. DEATH_CHECK_DOT → Check DoT kills
4. ENEMY_ACTION → AI skill selection + execution
5. DEATH_CHECK_ATTACK → Check combat kills
6. RESOURCE_RECOVERY → Cooldowns, chakra regen
7. TERRAIN_HAZARDS → Environmental damage
8. FINAL_DEATH_CHECK → Hazard kills

### Adding New Phase

```typescript
// 1. Add to CombatPhase enum
enum CombatPhase {
  // ... existing
  NEW_PHASE,
}

// 2. Create calculation function
function calculateNewPhaseEffects(state: CombatWorkflowState): NewPhaseResult;

// 3. Create workflow handler
function processNewPhase(state: CombatWorkflowState): CombatWorkflowState;

// 4. Insert into turn flow in processEnemyTurn or executePlayerAction
```

## Output Templates

### New Calculation Function

```typescript
/**
 * [Description of what this calculates]
 * @param attackerStats - Attacker's derived stats
 * @param defenderStats - Defender's derived stats
 * @param skill - The skill being used
 * @returns [ResultType] with all calculation details
 */
export function calculateX(
  attackerStats: DerivedStats,
  defenderStats: DerivedStats,
  skill: Skill
): XResult {
  const result: XResult = {
    // Initialize result object
  };

  // Pure calculations here
  // NO state mutation
  // Use Math.random() for rolls

  return result;
}
```

### New Workflow Function

```typescript
/**
 * [Description of what state changes this applies]
 * @param state - Current combat state
 * @param result - Calculation result to apply
 * @returns New combat state with changes applied
 */
export function applyX(
  state: CombatWorkflowState,
  result: XResult
): CombatWorkflowState {
  // Create new state object (immutable)
  const newState = { ...state };

  // Apply result values to state
  // Add combat logs
  // Check for combat end conditions

  return newState;
}
```

### New Effect Implementation

```typescript
// In constants/index.ts - Add to SKILLS
NEW_SKILL: {
  id: 'new_skill',
  name: 'New Skill Name',
  // ... other properties
  effects: [{
    type: EffectType.NEW_EFFECT,
    value: 10,
    duration: 3,
    chance: 0.8,
    damageType: DamageType.PHYSICAL,
    damageProperty: DamageProperty.NORMAL
  }]
}

// In CombatSystem.ts - Handle in applyMitigation or processDoT
if (buff.effect.type === EffectType.NEW_EFFECT) {
  // Calculate effect
  // Apply to appropriate target
}
```

## Reference Files

- [combat-mechanics.md](references/combat-mechanics.md) - Full combat formulas and constants
- [architecture.md](references/architecture.md) - Dual-system architecture details

## Balance Constants

### Resource Pools
- HP: `50 + (WIL × 12)`
- Chakra: `30 + (CHA × 8)`
- HP Regen: `maxHP × 0.02 × (WIL / 20)`
- Chakra Regen: `INT × 2`

### Combat Constants
- Base Hit: 92%
- Hit Range: 30-98%
- Base Crit: 8%
- Crit Cap: 75%
- Crit Mult: 1.75×
- Flat Def Cap: 60% of damage
- % Def Cap: 75%

### Survival
- Guts: `WIL / (WIL + 200)`
- Status Resist: `CAL / (CAL + 80)`
- Evasion: `SPD / (SPD + 250)`
