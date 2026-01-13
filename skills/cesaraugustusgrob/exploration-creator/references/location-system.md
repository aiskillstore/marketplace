# Location System

Each location is a distinct area within a region containing 10 rooms.

## Location Types

| Type | Focus | Combat | Merchant | Rest | Special |
|------|-------|--------|----------|------|---------|
| `settlement` | Story, social | Low | Yes | Yes | NPC interactions |
| `wilderness` | Exploration | Medium | No | Maybe | Random events |
| `stronghold` | Heavy combat | High | Maybe | No | Guaranteed elites |
| `landmark` | Balanced | Medium | Maybe | Maybe | Story events |
| `secret` | Special content | Varies | Rare | Rare | Unique rewards |
| `boss` | Final encounter | BOSS | No | No | Cannot skip Room 10 |

## Location Data Structure

```typescript
interface Location {
  // Identity
  id: string;
  name: string;
  type: LocationType;
  icon: string;                   // Emoji for map display

  // Difficulty
  danger: 1 | 2 | 3 | 4 | 5 | 6 | 7;

  // Environment
  terrain: TerrainType;
  terrainEffects: TerrainEffect[];

  // Content
  description: string;
  enemyPool: EnemyId[];
  lootTable: LootTableId;

  // Events
  atmosphereEvents: EventId[];    // Random events pool
  tiedStoryEvents?: EventId[];    // Story tree events

  // Room 10 - Intel Mission
  intelMission: IntelMission;

  // Navigation
  forwardPaths: PathId[];         // Always available paths forward
  loopPaths?: PathId[];           // Paths back (require intel)
  secretPaths?: PathId[];         // Hidden paths (require unlock)

  // Flags
  flags: {
    isEntry: boolean;             // Starting location?
    isBoss: boolean;              // Final boss location?
    isSecret: boolean;            // Hidden until discovered?
    hasMerchant: boolean;         // Can spawn merchant room?
    hasRest: boolean;             // Can spawn rest room?
    hasTraining: boolean;         // Can spawn training room?
  };

  // Secret unlock (only if isSecret: true)
  unlockCondition?: UnlockCondition;
}
```

## Terrain Types

| Terrain | Combat Effect | Exploration Effect |
|---------|---------------|-------------------|
| `neutral` | None | None |
| `water_adjacent` | +20% Water jutsu damage | Fishing available |
| `forest` | +15% evasion, -10% accuracy | +10% secret discovery |
| `mist` | Negates ambush advantage | -20% scouting |
| `underground` | -10% accuracy for all | Traps more common |
| `hazardous` | +15% damage taken | -30% rest effectiveness |
| `fortified` | +10% enemy Willpower | Traps common |
| `corrupted` | -30% healing, +20% dark damage | Dark events available |
| `sacred` | +20% healing, +20% light damage | Light events available |

## Location Flags

```typescript
interface LocationFlags {
  isEntry: boolean;      // True for 1-2 starting locations
  isBoss: boolean;       // True for final boss location
  isSecret: boolean;     // True for hidden locations
  hasMerchant: boolean;  // Can rooms include merchant?
  hasRest: boolean;      // Can rooms include rest?
  hasTraining: boolean;  // Can rooms include training?
}
```

**Flag Guidelines:**

| Location Type | isEntry | isBoss | isSecret | hasMerchant | hasRest | hasTraining |
|---------------|---------|--------|----------|-------------|---------|-------------|
| Settlement | Maybe | No | No | Yes | Yes | Maybe |
| Wilderness | Maybe | No | No | No | Maybe | No |
| Stronghold | No | No | No | Maybe | No | Maybe |
| Landmark | No | No | No | Maybe | Maybe | Maybe |
| Secret | No | No | **Yes** | Rare | Rare | Maybe |
| Boss | No | **Yes** | No | No | No | No |

## Unlock Conditions (Secrets Only)

```typescript
interface UnlockCondition {
  type: 'intel' | 'item' | 'karma' | 'story_flag' | 'always';
  requirement: string | number;
}

// Examples:
{ type: 'intel', requirement: 'secret_discovered' }
{ type: 'item', requirement: 'sunken_key' }
{ type: 'karma', requirement: -50 }  // Dark karma < -50
{ type: 'story_flag', requirement: 'rescued_tazuna' }
```

## Location Template

```typescript
const newLocation: Location = {
  id: 'location_id',
  name: 'Location Name',
  type: 'wilderness',
  icon: '🌲',
  danger: 3,

  terrain: 'forest',
  terrainEffects: [{ type: 'evasion_bonus', value: 0.15 }],

  description: 'Atmospheric description of the location.',
  enemyPool: ['bandit', 'wolf', 'rogue_ninja'],
  lootTable: 'forest_loot',

  atmosphereEvents: ['rustling_leaves', 'hidden_cache'],
  tiedStoryEvents: ['encounter_tazuna'],

  intelMission: {
    elite: { id: 'forest_guardian', level: 4 },
    flavorText: 'A masked figure blocks the forest path...',
    skipAllowed: true,
    intelReward: {
      revealedPaths: [/* path info */],
      loopHint: 'Hidden trail back to the docks...'
    }
  },

  forwardPaths: ['forest_to_village', 'forest_to_cave'],
  loopPaths: ['forest_to_docks'],

  flags: {
    isEntry: false,
    isBoss: false,
    isSecret: false,
    hasMerchant: false,
    hasRest: true,
    hasTraining: false
  }
};
```

## Validation Checklist

- [ ] Has unique id and name
- [ ] Has valid type from LocationType enum
- [ ] Danger level 1-7 appropriate for column
- [ ] Terrain assigned and matches theme
- [ ] Has 1-3 forward paths (except boss = 0)
- [ ] Intel mission defined with elite or boss
- [ ] Flags consistent with type
- [ ] Secret locations have unlockCondition
- [ ] Enemy pool matches location theme
