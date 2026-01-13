# Intel Mission System

Room 10 is ALWAYS an Intel Mission. This is the climax of each location.

## Core Concept

The player faces an **Elite Enemy** (or **Boss** at boss locations) with two choices:

1. **FIGHT** the elite → Win = Get Intel → **Choose** your next path
2. **SKIP** the fight → No intel → Next path chosen **randomly**

## Intel Mission Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROOM 10: INTEL MISSION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚔️ [ELITE NAME] blocks your path.                              │
│                                                                 │
│  "Flavor text describing the elite and situation..."            │
│                                                                 │
│  They guard valuable information about the roads ahead.         │
│                                                                 │
│  ┌─────────────────────────────┐  ┌─────────────────────────┐   │
│  │                             │  │                         │   │
│  │        ⚔️ FIGHT             │  │       🚪 SKIP           │   │
│  │                             │  │                         │   │
│  │   Defeat the elite to       │  │   Leave without         │   │
│  │   obtain intel about        │  │   fighting.             │   │
│  │   paths ahead.              │  │                         │   │
│  │                             │  │   Your next destination │   │
│  │   → You choose next path    │  │   will be random.       │   │
│  │   → Elite loot drops        │  │                         │   │
│  │                             │  │   → No rewards          │   │
│  │                             │  │   → No intel            │   │
│  └─────────────────────────────┘  └─────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Fight Outcomes

| Action | Outcome | Result |
|--------|---------|--------|
| **FIGHT → WIN** | Elite defeated | Intel + Loot + **Choose path** |
| **FIGHT → LOSE** | Player dies | Game Over (or flee with penalty) |
| **SKIP** | No combat | No rewards + **Random path** |

## Intel Rewards

When you **defeat the elite**, you receive:

```typescript
interface IntelReward {
  // Primary reward - path visibility
  revealedPaths: PathInfo[];      // All forward paths with details

  // Optional bonuses
  secretHint?: string;            // Hint about secret location
  loopHint?: string;              // Hint about loop path
  bossInfo?: string;              // Info about region boss
}

interface PathInfo {
  pathId: string;
  destinationName: string;
  destinationIcon: string;
  dangerLevel: number;
  hint: string;                   // "Safe haven", "Heavy combat", etc.
}
```

## With Intel vs Without Intel

### With Intel (Player Chooses)

```
┌─────────────────────────────────────────────────────────────────┐
│              ✅ INTEL OBTAINED - CHOOSE YOUR PATH               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Current Location: Coastal Forest 🌲                            │
│                                                                 │
│  Available Paths:                                               │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ 🏘️ FISHING     │  │ 🕳️ SMUGGLER'S  │  │ 🏕️ RIVERSIDE   │    │
│  │    VILLAGE     │  │     CAVE       │  │     CAMP       │    │
│  │                │  │                │  │                │    │
│  │ Danger: ⚠️      │  │ Danger: ⚠️⚠️⚠️⚠️  │  │ Danger: ⚠️⚠️⚠️   │    │
│  │ "Safe haven,   │  │ "Smuggler den, │  │ "Rest spot,    │    │
│  │  story events" │  │  rare loot"    │  │  balanced"     │    │
│  │                │  │                │  │                │    │
│  │   [CHOOSE]     │  │   [CHOOSE]     │  │   [CHOOSE]     │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                 │
│  💡 Secret Hint: "The smugglers know hidden sea routes..."      │
│  ↩️ Loop Hint: "There's a path back through the forest..."      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Without Intel (Random)

```
┌─────────────────────────────────────────────────────────────────┐
│              ❌ NO INTEL - RANDOM DESTINATION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Current Location: Coastal Forest 🌲                            │
│                                                                 │
│  You didn't gather intel about the paths ahead...               │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │                │  │                │  │                │    │
│  │    ❓ ???      │  │    ❓ ???      │  │    ❓ ???      │    │
│  │                │  │                │  │                │    │
│  │   Unknown      │  │   Unknown      │  │   Unknown      │    │
│  │                │  │                │  │                │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                 │
│              🎲 The path will be chosen for you...              │
│                                                                 │
│                      [CONTINUE]                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Intel Mission Data Structure

```typescript
interface IntelMission {
  // The enemy
  elite?: EliteEnemy;              // Normal locations
  boss?: BossEnemy;                // Boss location only

  // Presentation
  flavorText: string;             // "A scarred enforcer blocks the road..."

  // Behavior
  skipAllowed: boolean;           // true for normal, FALSE for boss location

  // Rewards for winning
  intelReward: IntelReward | null;
  lootReward?: LootTableId;
}

interface IntelMissionData {
  type: 'intel_mission';
  elite?: EliteEnemy;
  boss?: BossEnemy;
  flavorText: string;
  skipAllowed: boolean;
  intelReward: IntelReward | null;
}
```

## Elite Scaling by Location Type

| Location Type | Elite Difficulty | Level Range | Notes |
|---------------|------------------|-------------|-------|
| Settlement | Easy | 2-3 | Guards, spies |
| Wilderness | Medium | 3-5 | Beasts, bandits |
| Stronghold | Hard | 5-7 | Commanders, champions |
| Landmark | Medium | 4-5 | Guardians, spirits |
| Secret | Varies | 4-7 | Unique elites |
| Boss | **BOSS** | 8-10 | Region boss, cannot skip |

## Boss Location Special Case

At the **Boss Location** (e.g., Goro's Compound):

- Room 10 contains the **REGION BOSS**, not an elite
- **skipAllowed: false** - Player MUST fight
- Defeating the boss completes the region

```typescript
const bossIntelMission: IntelMission = {
  boss: {
    id: 'goro',
    name: 'Goro',
    title: 'The Tyrant of Waves',
    level: 10,
    hp: 850,
    element: 'water'
  },
  flavorText: 'Goro sits on his throne of stolen wealth. There is no escape.',
  skipAllowed: false,  // MUST FIGHT
  intelReward: null,   // No "next path" - this is the end
  lootReward: 'goro_treasury'
};
```

## Intel Mission Template

```typescript
const locationIntelMission: IntelMission = {
  elite: {
    id: 'elite_id',
    name: 'Elite Name',
    level: 5,
    hp: 200,
    skills: ['skill_1', 'skill_2'],
    element: ElementType.WATER
  },
  flavorText: 'Atmospheric description of the confrontation...',
  skipAllowed: true,
  intelReward: {
    revealedPaths: [
      {
        pathId: 'path_1',
        destinationName: 'Fishing Village',
        destinationIcon: '🏘️',
        dangerLevel: 1,
        hint: 'Safe haven, story events'
      },
      {
        pathId: 'path_2',
        destinationName: 'Smuggler Cave',
        destinationIcon: '🕳️',
        dangerLevel: 4,
        hint: 'Dangerous, rare loot'
      }
    ],
    secretHint: 'The smugglers speak of sunken treasure...',
    loopHint: 'A hidden trail leads back to the docks...'
  },
  lootReward: 'elite_loot_table'
};
```

## Validation Checklist

- [ ] Has elite OR boss defined (not both)
- [ ] Boss locations have boss, not elite
- [ ] Boss locations have skipAllowed: false
- [ ] Has flavorText describing the encounter
- [ ] intelReward has revealedPaths (except boss)
- [ ] Elite level matches location danger
- [ ] Loot reward defined
