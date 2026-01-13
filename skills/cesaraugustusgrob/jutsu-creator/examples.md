# Skill Examples

Real skill examples from SHINOBI WAY to use as reference patterns.

---

## BASIC Tier (Academy/Genin Level)

### MAIN: Basic Attack (No Cost, No Cooldown)

```typescript
BASIC_ATTACK: {
  id: 'basic_atk',
  name: 'Taijutsu',
  tier: SkillTier.BASIC,
  description: 'A disciplined martial arts strike using raw physical power. Reliable and effective.',
  actionType: ActionType.MAIN,
  chakraCost: 0,
  hpCost: 0,
  cooldown: 0,
  currentCooldown: 0,
  damageMult: 2.0,
  scalingStat: PrimaryStat.STRENGTH,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.MELEE,
  element: ElementType.PHYSICAL
},
```

### MAIN: Ranged with Crit Bonus

```typescript
SHURIKEN: {
  id: 'shuriken',
  name: 'Shuriken',
  tier: SkillTier.BASIC,
  description: 'A swift throw of sharpened steel stars. Targets weak points for high critical chance.',
  actionType: ActionType.MAIN,
  chakraCost: 0,
  hpCost: 0,
  cooldown: 1,
  currentCooldown: 0,
  damageMult: 1.8,
  scalingStat: PrimaryStat.ACCURACY,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.RANGED,
  element: ElementType.PHYSICAL,
  critBonus: 25
},
```

### SIDE: Defensive Shield Skill

```typescript
MUD_WALL: {
  id: 'mud_wall',
  name: 'Mud Wall',
  tier: SkillTier.BASIC,
  description: 'Spits mud that hardens into a barricade. Creates a Shield.',
  actionType: ActionType.SIDE,
  chakraCost: 15,
  hpCost: 0,
  cooldown: 4,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.EARTH,
  requirements: { intelligence: 8 },
  effects: [{ type: EffectType.SHIELD, value: 40, duration: 3, chance: 1.0 }]
},
```

### SIDE: Buff Skill (No Damage)

```typescript
SHUNSHIN: {
  id: 'shunshin',
  name: 'Body Flicker',
  tier: SkillTier.BASIC,
  description: 'High-speed movement to close gaps. Greatly boosts Speed.',
  actionType: ActionType.SIDE,
  chakraCost: 15,
  hpCost: 0,
  cooldown: 3,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.SPEED,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.PHYSICAL,
  effects: [{ type: EffectType.BUFF, targetStat: PrimaryStat.SPEED, value: 0.4, duration: 2, chance: 1.0 }]
},
```

### SIDE: Clone Jutsu (Evasion Buff)

```typescript
BUNSHIN: {
  id: 'bunshin',
  name: 'Clone Technique',
  tier: SkillTier.BASIC,
  description: 'Creates illusory copies to distract the enemy. Boosts evasion.',
  actionType: ActionType.SIDE,
  chakraCost: 5,
  hpCost: 0,
  cooldown: 3,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.CHAKRA,
  damageType: DamageType.MENTAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.MENTAL,
  effects: [{ type: EffectType.BUFF, targetStat: PrimaryStat.SPEED, value: 0.2, duration: 2, chance: 1.0 }]
},
```

### SIDE: Smoke Bomb (Debuff Enemy)

```typescript
SMOKE_BOMB: {
  id: 'smoke_bomb',
  name: 'Smoke Bomb',
  tier: SkillTier.BASIC,
  description: 'Creates a smoke screen for cover. Reduces enemy accuracy.',
  actionType: ActionType.SIDE,
  chakraCost: 0,
  hpCost: 0,
  cooldown: 3,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.DEXTERITY,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.PHYSICAL,
  effects: [
    { type: EffectType.BUFF, targetStat: PrimaryStat.SPEED, value: 0.35, duration: 2, chance: 1.0 },
    { type: EffectType.DEBUFF, targetStat: PrimaryStat.ACCURACY, value: 0.2, duration: 2, chance: 1.0 }
  ]
},
```

### PASSIVE: Academy Training

```typescript
ACADEMY_TRAINING: {
  id: 'academy_training',
  name: 'Academy Training',
  tier: SkillTier.BASIC,
  description: 'Basic ninja academy conditioning. Slightly increases HP and Chakra.',
  actionType: ActionType.PASSIVE,
  chakraCost: 0,
  hpCost: 0,
  cooldown: 0,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.WILLPOWER,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.PHYSICAL,
  passiveEffect: {
    statBonus: { willpower: 1, chakra: 1 },
    specialEffect: 'academy_conditioning'
  }
},
```

### PASSIVE: Chakra Reserves

```typescript
CHAKRA_RESERVES: {
  id: 'chakra_reserves',
  name: 'Chakra Reserves',
  tier: SkillTier.BASIC,
  description: 'Deep chakra pools grant faster regeneration.',
  actionType: ActionType.PASSIVE,
  chakraCost: 0,
  hpCost: 0,
  cooldown: 0,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.CHAKRA,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.PHYSICAL,
  requirements: { intelligence: 6 },
  passiveEffect: {
    regenBonus: { chakra: 3 }
  }
},
```

---

## ADVANCED Tier (Chunin Level)

### MAIN: Fire Nuke with Burn

```typescript
FIREBALL: {
  id: 'fireball',
  name: 'Fireball Jutsu',
  tier: SkillTier.ADVANCED,
  description: 'A massive, searing projectile of flame. Leaves the target burning.',
  actionType: ActionType.MAIN,
  chakraCost: 25,
  hpCost: 0,
  cooldown: 3,
  currentCooldown: 0,
  damageMult: 3.5,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.RANGED,
  element: ElementType.FIRE,
  requirements: { intelligence: 12 },
  effects: [{
    type: EffectType.BURN,
    value: 15,
    duration: 3,
    chance: 0.8,
    damageType: DamageType.ELEMENTAL,
    damageProperty: DamageProperty.NORMAL
  }]
},
```

### MAIN: TRUE Damage with Chakra Drain

```typescript
GENTLE_FIST: {
  id: 'gentle_fist',
  name: 'Gentle Fist',
  tier: SkillTier.ADVANCED,
  description: 'Precise strikes to chakra points. True damage + Chakra Drain.',
  actionType: ActionType.MAIN,
  chakraCost: 15,
  hpCost: 0,
  cooldown: 2,
  currentCooldown: 0,
  damageMult: 2.5,
  scalingStat: PrimaryStat.ACCURACY,
  damageType: DamageType.TRUE,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.MELEE,
  element: ElementType.PHYSICAL,
  requirements: { intelligence: 12 },
  effects: [{ type: EffectType.CHAKRA_DRAIN, value: 20, duration: 1, chance: 1.0 }]
},
```

### MAIN: Control Skill with Stun

```typescript
WATER_PRISON: {
  id: 'water_prison',
  name: 'Water Prison',
  tier: SkillTier.ADVANCED,
  description: 'Traps the enemy in a sphere of heavy water. High stun chance.',
  actionType: ActionType.MAIN,
  chakraCost: 30,
  hpCost: 0,
  cooldown: 5,
  currentCooldown: 0,
  damageMult: 2.0,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.RANGED,
  element: ElementType.WATER,
  requirements: { intelligence: 14 },
  effects: [{ type: EffectType.STUN, duration: 2, chance: 0.7 }]
},
```

### MAIN: Mental Damage Genjutsu

```typescript
HELL_VIEWING: {
  id: 'hell_viewing',
  name: 'Hell Viewing Technique',
  tier: SkillTier.ADVANCED,
  description: 'A Genjutsu that reveals the target\'s worst fears. MENTAL damage resisted by Calmness.',
  actionType: ActionType.MAIN,
  chakraCost: 25,
  hpCost: 0,
  cooldown: 4,
  currentCooldown: 0,
  damageMult: 2.8,
  scalingStat: PrimaryStat.CALMNESS,
  damageType: DamageType.MENTAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.MENTAL,
  requirements: { intelligence: 10 },
  effects: [{
    type: EffectType.DEBUFF,
    targetStat: PrimaryStat.STRENGTH,
    value: 0.3,
    duration: 3,
    chance: 1.0
  }]
},
```

### SIDE: Phoenix Flower (Exception - SIDE with Damage)

```typescript
PHOENIX_FLOWER: {
  id: 'phoenix_flower',
  name: 'Phoenix Flower',
  tier: SkillTier.ADVANCED,
  description: 'Volleys of small fireballs. SIDE action exception that deals chip damage.',
  actionType: ActionType.SIDE,
  chakraCost: 20,
  hpCost: 0,
  cooldown: 2,
  currentCooldown: 0,
  damageMult: 2.2,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.RANGED,
  element: ElementType.FIRE,
  requirements: { intelligence: 10 },
  effects: [{
    type: EffectType.BURN,
    value: 8,
    duration: 2,
    chance: 0.5,
    damageType: DamageType.ELEMENTAL,
    damageProperty: DamageProperty.NORMAL
  }]
},
```

### TOGGLE: Sharingan (Clan Restricted)

```typescript
SHARINGAN_2TOMOE: {
  id: 'sharingan_2',
  name: 'Sharingan (2-Tomoe)',
  tier: SkillTier.ADVANCED,
  description: 'Visual prowess that perceives attack trajectories. Increases Speed and Dexterity.',
  actionType: ActionType.TOGGLE,
  chakraCost: 10,
  hpCost: 0,
  cooldown: 5,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.INTELLIGENCE,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.FIRE,
  requirements: { intelligence: 14, clan: Clan.UCHIHA },
  isToggle: true,
  upkeepCost: 5,
  effects: [
    { type: EffectType.BUFF, targetStat: PrimaryStat.SPEED, value: 0.3, duration: -1, chance: 1.0 },
    { type: EffectType.BUFF, targetStat: PrimaryStat.DEXTERITY, value: 0.25, duration: -1, chance: 1.0 }
  ]
},
```

---

## HIDDEN Tier (Jonin/Clan Secrets)

### MAIN: Piercing Signature Move

```typescript
RASENGAN: {
  id: 'rasengan',
  name: 'Rasengan',
  tier: SkillTier.HIDDEN,
  description: 'A swirling sphere of pure chakra. PIERCING damage ignores flat defense.',
  actionType: ActionType.MAIN,
  chakraCost: 35,
  hpCost: 0,
  cooldown: 3,
  currentCooldown: 0,
  damageMult: 4.2,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.PIERCING,
  attackMethod: AttackMethod.MELEE,
  element: ElementType.WIND,
  requirements: { intelligence: 14 },
  effects: [{
    type: EffectType.DEBUFF,
    targetStat: PrimaryStat.STRENGTH,
    value: 0.25,
    duration: 3,
    chance: 0.5
  }]
},
```

### MAIN: Lightning Assassin

```typescript
CHIDORI: {
  id: 'chidori',
  name: 'Chidori',
  tier: SkillTier.HIDDEN,
  description: 'A crackling assassination technique. PIERCING elemental damage with high crit.',
  actionType: ActionType.MAIN,
  chakraCost: 35,
  hpCost: 0,
  cooldown: 4,
  currentCooldown: 0,
  damageMult: 4.5,
  scalingStat: PrimaryStat.SPEED,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.PIERCING,
  attackMethod: AttackMethod.MELEE,
  element: ElementType.LIGHTNING,
  requirements: { intelligence: 16 },
  critBonus: 15,
  penetration: 0.2
},
```

### MAIN: HP Cost Physical

```typescript
PRIMARY_LOTUS: {
  id: 'primary_lotus',
  name: 'Primary Lotus',
  tier: SkillTier.HIDDEN,
  description: 'A forbidden technique unlocking the body\'s limits. Devastating PIERCING damage at HP cost.',
  actionType: ActionType.MAIN,
  chakraCost: 0,
  hpCost: 30,
  cooldown: 4,
  currentCooldown: 0,
  damageMult: 5.0,
  scalingStat: PrimaryStat.STRENGTH,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.PIERCING,
  attackMethod: AttackMethod.MELEE,
  element: ElementType.PHYSICAL,
  requirements: { intelligence: 6 },
  effects: [{
    type: EffectType.DEBUFF,
    targetStat: PrimaryStat.STRENGTH,
    value: 0.2,
    duration: 2,
    chance: 1.0
  }]
},
```

### MAIN: Armor Break

```typescript
SAND_COFFIN: {
  id: 'sand_coffin',
  name: 'Sand Coffin',
  tier: SkillTier.HIDDEN,
  description: 'Encases the enemy in crushing waves of sand. ARMOR_BREAK ignores % defense.',
  actionType: ActionType.MAIN,
  chakraCost: 40,
  hpCost: 0,
  cooldown: 5,
  currentCooldown: 0,
  damageMult: 4.0,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.ARMOR_BREAK,
  attackMethod: AttackMethod.RANGED,
  element: ElementType.EARTH,
  requirements: { intelligence: 16 },
  effects: [{ type: EffectType.STUN, duration: 1, chance: 0.7 }]
},
```

### TOGGLE: Byakugan (Clan Restricted)

```typescript
BYAKUGAN: {
  id: 'byakugan',
  name: 'Byakugan',
  tier: SkillTier.HIDDEN,
  description: 'The All-Seeing White Eye. Drastically improves Accuracy and Crit Chance.',
  actionType: ActionType.TOGGLE,
  chakraCost: 10,
  hpCost: 0,
  cooldown: 5,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.CALMNESS,
  damageType: DamageType.MENTAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.PHYSICAL,
  requirements: { clan: Clan.HYUGA },
  isToggle: true,
  upkeepCost: 5,
  effects: [
    { type: EffectType.BUFF, targetStat: PrimaryStat.ACCURACY, value: 0.4, duration: -1, chance: 1.0 },
    { type: EffectType.BUFF, targetStat: PrimaryStat.DEXTERITY, value: 0.3, duration: -1, chance: 1.0 }
  ]
},
```

### SIDE: Rotation (Defensive Reflect)

```typescript
ROTATION: {
  id: 'kaiten',
  name: '8 Trigrams Rotation',
  tier: SkillTier.HIDDEN,
  description: 'Expels chakra while spinning to repel attacks. Shield with damage reflection.',
  actionType: ActionType.SIDE,
  chakraCost: 25,
  hpCost: 0,
  cooldown: 4,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.CALMNESS,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.PHYSICAL,
  requirements: { clan: Clan.HYUGA },
  effects: [
    { type: EffectType.SHIELD, value: 50, duration: 1, chance: 1.0 },
    { type: EffectType.REFLECTION, value: 0.6, duration: 1, chance: 1.0 }
  ]
},
```

### SIDE: Multi-Buff Support

```typescript
SHADOW_CLONE: {
  id: 'shadow_clone',
  name: 'Shadow Clone Jutsu',
  tier: SkillTier.HIDDEN,
  description: 'Creates solid clones. Massive stat buffs but NO direct damage.',
  actionType: ActionType.SIDE,
  chakraCost: 50,
  hpCost: 0,
  cooldown: 6,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.CHAKRA,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.PHYSICAL,
  requirements: { intelligence: 18 },
  effects: [
    { type: EffectType.BUFF, targetStat: PrimaryStat.STRENGTH, value: 0.6, duration: 3, chance: 1.0 },
    { type: EffectType.BUFF, targetStat: PrimaryStat.SPEED, value: 0.4, duration: 3, chance: 1.0 }
  ]
},
```

---

## FORBIDDEN Tier (Dangerous Techniques)

### MAIN: TRUE Mental Damage

```typescript
TSUKUYOMI: {
  id: 'tsukuyomi',
  name: 'Tsukuyomi',
  tier: SkillTier.FORBIDDEN,
  description: 'Traps the target in an illusion of torture. Massive TRUE MENTAL damage.',
  actionType: ActionType.MAIN,
  chakraCost: 80,
  hpCost: 15,
  cooldown: 6,
  currentCooldown: 0,
  damageMult: 5.0,
  scalingStat: PrimaryStat.CALMNESS,
  damageType: DamageType.TRUE,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.MENTAL,
  requirements: { intelligence: 20, clan: Clan.UCHIHA },
  effects: [{ type: EffectType.STUN, duration: 1, chance: 1.0 }]
},
```

### MAIN: TRUE Physical (Hidden Lotus)

```typescript
HIDDEN_LOTUS: {
  id: 'hidden_lotus',
  name: 'Hidden Lotus',
  tier: SkillTier.FORBIDDEN,
  description: 'Opens multiple gates for devastating TRUE physical damage. Self-stun after.',
  actionType: ActionType.MAIN,
  chakraCost: 0,
  hpCost: 50,
  cooldown: 6,
  currentCooldown: 0,
  damageMult: 7.0,
  scalingStat: PrimaryStat.STRENGTH,
  damageType: DamageType.TRUE,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.MELEE,
  element: ElementType.PHYSICAL,
  requirements: { intelligence: 4 },
  effects: [{ type: EffectType.STUN, duration: 1, chance: 1.0, targetSelf: true }]
},
```

### TOGGLE: Gate of Life

```typescript
GATE_OF_LIFE: {
  id: 'gate_of_life',
  name: 'Gate of Life (3rd Gate)',
  tier: SkillTier.FORBIDDEN,
  description: 'Opens the Third Gate. Massive power at the cost of HP drain.',
  actionType: ActionType.TOGGLE,
  chakraCost: 0,
  hpCost: 25,
  cooldown: 99,
  currentCooldown: 0,
  damageMult: 0,
  scalingStat: PrimaryStat.STRENGTH,
  damageType: DamageType.PHYSICAL,
  damageProperty: DamageProperty.NORMAL,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.PHYSICAL,
  requirements: { intelligence: 4 },
  isToggle: true,
  upkeepCost: 10,  // HP per turn
  effects: [
    { type: EffectType.BUFF, targetStat: PrimaryStat.STRENGTH, value: 0.8, duration: -1, chance: 1.0 },
    { type: EffectType.BUFF, targetStat: PrimaryStat.SPEED, value: 0.6, duration: -1, chance: 1.0 }
  ]
},
```

---

## KINJUTSU Tier (Ultimate Forbidden)

### MAIN: Ultimate Wind Nuke

```typescript
RASENSHURIKEN: {
  id: 'rasenshuriken',
  name: 'Rasenshuriken',
  tier: SkillTier.KINJUTSU,
  description: 'Microscopic wind blades that sever chakra channels. TRUE PIERCING damage.',
  actionType: ActionType.MAIN,
  chakraCost: 120,
  hpCost: 0,
  cooldown: 5,
  currentCooldown: 0,
  damageMult: 6.0,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.TRUE,
  damageProperty: DamageProperty.PIERCING,
  attackMethod: AttackMethod.RANGED,
  element: ElementType.WIND,
  requirements: { intelligence: 20 }
},
```

### MAIN: DoT Ultimate

```typescript
AMATERASU: {
  id: 'amaterasu',
  name: 'Amaterasu',
  tier: SkillTier.KINJUTSU,
  description: 'Inextinguishable black flames. Initial PIERCING damage + massive TRUE DoT.',
  actionType: ActionType.MAIN,
  chakraCost: 80,
  hpCost: 20,
  cooldown: 5,
  currentCooldown: 0,
  damageMult: 3.0,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.PIERCING,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.FIRE,
  requirements: { intelligence: 22, clan: Clan.UCHIHA },
  effects: [{
    type: EffectType.BURN,
    value: 50,
    duration: 5,
    chance: 1.0,
    damageType: DamageType.TRUE,
    damageProperty: DamageProperty.NORMAL
  }]
},
```

### MAIN: Armor Break Nuke

```typescript
KIRIN: {
  id: 'kirin',
  name: 'Kirin',
  tier: SkillTier.KINJUTSU,
  description: 'Harnesses natural lightning from the heavens. Unavoidable ARMOR_BREAK strike.',
  actionType: ActionType.MAIN,
  chakraCost: 150,
  hpCost: 0,
  cooldown: 8,
  currentCooldown: 0,
  damageMult: 7.0,
  scalingStat: PrimaryStat.SPIRIT,
  damageType: DamageType.ELEMENTAL,
  damageProperty: DamageProperty.ARMOR_BREAK,
  attackMethod: AttackMethod.AUTO,
  element: ElementType.LIGHTNING,
  requirements: { intelligence: 24 }
},
```
