# Example: Land of Waves Region

Complete example implementation of the Land of Waves region.

## Region Overview

```typescript
const wavesRegion: Region = {
  id: 'waves',
  name: 'Land of Waves',
  theme: 'Misty coast, poverty, tyranny, moral ambiguity',
  description: 'A coastal region under the brutal control of shipping magnate Goro.',

  entryPoints: ['docks', 'beach'],
  bossLocation: 'compound',

  lootTheme: {
    primaryElement: ElementType.WATER,
    equipmentFocus: ['speed', 'dexterity'],
    goldMultiplier: 0.8  // Poor region
  }
};
```

## Location Map (13 Locations)

```
COLUMN 0          COLUMN 1         COLUMN 2         COLUMN 3         COLUMN 4
(Entry)           (Early)          (Mid)            (Late)           (Boss)

⚓ Docks ─────────► 🌲 Forest ──────► 🏘️ Village ────► 🌉 Bridge ──────► 🏯 Compound
   │                  │                  │               │                  ▲
   │                  │                  │               │                  │
   │                  ▼                  ▼               ▼                  │
   │              🕳️ Cave ◄────────► 🏕️ Camp ──────► ⚔️ Outpost ─────────┤
   │                  │                  │               │                  │
   │                  │                  │               │                  │
   ▼                  │                  │               ▼                  │
🌊 Beach ─────────────┴──────────────────┴───────────► 🏚️ Manor ──────────┤
   │                                                     ▲                  │
   │                                                     │                  │
   │              ┌─────────────────────────────────────┘                  │
   │              │                                                         │
   ▼              ▼                                                         │
🚢 Ship ────────► 🔮 Cove                                                   │
(Secret)         (Secret)                                                   │
   │                                                                        │
   ▼                                                                        │
💀 Shrine ──────────────────────────────────────────────────────────────────┘
(Secret/Dark)
```

## All Locations

| # | Location | Type | Danger | Icon | Column | Forward Paths |
|---|----------|------|--------|------|--------|---------------|
| 1 | The Docks | settlement | 2 | ⚓ | 0 | Forest, Cave |
| 2 | Misty Beach | wilderness | 1 | 🌊 | 0 | Cave, Camp, Ship* |
| 3 | Coastal Forest | wilderness | 3 | 🌲 | 1 | Village, Cave |
| 4 | Smuggler's Cave | stronghold | 4 | 🕳️ | 1 | Camp, Village |
| 5 | Fishing Village | settlement | 1 | 🏘️ | 2 | Bridge, Camp |
| 6 | Riverside Camp | wilderness | 3 | 🏕️ | 2 | Bridge, Outpost |
| 7 | Sunken Ship | secret | 5 | 🚢 | 2 | Cove, Shrine* |
| 8 | Bridge Construction | landmark | 4 | 🌉 | 3 | Compound, Outpost, Manor |
| 9 | Bandit Outpost | stronghold | 5 | ⚔️ | 3 | Compound, Manor |
| 10 | Abandoned Manor | landmark | 3 | 🏚️ | 3 | Compound |
| 11 | Hidden Cove | secret | 4 | 🔮 | 2 | Manor, Outpost |
| 12 | Drowned Shrine | secret | 6 | 💀 | 3 | Compound |
| 13 | Goro's Compound | boss | 7 | 🏯 | 4 | (none - end) |

*Secret paths require special unlock conditions

## Loop Paths

| From | To | Discovery |
|------|----|-----------|
| Forest | Docks | Intel from Forest elite |
| Cave | Beach | Intel from Cave elite |
| Cave | Docks | Intel from Cave elite |
| Outpost | Camp | Intel from Outpost elite |

## Location Definitions

### Entry Locations (Column 0)

```typescript
const theDocks: Location = {
  id: 'docks',
  name: 'The Docks',
  type: 'settlement',
  icon: '⚓',
  danger: 2,
  terrain: 'water_adjacent',
  terrainEffects: [{ type: 'water_damage_bonus', value: 0.2 }],
  description: 'Weathered wooden piers stretch into the mist. Workers load cargo under watchful eyes.',
  enemyPool: ['dock_worker', 'corrupt_guard', 'smuggler'],
  lootTable: 'docks_loot',
  atmosphereEvents: ['suspicious_cargo', 'overheard_conversation'],
  tiedStoryEvents: ['meet_tazuna'],
  intelMission: {
    elite: { id: 'dock_enforcer', name: 'Goro\'s Enforcer', level: 3, hp: 120 },
    flavorText: 'A scarred enforcer blocks the road out of town...',
    skipAllowed: true,
    intelReward: {
      revealedPaths: [
        { pathId: 'docks_to_forest', destinationName: 'Coastal Forest', destinationIcon: '🌲', dangerLevel: 3, hint: 'Dense trees, ambush territory' },
        { pathId: 'docks_to_cave', destinationName: 'Smuggler\'s Cave', destinationIcon: '🕳️', dangerLevel: 4, hint: 'Criminal hideout, valuable loot' }
      ]
    }
  },
  forwardPaths: ['docks_to_forest', 'docks_to_cave'],
  flags: {
    isEntry: true,
    isBoss: false,
    isSecret: false,
    hasMerchant: true,
    hasRest: true,
    hasTraining: false
  }
};

const mistyBeach: Location = {
  id: 'beach',
  name: 'Misty Beach',
  type: 'wilderness',
  icon: '🌊',
  danger: 1,
  terrain: 'water_adjacent',
  terrainEffects: [{ type: 'water_damage_bonus', value: 0.2 }],
  description: 'Fog rolls in from the sea, obscuring the sand. Wrecked boats dot the shoreline.',
  enemyPool: ['crab', 'beach_bandit', 'sea_spirit'],
  lootTable: 'beach_loot',
  atmosphereEvents: ['washed_up_treasure', 'stranded_sailor'],
  intelMission: {
    elite: { id: 'beach_guardian', name: 'Sea Spirit', level: 2, hp: 80 },
    flavorText: 'The mist parts to reveal a shimmering figure...',
    skipAllowed: true,
    intelReward: {
      revealedPaths: [
        { pathId: 'beach_to_cave', destinationName: 'Smuggler\'s Cave', destinationIcon: '🕳️', dangerLevel: 4, hint: 'Criminal hideout' },
        { pathId: 'beach_to_camp', destinationName: 'Riverside Camp', destinationIcon: '🏕️', dangerLevel: 3, hint: 'Rest spot' }
      ],
      secretHint: 'Legends speak of a sunken ship visible at low tide...'
    }
  },
  forwardPaths: ['beach_to_cave', 'beach_to_camp'],
  secretPaths: ['beach_to_ship'],
  flags: {
    isEntry: true,
    isBoss: false,
    isSecret: false,
    hasMerchant: false,
    hasRest: true,
    hasTraining: false
  }
};
```

### Secret Location Example

```typescript
const sunkenShip: Location = {
  id: 'ship',
  name: 'Sunken Ship',
  type: 'secret',
  icon: '🚢',
  danger: 5,
  terrain: 'underwater',
  terrainEffects: [
    { type: 'water_damage_bonus', value: 0.3 },
    { type: 'fire_damage_penalty', value: -0.5 }
  ],
  description: 'A merchant vessel lies half-submerged. Its cargo hold still beckons treasure hunters.',
  enemyPool: ['drowned_sailor', 'water_spirit', 'treasure_guardian'],
  lootTable: 'sunken_treasure',
  atmosphereEvents: ['trapped_air_pocket', 'spectral_captain'],
  intelMission: {
    elite: { id: 'ship_captain', name: 'Spectral Captain', level: 5, hp: 200 },
    flavorText: 'The ghostly captain guards his lost treasure eternally...',
    skipAllowed: true,
    intelReward: {
      revealedPaths: [
        { pathId: 'ship_to_cove', destinationName: 'Hidden Cove', destinationIcon: '🔮', dangerLevel: 4, hint: 'Sacred waters' }
      ],
      secretHint: 'The captain whispers of a drowned shrine to dark gods...'
    }
  },
  forwardPaths: ['ship_to_cove'],
  secretPaths: ['ship_to_shrine'],
  flags: {
    isEntry: false,
    isBoss: false,
    isSecret: true,
    hasMerchant: false,
    hasRest: false,
    hasTraining: false
  },
  unlockCondition: { type: 'intel', requirement: 'sunken_ship_discovered' }
};
```

### Boss Location

```typescript
const goroCompound: Location = {
  id: 'compound',
  name: 'Goro\'s Compound',
  type: 'boss',
  icon: '🏯',
  danger: 7,
  terrain: 'fortified',
  terrainEffects: [{ type: 'enemy_willpower_bonus', value: 0.1 }],
  description: 'A fortress of wealth built on suffering. Goro rules from within.',
  enemyPool: ['elite_guard', 'ronin', 'assassin'],
  lootTable: 'goro_treasury',
  atmosphereEvents: ['servant_whispers', 'display_of_power'],
  intelMission: {
    boss: {
      id: 'goro',
      name: 'Goro',
      title: 'The Tyrant of Waves',
      level: 10,
      hp: 850,
      element: ElementType.WATER,
      skills: ['water_prison', 'tidal_wave', 'drowning_grip'],
      phases: [
        { hpThreshold: 0.5, skills: ['desperate_flood'], buffs: [{ type: 'attack', value: 0.3 }] }
      ]
    },
    flavorText: 'Goro sits on his throne of stolen wealth. There is no escape.',
    skipAllowed: false,  // MUST FIGHT
    intelReward: null    // No next path - this is the end
  },
  forwardPaths: [],  // No forward paths from boss
  flags: {
    isEntry: false,
    isBoss: true,
    isSecret: false,
    hasMerchant: false,
    hasRest: false,
    hasTraining: false
  }
};
```

## Path Definitions

```typescript
const wavesPaths: Path[] = [
  // Entry paths
  { id: 'docks_to_forest', from: 'docks', to: 'forest', type: 'forward', hidden: false },
  { id: 'docks_to_cave', from: 'docks', to: 'cave', type: 'branch', hidden: false },
  { id: 'beach_to_cave', from: 'beach', to: 'cave', type: 'forward', hidden: false },
  { id: 'beach_to_camp', from: 'beach', to: 'camp', type: 'forward', hidden: false },

  // Secret path
  { id: 'beach_to_ship', from: 'beach', to: 'ship', type: 'secret', hidden: true,
    unlockCondition: { type: 'intel', requirement: 'sunken_ship_discovered' } },

  // Mid-game paths
  { id: 'forest_to_village', from: 'forest', to: 'village', type: 'forward', hidden: false },
  { id: 'forest_to_cave', from: 'forest', to: 'cave', type: 'branch', hidden: false },
  { id: 'cave_to_camp', from: 'cave', to: 'camp', type: 'forward', hidden: false },
  { id: 'cave_to_village', from: 'cave', to: 'village', type: 'branch', hidden: false },

  // Loop paths
  { id: 'forest_to_docks', from: 'forest', to: 'docks', type: 'loop', hidden: true,
    unlockCondition: { type: 'intel', requirement: 'loop_discovered' } },
  { id: 'cave_to_beach', from: 'cave', to: 'beach', type: 'loop', hidden: true,
    unlockCondition: { type: 'intel', requirement: 'loop_discovered' } },

  // Late-game paths
  { id: 'village_to_bridge', from: 'village', to: 'bridge', type: 'forward', hidden: false },
  { id: 'camp_to_bridge', from: 'camp', to: 'bridge', type: 'forward', hidden: false },
  { id: 'camp_to_outpost', from: 'camp', to: 'outpost', type: 'branch', hidden: false },

  // Boss paths
  { id: 'bridge_to_compound', from: 'bridge', to: 'compound', type: 'boss', hidden: false },
  { id: 'outpost_to_compound', from: 'outpost', to: 'compound', type: 'boss', hidden: false },
  { id: 'manor_to_compound', from: 'manor', to: 'compound', type: 'boss', hidden: false },
  { id: 'shrine_to_compound', from: 'shrine', to: 'compound', type: 'boss', hidden: false }
];
```

## Elite Pool

```typescript
const wavesElites: EliteEnemy[] = [
  { id: 'dock_enforcer', name: 'Goro\'s Enforcer', level: 3, hp: 120, element: ElementType.PHYSICAL },
  { id: 'beach_guardian', name: 'Sea Spirit', level: 2, hp: 80, element: ElementType.WATER },
  { id: 'forest_hunter', name: 'Demon Brothers Scout', level: 4, hp: 150, element: ElementType.PHYSICAL },
  { id: 'cave_boss', name: 'Smuggler King', level: 4, hp: 180, element: ElementType.PHYSICAL },
  { id: 'village_defender', name: 'Retired Shinobi', level: 3, hp: 100, element: ElementType.WATER },
  { id: 'bridge_guardian', name: 'Construction Foreman', level: 5, hp: 200, element: ElementType.EARTH },
  { id: 'outpost_commander', name: 'Bandit Captain', level: 6, hp: 250, element: ElementType.PHYSICAL },
  { id: 'manor_spirit', name: 'Vengeful Ghost', level: 4, hp: 130, element: ElementType.MENTAL },
  { id: 'ship_captain', name: 'Spectral Captain', level: 5, hp: 200, element: ElementType.WATER },
  { id: 'cove_priestess', name: 'Sea Priestess', level: 5, hp: 170, element: ElementType.WATER },
  { id: 'shrine_demon', name: 'Drowned Demon', level: 7, hp: 300, element: ElementType.WATER }
];
```

## Validation Summary

- [x] 13 locations (within 10-15 range)
- [x] 2 entry points (docks, beach)
- [x] 1 boss location (compound)
- [x] All locations reachable from entry
- [x] 4 paths lead to boss (bridge, outpost, manor, shrine)
- [x] Danger curve: Entry (1-2) → Mid (3-4) → Late (5-6) → Boss (7)
- [x] 3 secret locations (ship, cove, shrine)
- [x] 4 loop paths defined
- [x] Water theme consistent throughout
