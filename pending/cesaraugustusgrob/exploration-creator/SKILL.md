---
name: exploration-creator
description: Create exploration content for SHINOBI WAY game with node-based path navigation. Use when user wants to add new regions, locations, room layouts, intel missions, path networks, or exploration mechanics. Guides through the Region→Location→Room hierarchy with intel-gated path choices. (project)
---

# Exploration System Creator

Create exploration content for SHINOBI WAY: THE INFINITE TOWER following the node-based navigation system with intel-gated path choices.

## Core Hierarchy

```
REGION (e.g., Land of Waves)
├── LOCATION × 10-15 (e.g., The Docks, Fishing Village)
│   ├── ROOM × 10 per location (1→2→4→2→1 branching)
│   │   ├── Rooms 1-9: Random activities (combat, event, merchant, etc.)
│   │   └── Room 10: INTEL MISSION (always elite fight)
│   └── PATHS (connections to other locations)
└── BOSS (final destination)
```

## Key Mechanics

| Mechanic | Description |
|----------|-------------|
| **Forward-Only** | Cannot backtrack to previous locations (roguelike style) |
| **Path Choice** | With intel: choose path. Without: random destination |
| **Intel Mission** | Room 10 elite fight. Win = intel. Skip = random path |
| **Loops** | Special paths back to earlier locations (discovered via intel) |
| **Secrets** | Hidden locations unlocked by intel, items, karma, or story |

## Workflow

### Step 1: Design Region

Define the region's identity:

```typescript
const region: Region = {
  id: 'region_id',
  name: 'Region Name',
  theme: 'Narrative theme description',
  description: 'Atmospheric description',
  entryPoints: ['location_1', 'location_2'],  // 1-2 starting locations
  bossLocation: 'boss_location_id',
  lootTheme: {
    primaryElement: ElementType.WATER,
    equipmentFocus: ['speed', 'dexterity'],
    goldMultiplier: 0.8
  }
};
```

See [region-system.md](references/region-system.md) for complete region structure.

### Step 2: Plan Locations (10-15)

Map locations with danger progression:

| Column | Stage | Danger | Location Count |
|--------|-------|--------|----------------|
| 0 | Entry | 1-2 | 1-2 locations |
| 1 | Early | 3-4 | 2-3 locations |
| 2 | Mid | 4-5 | 3-4 locations |
| 3 | Late | 5-6 | 2-3 locations |
| 4 | Boss | 7 | 1 location |

**Location Types:**

| Type | Combat | Merchant | Rest | Focus |
|------|--------|----------|------|-------|
| `settlement` | Low | Yes | Yes | Story, social |
| `wilderness` | Medium | No | Maybe | Exploration |
| `stronghold` | High | Maybe | No | Heavy combat |
| `landmark` | Medium | Maybe | Maybe | Balanced, story |
| `secret` | Varies | Rare | Rare | Unique rewards |
| `boss` | BOSS | No | No | Final encounter |

See [location-system.md](references/location-system.md) for location data structure and terrain types.

### Step 3: Define Room Activities

Each location has 10 rooms in a 1→2→4→2→1 branching structure. Player visits 5 rooms per location.

**Activity Weights (Rooms 1-9 only):**

| Activity | Weight | Description |
|----------|--------|-------------|
| `combat` | 40% | Fight enemies from location pool |
| `event` | 25% | Atmosphere event with choices |
| `merchant` | 10% | Buy/sell (max 1 per location) |
| `rest` | 8% | Recover HP/Chakra (max 1 per location) |
| `treasure` | 8% | Loot chest |
| `training` | 5% | Permanent stat upgrade |
| `story_event` | 4% | Narrative from story tree |

**Room 10 is ALWAYS an Intel Mission** - elite fight or boss.

See [room-system.md](references/room-system.md) for room layout and connections.

### Step 4: Configure Intel Missions

Every location's Room 10 contains an Intel Mission:

```
Player reaches Room 10 → FIGHT or SKIP
├── FIGHT → Win → Intel + Loot → CHOOSE next path
├── FIGHT → Lose → Game Over
└── SKIP → No rewards → RANDOM next path
```

**Elite scaling by location type:**

| Location Type | Elite Level | Notes |
|---------------|-------------|-------|
| Settlement | 2-3 | Guards, spies |
| Wilderness | 3-5 | Beasts, bandits |
| Stronghold | 5-7 | Commanders |
| Landmark | 4-5 | Guardians |
| Secret | 4-7 | Unique elites |
| Boss | 8-10 | **Cannot skip** |

See [intel-mission-system.md](references/intel-mission-system.md) for intel rewards and boss handling.

### Step 5: Map Path Network

Define connections between locations:

**Path Types:**

| Type | Direction | Discovery | Description |
|------|-----------|-----------|-------------|
| `forward` | → | Always visible | Standard progression |
| `branch` | → | Always visible | Alternative route |
| `loop` | ← | Via intel hint | Return to earlier location |
| `secret` | → | Via intel/item/karma | Hidden location access |
| `boss` | → | Always visible | Final path to boss |

**Navigation Rules:**
1. Forward-only (except loops)
2. Visited locations are closed
3. Intel = player chooses path
4. No intel = random destination
5. Loops are one-time use
6. Boss completes region

See [navigation-system.md](references/navigation-system.md) for path data structures and loop system.

### Step 6: Validate

**Region Checklist:**
- [ ] 10-15 locations total
- [ ] 1-2 entry points (isEntry: true)
- [ ] 1 boss location (isBoss: true)
- [ ] All locations reachable from entry
- [ ] Multiple paths to boss (2-3 minimum)
- [ ] Danger curve: Entry (1-2) → Boss (7)

**Location Checklist:**
- [ ] Unique id and name
- [ ] Valid type and danger level
- [ ] 1-3 forward paths (except boss)
- [ ] Intel mission defined
- [ ] Flags match type

**Room Checklist:**
- [ ] 10 rooms per location
- [ ] Room 10 = intel_mission
- [ ] Max 1 merchant, max 1 rest
- [ ] Connections follow 1→2→4→2→1

See [types.md](references/types.md) for complete TypeScript interfaces.

## Reference Files

- [region-system.md](references/region-system.md) - Region structure and data
- [location-system.md](references/location-system.md) - Location types, terrain, flags
- [room-system.md](references/room-system.md) - 10-room layout and activities
- [intel-mission-system.md](references/intel-mission-system.md) - Elite fights and intel rewards
- [navigation-system.md](references/navigation-system.md) - Paths, loops, secrets
- [types.md](references/types.md) - TypeScript type definitions
- [example-waves.md](references/example-waves.md) - Complete Land of Waves region

## Output Format

Generate TypeScript code for new regions/locations ready to integrate into the game systems.
