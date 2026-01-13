# Combat Mechanics Reference

Complete reference for all combat formulas, constants, and mechanics.

## Table of Contents

1. [Stat System](#stat-system)
2. [Damage Calculation](#damage-calculation)
3. [Defense System](#defense-system)
4. [Elemental System](#elemental-system)
5. [Critical Hits](#critical-hits)
6. [Status Effects](#status-effects)
7. [Mitigation Pipeline](#mitigation-pipeline)
8. [Turn Flow](#turn-flow)
9. [Constants](#constants)

---

## Stat System

### 9 Primary Stats

**Body (Physical):**
| Stat | Effects | Range |
|------|---------|-------|
| Willpower | Max HP, Guts, HP Regen | 4-25 |
| Chakra | Max Chakra | 4-22 |
| Strength | Physical ATK, Physical DEF | 8-28 |

**Mind (Mental):**
| Stat | Effects | Range |
|------|---------|-------|
| Spirit | Elemental ATK, Elemental DEF | 2-22 |
| Intelligence | Chakra Regen, Mental ATK | 6-22 |
| Calmness | Mental DEF, Status Resist | 10-18 |

**Technique (Combat):**
| Stat | Effects | Range |
|------|---------|-------|
| Speed | Melee Hit, Evasion, Initiative | 10-26 |
| Accuracy | Ranged Hit, Ranged Crit Bonus | 8-22 |
| Dexterity | Crit Chance | 8-18 |

### Derived Stats

```typescript
// Resource Pools
maxHp = 50 + (willpower × 12) + equipment
maxChakra = 30 + (chakra × 8) + equipment
hpRegen = floor(maxHp × 0.02 × (willpower / 20))
chakraRegen = floor(intelligence × 2)

// Attack Power
physicalAtk = strength × 2 + dexterity × 0.5
elementalAtk = spirit × 2 + intelligence × 0.5
mentalAtk = intelligence × 1.5 + calmness × 1

// Defense (Flat)
physicalDefFlat = floor(strength × 0.3)
elementalDefFlat = floor(spirit × 0.3)
mentalDefFlat = floor(calmness × 0.25)

// Defense (Percent - Soft Cap)
physicalDefPercent = strength / (strength + 200)  // max 75%
elementalDefPercent = spirit / (spirit + 200)      // max 75%
mentalDefPercent = calmness / (calmness + 150)     // max 75%

// Combat
meleeHitRate = 92 + (speed × 0.3)
rangedHitRate = 92 + (accuracy × 0.3)
evasion = speed / (speed + 250)
critChance = min(75, 8 + (dexterity × 0.5))
critDamageMelee = 1.75
critDamageRanged = 1.75 + (accuracy × 0.008)
initiative = 10 + speed

// Survival
statusResistance = calmness / (calmness + 80)
gutsChance = willpower / (willpower + 200)
```

---

## Damage Calculation

### 5-Step Pipeline

**Step 1: Hit/Miss Check**
```typescript
// AUTO: Always hits
// MELEE: hitChance = 92 + (attackerSpeed × 0.3) - (defenderSpeed × 0.5)
// RANGED: hitChance = 92 + (attackerAcc × 0.3) - (defenderSpeed × 0.5)
hitChance = clamp(hitChance, 30, 98)
if (random() × 100 > hitChance) → MISS

// Evasion (separate roll after hit)
if (random() < defenderEvasion) → EVADED
```

**Step 2: Base Damage**
```typescript
scalingValue = attackerPrimary[skill.scalingStat]
rawDamage = floor(scalingValue × skill.damageMult)
```

**Step 3: Elemental Effectiveness**
```typescript
// Cycle: Fire → Wind → Lightning → Earth → Water → Fire
if (skillElement beats defenderElement) → multiplier = 1.5  // +10% crit
if (defenderElement beats skillElement) → multiplier = 0.5
else → multiplier = 1.0

rawDamage = floor(rawDamage × multiplier)
```

**Step 4: Critical Hit**
```typescript
effectiveCrit = critChance + skill.critBonus
if (elementMultiplier > 1.0) effectiveCrit += 10  // Super effective bonus
effectiveCrit = min(95, effectiveCrit)

if (random() × 100 < effectiveCrit) {
  isCrit = true
  critMult = (skill.attackMethod === RANGED) ? critDamageRanged : critDamageMelee
  rawDamage = floor(rawDamage × critMult)
}
```

**Step 5: Defense Application**
```typescript
// Select defense by damage type
if (TRUE) → flatDef = 0, percentDef = 0
if (PHYSICAL) → flatDef = physicalFlat, percentDef = physicalPercent
if (ELEMENTAL) → flatDef = elementalFlat, percentDef = elementalPercent
if (MENTAL) → flatDef = mentalFlat, percentDef = mentalPercent

// Apply penetration
percentDef = percentDef × (1 - skill.penetration)

// Apply by property
if (NORMAL) {
  flatReduction = min(flatDef, damage × 0.6)
  damage -= flatReduction
  percentReduction = floor(damage × percentDef)
  damage -= percentReduction
}
if (PIERCING) {
  percentReduction = floor(damage × percentDef)
  damage -= percentReduction
}
if (ARMOR_BREAK) {
  flatReduction = min(flatDef, damage × 0.6)
  damage -= flatReduction
}

finalDamage = max(1, floor(damage))
```

---

## Defense System

### Dual-Layer Mitigation

1. **Flat Defense** (Applied First)
   - Subtracts fixed amount from damage
   - Capped at 60% of incoming damage
   - Formula: `flatReduction = min(flatDef, damage × 0.6)`

2. **Percent Defense** (Applied Second)
   - Reduces remaining damage by percentage
   - Soft cap at 75%
   - Formula: `stat / (stat + SOFT_CAP)`

### Example
```
Incoming: 100 Physical Damage
Strength: 50 → Flat: 15, %: 20%

Step 1: Flat = min(15, 100 × 0.6) = 15
Step 2: After Flat = 100 - 15 = 85
Step 3: Final = 85 × (1 - 0.20) = 68 damage
```

---

## Elemental System

### Element Cycle
```
🔥 Fire → 🌪️ Wind → ⚡ Lightning → 🪨 Earth → 💧 Water → 🔥 Fire
```

### Effectiveness
| Matchup | Multiplier | Crit Bonus |
|---------|------------|------------|
| Super Effective | 1.5× | +10% |
| Neutral | 1.0× | 0 |
| Resisted | 0.5× | 0 |

### Element Types
- FIRE, WIND, LIGHTNING, EARTH, WATER (cycle)
- PHYSICAL (neutral, taijutsu)
- MENTAL (neutral, genjutsu)

---

## Critical Hits

### Chance Formula
```typescript
critChance = 8 + (dexterity × 0.5) + equipment + skillBonus
if (superEffective) critChance += 10
critChance = min(75, critChance)  // Hard cap
```

### Damage Multipliers
| Type | Multiplier |
|------|------------|
| Melee | 1.75× |
| Ranged | 1.75× + (accuracy × 0.008) |

---

## Status Effects

### Damage Over Time (DoT)
| Effect | Type | Duration | Defense |
|--------|------|----------|---------|
| Bleed | Physical | 3 turns | 50% mitigation |
| Burn | Elemental | 3 turns | 50% mitigation |
| Poison | True | Variable | Bypasses all |

**DoT Damage Formula:**
```typescript
dotDamage = max(1, floor(baseDamage - flatDef × 0.5 - damage × percentDef × 0.5))
```

### Crowd Control
| Effect | Description |
|--------|-------------|
| Stun | Skip turn entirely |
| Confusion | 50% chance to hit self for half damage |
| Silence | Cannot use jutsu (planned) |

### Buffs/Debuffs
```typescript
// Buff
modifiedStat = originalStat × (1 + buffValue)

// Debuff
modifiedStat = originalStat × (1 - debuffValue)
```

### Defensive Effects
| Effect | Priority | Description |
|--------|----------|-------------|
| Invulnerability | 1 | Take 0 damage |
| Reflection | 2 | Return % to attacker |
| Shield | 3 | Absorb before HP |
| Guts | 4 | Survive at 1 HP |

---

## Mitigation Pipeline

Applied in strict order after damage calculation:

```typescript
function applyMitigation(buffs, incomingDamage, targetName): MitigationResult {
  let damage = incomingDamage;
  let reflected = 0;

  // 1. INVULNERABILITY (highest priority)
  if (hasInvulnerability(buffs)) {
    return { finalDamage: 0, reflected: 0 };
  }

  // 2. REFLECTION (calculate before curse amplifies)
  const reflect = findReflection(buffs);
  if (reflect) {
    reflected = floor(damage × reflect.value);
  }

  // 3. CURSE (damage amplification)
  const curse = findCurse(buffs);
  if (curse) {
    damage += floor(damage × curse.value);
  }

  // 4. SHIELD (absorption)
  const shield = findShield(buffs);
  if (shield) {
    if (shield.value >= damage) {
      shield.value -= damage;
      damage = 0;
    } else {
      damage -= shield.value;
      removeShield(buffs);
    }
  }

  return { finalDamage: damage, reflected };
}
```

---

## Turn Flow

### Player Turn Phases
1. **TURN_START** - Reset gutsUsedThisTurn flag
2. **UPKEEP** - Pay toggle costs, apply passive regen
3. **MAIN_ACTION** - Execute skill, calculate & apply damage
4. **DEATH_CHECK** - Check victory/defeat
5. **TURN_END** - Mark isFirstTurn = false

### Enemy Turn Phases
1. **DOT_ENEMY** - Process Bleed/Burn/Poison on enemy, tick buffs
2. **DOT_PLAYER** - Process DoTs on player (through shield), tick buffs
3. **DEATH_CHECK_DOT** - Check DoT kills, player guts
4. **STUN_CHECK** - Skip if stunned
5. **CONFUSION_CHECK** - 50% self-hit if confused
6. **ENEMY_ACTION** - AI selects skill, calculate & apply damage
7. **DEATH_CHECK_ATTACK** - Check kills, player guts
8. **COOLDOWN_REDUCTION** - Reduce player cooldowns by 1
9. **CHAKRA_REGEN** - Restore player chakra
10. **TERRAIN_HAZARDS** - Environmental damage to both
11. **FINAL_DEATH_CHECK** - Hazard kills, player guts

---

## Constants

### Resource Constants
| Constant | Value |
|----------|-------|
| HP_BASE | 50 |
| HP_PER_WILLPOWER | 12 |
| CHAKRA_BASE | 30 |
| CHAKRA_PER_CHAKRA | 8 |
| HP_REGEN_PERCENT | 0.02 |
| CHAKRA_REGEN_PER_INT | 2 |

### Combat Constants
| Constant | Value |
|----------|-------|
| BASE_HIT_CHANCE | 92% |
| HIT_CHANCE_MIN | 30% |
| HIT_CHANCE_MAX | 98% |
| BASE_CRIT_CHANCE | 8% |
| CRIT_PER_DEX | 0.5 |
| CRIT_CHANCE_CAP | 75% |
| BASE_CRIT_MULT | 1.75× |
| SUPER_EFFECTIVE_CRIT_BONUS | 10% |

### Defense Constants
| Constant | Value |
|----------|-------|
| FLAT_PHYS_DEF_PER_STR | 0.3 |
| FLAT_ELEM_DEF_PER_SPIRIT | 0.3 |
| FLAT_MENTAL_DEF_PER_CALM | 0.25 |
| PHYSICAL_DEF_SOFT_CAP | 200 |
| ELEMENTAL_DEF_SOFT_CAP | 200 |
| MENTAL_DEF_SOFT_CAP | 150 |
| FLAT_DEF_MAX_PERCENT | 60% |
| PERCENT_DEF_MAX | 75% |

### Survival Constants
| Constant | Value |
|----------|-------|
| EVASION_SOFT_CAP | 250 |
| STATUS_RESIST_SOFT_CAP | 80 |
| GUTS_SOFT_CAP | 200 |
| INIT_BASE | 10 |
| INIT_PER_SPEED | 1 |

### Enemy Scaling
```typescript
floorMultiplier = 1 + (floor × 0.08)
difficultyMultiplier = 0.50 + (difficulty / 200)
totalScaling = floorMultiplier × difficultyMultiplier
```
