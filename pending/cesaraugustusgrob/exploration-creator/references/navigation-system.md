# Navigation System

Paths connect locations. Intel determines whether the player chooses or fate decides.

## Path Types

| Type | Direction | Discovery | Description |
|------|-----------|-----------|-------------|
| `forward` | One-way → | Always visible | Standard progression |
| `branch` | One-way → | Always visible | Alternative forward route |
| `loop` | One-way ← | Via intel hint | Returns to earlier location |
| `secret` | One-way → | Via intel/item/karma | Leads to hidden location |
| `boss` | One-way → | Always visible | Final path to boss |

## Path Data Structure

```typescript
interface Path {
  id: string;
  from: LocationId;
  to: LocationId;
  type: PathType;

  // Visibility
  hidden: boolean;                // Shown on map?

  // Unlock requirements (for hidden paths)
  unlockCondition?: UnlockCondition;
}

interface UnlockCondition {
  type: 'intel' | 'item' | 'karma' | 'story_flag' | 'always';
  requirement: string | number;
}

type PathType = 'forward' | 'branch' | 'loop' | 'secret' | 'boss';
```

## Navigation Rules

1. **Forward Only** - Cannot return to visited locations (without loop)
2. **Visited = Blocked** - Once you leave a location, it's closed
3. **Intel = Choice** - With intel, pick your path
4. **No Intel = Random** - Game picks randomly from available paths
5. **Loops are One-Time** - Loop paths disappear after use
6. **Boss Ends Region** - Defeating boss completes the region

## Navigation State

```typescript
interface NavigationState {
  // Current position
  currentRegion: RegionId;
  currentLocation: LocationId;
  currentRoom: number;            // 1-10

  // History
  visitedLocations: Set<LocationId>;
  completedRooms: Map<LocationId, Set<number>>;

  // Intel state
  hasIntel: boolean;
  revealedPaths: Set<PathId>;
  discoveredSecrets: Set<LocationId>;
  availableLoops: Set<PathId>;

  // Available moves
  availablePaths: PathId[];       // What player can access next
}
```

## Path Selection Logic

```typescript
function selectNextPath(
  state: NavigationState,
  availablePaths: Path[]
): LocationId | null {

  if (state.hasIntel) {
    // Player chooses - return null and let UI handle selection
    return null; // UI will show path selection screen
  } else {
    // Random selection
    const randomIndex = Math.floor(Math.random() * availablePaths.length);
    return availablePaths[randomIndex].to;
  }
}

function getAvailablePaths(
  currentLocation: LocationId,
  allPaths: Path[],
  visitedLocations: Set<LocationId>,
  revealedSecrets: Set<PathId>,
  availableLoops: Set<PathId>
): Path[] {

  return allPaths.filter(path => {
    // Must start from current location
    if (path.from !== currentLocation) return false;

    // Forward paths to unvisited locations
    if (path.type === 'forward' || path.type === 'branch' || path.type === 'boss') {
      return !visitedLocations.has(path.to);
    }

    // Secret paths if revealed
    if (path.type === 'secret') {
      return revealedSecrets.has(path.id) && !visitedLocations.has(path.to);
    }

    // Loop paths if discovered (lead to visited locations)
    if (path.type === 'loop') {
      return availableLoops.has(path.id);
    }

    return false;
  });
}
```

---

# Loop System

Loops allow players to **return to earlier locations** for extended exploration.

## Loop Purpose

- Missed content or story events
- Resource farming
- Secret discovery
- Extended exploration

## Loop Discovery

Loops are **hidden by default**. They are revealed as **hints** when defeating elites:

```
┌─────────────────────────────────────────────────────────────────┐
│                      INTEL GATHERED                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FORWARD PATHS:                                                 │
│  ├─ 🏘️ Village (Danger: ⚠️) - Safe haven                        │
│  └─ 🕳️ Cave (Danger: ⚠️⚠️⚠️⚠️) - Rare loot                        │
│                                                                 │
│  ↩️ LOOP DISCOVERED:                                            │
│  └─ ⚓ Docks - "Hidden trail back through the forest"           │
│                                                                 │
│  💡 SECRET HINT:                                                │
│  └─ "Smugglers speak of a sunken ship off the coast..."        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Loop Rules

1. **Lead to visited locations** - Loops go backward, not forward
2. **Reset location rooms** - Activities regenerate (new merchants, combats, etc.)
3. **Story events don't repeat** - Already-seen story stays completed
4. **One-time use** - Loop path disappears after taking it
5. **Maximum 2 loops per location** - Don't overwhelm with options
6. **Optional** - Player never needs loops to reach boss

## Loop Data Structure

```typescript
interface LoopPath extends Path {
  type: 'loop';

  // Loop-specific
  loopDescription: string;        // "Secret tunnel through the caves"
  oneTimeUse: boolean;            // Usually true

  unlockCondition: {
    type: 'intel';
    requirement: 'loop_discovered';
  };
}
```

## Path Template

```typescript
// Forward path
const forwardPath: Path = {
  id: 'forest_to_village',
  from: 'coastal_forest',
  to: 'fishing_village',
  type: 'forward',
  hidden: false
};

// Loop path
const loopPath: Path = {
  id: 'forest_to_docks',
  from: 'coastal_forest',
  to: 'the_docks',
  type: 'loop',
  hidden: true,
  unlockCondition: { type: 'intel', requirement: 'loop_discovered' },
  loopDescription: 'Hidden trail back through the forest',
  oneTimeUse: true
};

// Secret path
const secretPath: Path = {
  id: 'beach_to_ship',
  from: 'misty_beach',
  to: 'sunken_ship',
  type: 'secret',
  hidden: true,
  unlockCondition: { type: 'item', requirement: 'sunken_key' }
};

// Boss path
const bossPath: Path = {
  id: 'outpost_to_compound',
  from: 'bandit_outpost',
  to: 'goro_compound',
  type: 'boss',
  hidden: false
};
```

## Validation Checklist

- [ ] All paths have valid from/to locations
- [ ] No orphan locations (unreachable)
- [ ] Loop paths lead to earlier (visited) locations
- [ ] Secret paths have unlockCondition
- [ ] Boss paths only lead to boss location
- [ ] Maximum 2-3 forward paths per location
- [ ] At least 2 paths lead to boss location
