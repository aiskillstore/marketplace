# Combat System Architecture

Detailed guide for the dual-system combat architecture.

## Table of Contents

1. [Overview](#overview)
2. [CombatCalculationSystem](#combatcalculationsystem)
3. [CombatWorkflowSystem](#combatworkflowsystem)
4. [Data Flow](#data-flow)
5. [Interfaces](#interfaces)
6. [Implementation Patterns](#implementation-patterns)
7. [Migration Guide](#migration-guide)

---

## Overview

### The Separation Principle

```
┌─────────────────────────────────────────────────────────────────┐
│                      COMBAT ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   INPUT                CALCULATION              WORKFLOW         │
│     │                      │                       │             │
│     ▼                      │                       │             │
│  ┌──────┐                  │                       │             │
│  │Skill │ ────────────────►│                       │             │
│  │Usage │                  ▼                       │             │
│  └──────┘          ┌──────────────┐                │             │
│                    │   PURE MATH   │                │             │
│                    │  No Mutations │                │             │
│                    │ Returns Result│                │             │
│                    └───────┬───────┘                │             │
│                            │                        │             │
│                            │ CombatActionResult     │             │
│                            │                        │             │
│                            └───────────────────────►│             │
│                                                     ▼             │
│                                             ┌──────────────┐      │
│                                             │ APPLY STATE  │      │
│                                             │  Mutations   │      │
│                                             │ Combat Logs  │      │
│                                             └───────┬──────┘      │
│                                                     │             │
│                                                     ▼             │
│                                             ┌──────────────┐      │
│                                             │ NEW STATE    │      │
│                                             └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why Separate?

| Aspect | CombatCalculationSystem | CombatWorkflowSystem |
|--------|------------------------|---------------------|
| **Purpose** | Compute combat math | Manage combat state |
| **Functions** | Pure, stateless | Stateful, orchestration |
| **Side Effects** | None | State mutations, logs |
| **Testability** | Unit tests (easy) | Integration tests |
| **Reusability** | High (tooltips, AI, preview) | Tied to combat flow |

---

## CombatCalculationSystem

### Principles

1. **Pure Functions Only** - Same inputs = same outputs
2. **No State Mutation** - Never modify input parameters
3. **Complete Results** - Return everything needed to apply
4. **Testable** - No mocking needed

### Core Functions

```typescript
// Main entry point
function calculateSkillUse(
  attacker: CombatEntity,
  defender: CombatEntity,
  skill: Skill,
  context: CombatContext
): CombatActionResult;

// Individual calculations
function calculateHitCheck(attackerStats, defenderStats, skill): HitCheckResult;
function calculateBaseDamage(attackerPrimary, skill): number;
function calculateElementEffectiveness(attackElement, defendElement): ElementResult;
function calculateCritical(attackerStats, skill, elementResult): CriticalResult;
function calculateDefenseReduction(damage, defenderStats, damageType, property): DefenseResult;
function calculateMitigation(damage, targetBuffs): MitigationResult;
function calculateGutsSurvival(currentHp, damage, gutsChance, alreadyUsed): GutsResult;
function calculateEffectApplications(effects, targetResist, damageDealt): EffectApplication[];
function calculateDotTick(dotEffect, defenderStats): number;
```

### Example Implementation

```typescript
function calculateBaseDamage(
  attackerPrimary: PrimaryAttributes,
  skill: Skill
): number {
  const scalingKey = skill.scalingStat.toLowerCase() as keyof PrimaryAttributes;
  const scalingValue = attackerPrimary[scalingKey] || 10;
  return Math.floor(scalingValue * skill.damageMult);
}

function calculateElementEffectiveness(
  attackElement: ElementType,
  defenderElement: ElementType
): ElementResult {
  const cycle = { FIRE: 'WIND', WIND: 'LIGHTNING', LIGHTNING: 'EARTH', EARTH: 'WATER', WATER: 'FIRE' };

  if (cycle[attackElement] === defenderElement) {
    return { multiplier: 1.5, isSuperEffective: true, isResisted: false, critBonus: 10 };
  }
  if (cycle[defenderElement] === attackElement) {
    return { multiplier: 0.5, isSuperEffective: false, isResisted: true, critBonus: 0 };
  }
  return { multiplier: 1.0, isSuperEffective: false, isResisted: false, critBonus: 0 };
}
```

---

## CombatWorkflowSystem

### Principles

1. **Owns Combat State** - Single source of truth
2. **Uses Calculations** - Calls pure functions for math
3. **Controls Flow** - Manages phases and transitions
4. **Generates Events** - Combat logs and UI updates

### Combat State

```typescript
interface CombatWorkflowState {
  // Combatants
  player: CombatantState;
  enemy: CombatantState;

  // Turn tracking
  currentTurn: 'player' | 'enemy';
  turnNumber: number;
  phase: CombatPhase;

  // Combat context
  isFirstTurn: boolean;
  firstHitMultiplier: number;
  terrain: TerrainDefinition | null;

  // Turn-scoped flags
  gutsUsedThisTurn: boolean;

  // Combat log
  logs: CombatLogEntry[];

  // Resolution
  isComplete: boolean;
  winner: 'player' | 'enemy' | null;
}

interface CombatantState {
  entity: Player | Enemy;
  currentHp: number;
  currentChakra: number;
  activeBuffs: Buff[];
  skillCooldowns: Map<string, number>;
}
```

### Core Functions

```typescript
// Initialization
function initializeCombat(player, enemy, terrain, modifiers): CombatWorkflowState;

// Main actions
function executePlayerAction(state, skill): CombatWorkflowState;
function executeEnemyTurn(state): CombatWorkflowState;

// Phase handlers
function processTurnStart(state, combatant): CombatWorkflowState;
function processUpkeep(state, combatant): CombatWorkflowState;
function processDoTPhase(state, combatant): CombatWorkflowState;
function applyActionResult(state, result, attacker): CombatWorkflowState;
function processTurnEnd(state, combatant): CombatWorkflowState;
function processTerrainHazards(state): CombatWorkflowState;
function checkCombatEnd(state): CombatWorkflowState;

// State mutators
function applyDamageToTarget(state, target, damage, source): CombatWorkflowState;
function applyHealToTarget(state, target, amount, source): CombatWorkflowState;
function applyEffectToTarget(state, target, effect): CombatWorkflowState;
function tickBuffDurations(state, target): CombatWorkflowState;
function updateCooldowns(state, target): CombatWorkflowState;
function addCombatLog(state, entry): CombatWorkflowState;
```

---

## Data Flow

### Player Uses Skill

```typescript
// BEFORE (mixed approach)
const result = useSkill(player, playerStats, enemy, enemyStats, skill, combatState);
// Result contains everything, function does calculation AND mutation

// AFTER (separated approach)
// Step 1: Build entities
const attacker = getCombatEntity(state.player);
const defender = getCombatEntity(state.enemy);

// Step 2: Calculate (PURE)
const actionResult = CombatCalculation.calculateSkillUse(
  attacker,
  defender,
  skill,
  { isFirstTurn: state.isFirstTurn, terrain: state.terrain, gutsUsedThisTurn: state.gutsUsedThisTurn }
);

// Step 3: Apply (MUTATION)
const newState = CombatWorkflow.applyActionResult(state, actionResult, 'player');
```

### Enemy Turn

```typescript
function executeEnemyTurn(state: CombatWorkflowState): CombatWorkflowState {
  let current = state;

  // Phase 1: DoTs on enemy
  current = processDoTPhase(current, 'enemy');
  current = tickBuffDurations(current, 'enemy');

  // Phase 2: DoTs on player (through shield)
  current = processDoTPhase(current, 'player');
  current = tickBuffDurations(current, 'player');

  // Phase 3: DoT death check
  current = checkCombatEnd(current);
  if (current.isComplete) return current;

  // Phase 4: Enemy action
  if (!isStunned(current.enemy)) {
    const skill = selectEnemySkill(current);
    const result = CombatCalculation.calculateSkillUse(
      getCombatEntity(current.enemy),
      getCombatEntity(current.player),
      skill,
      getContext(current)
    );
    current = applyActionResult(current, result, 'enemy');
  }

  // Phase 5: Attack death check
  current = checkCombatEnd(current);
  if (current.isComplete) return current;

  // Phase 6: Resource recovery
  current = updateCooldowns(current, 'player');
  current = restoreChakra(current, 'player');

  // Phase 7: Terrain hazards
  current = processTerrainHazards(current);

  // Phase 8: Final death check
  current = checkCombatEnd(current);

  return current;
}
```

---

## Interfaces

### CombatActionResult

```typescript
interface CombatActionResult {
  // Attack outcome
  hit: boolean;
  evaded: boolean;
  criticalHit: boolean;

  // Damage values
  rawDamage: number;
  elementMultiplier: number;
  critMultiplier: number;
  flatDefenseApplied: number;
  percentDefenseApplied: number;
  finalDamage: number;

  // Mitigation
  damageAbsorbedByShield: number;
  damageReflected: number;
  damageAmplifiedByCurse: number;
  invulnerabilityBlocked: boolean;

  // Survival
  wouldBeLethal: boolean;
  gutsTriggered: boolean;
  gutsSucceeded: boolean;

  // Effects
  effectsOnTarget: EffectApplication[];
  effectsOnSelf: EffectApplication[];

  // Resources
  attackerChakraChange: number;
  attackerHpChange: number;

  // Metadata
  skillUsed: Skill;
  logs: CombatLogEntry[];
}
```

### Supporting Interfaces

```typescript
interface CombatEntity {
  primaryStats: PrimaryAttributes;
  derivedStats: DerivedStats;
  activeBuffs: Buff[];
  element: ElementType;
  currentHp: number;
  currentChakra: number;
}

interface CombatContext {
  isFirstTurn: boolean;
  firstHitMultiplier: number;
  terrain: TerrainDefinition | null;
  gutsUsedThisTurn: boolean;
}

interface HitCheckResult {
  hit: boolean;
  hitChance: number;
  evaded: boolean;
  evasionChance: number;
}

interface ElementResult {
  multiplier: number;
  isSuperEffective: boolean;
  isResisted: boolean;
  critBonus: number;
}

interface CriticalResult {
  isCrit: boolean;
  critChance: number;
  critMultiplier: number;
}

interface DefenseResult {
  flatReduction: number;
  percentReduction: number;
  damageAfterDefense: number;
}

interface MitigationResult {
  finalDamage: number;
  reflectedDamage: number;
  shieldAbsorbed: number;
  curseAmplification: number;
  wasInvulnerable: boolean;
  shieldBroken: boolean;
}

interface GutsResult {
  wouldDie: boolean;
  gutsTriggered: boolean;
  survived: boolean;
  finalHp: number;
}

interface EffectApplication {
  type: EffectType;
  value: number;
  duration: number;
  wasResisted: boolean;
  resistChance: number;
}

interface CombatLogEntry {
  message: string;
  type: 'info' | 'damage' | 'heal' | 'effect' | 'critical' | 'miss';
}
```

---

## Implementation Patterns

### Pattern 1: Calculation with Controlled Randomness

```typescript
function calculateCritical(
  attackerStats: DerivedStats,
  skill: Skill,
  elementResult: ElementResult,
  randomValue?: number  // Optional for testing
): CriticalResult {
  const random = randomValue ?? Math.random();

  let critChance = attackerStats.critChance + (skill.critBonus || 0);
  critChance += elementResult.critBonus;
  critChance = Math.min(95, critChance);

  const isCrit = random * 100 < critChance;
  const critMult = skill.attackMethod === AttackMethod.RANGED
    ? attackerStats.critDamageRanged
    : attackerStats.critDamageMelee;

  return { isCrit, critChance, critMultiplier: isCrit ? critMult : 1.0 };
}
```

### Pattern 2: Immutable State Updates

```typescript
function applyDamageToTarget(
  state: CombatWorkflowState,
  target: 'player' | 'enemy',
  damage: number,
  source: string
): CombatWorkflowState {
  const targetState = state[target];
  const newHp = Math.max(0, targetState.currentHp - damage);

  return {
    ...state,
    [target]: {
      ...targetState,
      currentHp: newHp
    },
    logs: [
      ...state.logs,
      { message: `${target} took ${damage} damage from ${source}`, type: 'damage' }
    ]
  };
}
```

### Pattern 3: Composing Calculations

```typescript
function calculateSkillUse(
  attacker: CombatEntity,
  defender: CombatEntity,
  skill: Skill,
  context: CombatContext
): CombatActionResult {
  // Compose smaller calculations
  const hitResult = calculateHitCheck(attacker.derivedStats, defender.derivedStats, skill);
  if (!hitResult.hit || hitResult.evaded) {
    return createMissResult(skill, hitResult);
  }

  const baseDamage = calculateBaseDamage(attacker.primaryStats, skill);
  const elementResult = calculateElementEffectiveness(skill.element, defender.element);
  const critResult = calculateCritical(attacker.derivedStats, skill, elementResult);
  const defenseResult = calculateDefenseReduction(/* ... */);
  const mitigationResult = calculateMitigation(/* ... */);
  const gutsResult = calculateGutsSurvival(/* ... */);
  const effectResults = calculateEffectApplications(/* ... */);

  return combineResults(/* all results */);
}
```

---

## Migration Guide

### Phase 1: Extract Calculations
1. Create `CombatCalculationSystem.ts`
2. Move pure logic from `StatSystem.ts` and `CombatSystem.ts`
3. Keep existing functions as wrappers

### Phase 2: Define Interfaces
1. Create `CombatActionResult` interface
2. Create supporting interfaces
3. Ensure all workflow data is captured

### Phase 3: Create Workflow System
1. Create `CombatWorkflowSystem.ts`
2. Implement state management
3. Implement phase handlers

### Phase 4: Integrate
1. Update `useSkill` to use new systems
2. Update `processEnemyTurn`
3. Test all functionality

### Phase 5: UI Integration
1. Update `Combat.tsx`
2. Verify combat logs
3. Test edge cases

### File Structure

```
src/game/systems/
├── combat/
│   ├── index.ts                      # Exports
│   ├── CombatCalculationSystem.ts    # Pure functions
│   ├── CombatWorkflowSystem.ts       # State management
│   ├── types.ts                      # Combat interfaces
│   └── __tests__/
│       ├── calculation.test.ts
│       └── workflow.test.ts
├── StatSystem.ts
├── EnemyAISystem.ts
└── ApproachSystem.ts
```
