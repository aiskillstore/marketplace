# Room System

Each location contains 10 rooms in a 1→2→4→2→1 branching layout. Players visit exactly 5 rooms per location.

## Room Layout

```
                              ┌─────────────┐
                              │   ROOM 10   │ ◄── INTEL MISSION
                              │ ⚔️ ELITE    │     (Always elite fight)
                              └──────▲──────┘
                                     │
                          ┌──────────┴──────────┐
                          │                     │
                     ┌────┴─────┐         ┌─────┴────┐
                     │  ROOM 8  │         │  ROOM 9  │
                     └────▲─────┘         └────▲─────┘
                          │                    │
        ┌─────────────────┼────────────────────┼─────────────────┐
        │                 │                    │                 │
   ┌────┴────┐      ┌─────┴────┐        ┌──────┴───┐      ┌──────┴───┐
   │ ROOM 4  │      │  ROOM 5  │        │  ROOM 6  │      │  ROOM 7  │
   └────▲────┘      └────▲─────┘        └────▲─────┘      └────▲─────┘
        │                │                   │                 │
        └────────┬───────┴───────────────────┴────────┬────────┘
                 │                                    │
            ┌────┴────┐                         ┌─────┴────┐
            │ ROOM 2  │                         │  ROOM 3  │
            └────▲────┘                         └────▲─────┘
                 │                                   │
                 └─────────────┬─────────────────────┘
                               │
                         ┌─────┴─────┐
                         │  ROOM 1   │ ◄── ENTRY (normal room, NOT safe!)
                         └───────────┘
```

## Room Connections

| Room | Connects To | Layer |
|------|-------------|-------|
| 1 | 2, 3 | Entry |
| 2 | 4, 5 | Split |
| 3 | 6, 7 | Split |
| 4 | 8 | Main |
| 5 | 8, 9 | Main |
| 6 | 8, 9 | Main |
| 7 | 9 | Main |
| 8 | 10 | Converge |
| 9 | 10 | Converge |
| 10 | EXIT | Intel Mission |

```typescript
const ROOM_CONNECTIONS: Record<number, number[]> = {
  1: [2, 3],
  2: [4, 5],
  3: [6, 7],
  4: [8],
  5: [8, 9],
  6: [8, 9],
  7: [9],
  8: [10],
  9: [10],
  10: []  // Exit
};
```

## Player Path

Player visits **5 rooms** per location:

```
Example paths:
1 → 2 → 4 → 8 → 10
1 → 2 → 5 → 9 → 10
1 → 3 → 6 → 8 → 10
1 → 3 → 7 → 9 → 10
```

## Room Activities (Rooms 1-9)

| Activity | Base Weight | Description |
|----------|-------------|-------------|
| `combat` | 40% | Fight enemies from location enemy pool |
| `event` | 25% | Atmosphere event with choices |
| `merchant` | 10% | Buy/sell items (max 1 per location) |
| `rest` | 8% | Recover HP/Chakra (max 1 per location) |
| `treasure` | 8% | Loot chest with rewards |
| `training` | 5% | Permanent stat upgrade (rare) |
| `story_event` | 4% | Narrative event from story tree |

**Room 10 is ALWAYS `intel_mission`** - never random.

## Activity Weight Modifiers

```typescript
function getActivityWeights(location: Location): ActivityWeights {
  const weights = { ...BASE_WEIGHTS };

  // Remove unavailable activities
  if (!location.flags.hasMerchant) weights.merchant = 0;
  if (!location.flags.hasRest) weights.rest = 0;
  if (!location.flags.hasTraining) weights.training = 0;
  if (!location.tiedStoryEvents?.length) weights.story_event = 0;

  // Modify by location type
  switch (location.type) {
    case 'settlement':
      weights.combat = 25;
      weights.event = 35;
      weights.merchant = 15;
      break;
    case 'stronghold':
      weights.combat = 55;
      weights.event = 15;
      break;
    case 'wilderness':
      weights.combat = 40;
      weights.treasure = 12;
      break;
  }

  return normalizeWeights(weights);
}
```

## Room Data Structure

```typescript
interface Room {
  index: number;                  // 1-10
  activity: ActivityType;         // 'combat' | 'event' | ... | 'intel_mission'
  connections: number[];          // Next room indices
  completed: boolean;

  // Activity-specific data
  data: RoomData | null;

  // Results
  rewards?: Reward[];
}

type RoomData =
  | CombatData
  | EventData
  | MerchantData
  | RestData
  | TreasureData
  | TrainingData
  | StoryEventData
  | IntelMissionData;

interface CombatData {
  type: 'combat';
  enemies: Enemy[];
  isAmbush: boolean;
}

interface EventData {
  type: 'event';
  eventId: EventId;
  choices: EventChoice[];
}
```

## Room Generation

```typescript
function generateLocationRooms(location: Location): Room[] {
  const rooms: Room[] = [];

  // Generate rooms 1-9 with random activities
  for (let i = 1; i <= 9; i++) {
    rooms.push(generateNormalRoom(i, location));
  }

  // Room 10 is ALWAYS Intel Mission
  rooms.push(generateIntelRoom(location));

  return rooms;
}

function generateNormalRoom(index: number, location: Location): Room {
  const activity = rollActivity(location);

  return {
    index,
    activity,
    connections: ROOM_CONNECTIONS[index],
    completed: false,
    data: generateActivityData(activity, location),
    rewards: null
  };
}

function generateIntelRoom(location: Location): Room {
  return {
    index: 10,
    activity: 'intel_mission',
    connections: [],  // Exit
    completed: false,
    data: {
      type: 'intel_mission',
      elite: location.intelMission.elite,
      boss: location.intelMission.boss,
      flavorText: location.intelMission.flavorText,
      skipAllowed: location.intelMission.skipAllowed,
      intelReward: location.intelMission.intelReward
    }
  };
}
```

## Validation Checklist

- [ ] Exactly 10 rooms per location
- [ ] Room 10 is ALWAYS intel_mission
- [ ] Connections follow 1→2→4→2→1 structure
- [ ] Max 1 merchant room per location
- [ ] Max 1 rest room per location
- [ ] Story events only if tiedStoryEvents exists
- [ ] Activity weights sum to 100%
