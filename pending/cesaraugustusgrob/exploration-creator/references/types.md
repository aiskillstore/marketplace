# TypeScript Type Definitions

Complete type definitions for the exploration system.

## Core Types

```typescript
type LocationId = string;
type PathId = string;
type EventId = string;
type EnemyId = string;
type RegionId = string;
type LootTableId = string;

type LocationType =
  | 'settlement'
  | 'wilderness'
  | 'stronghold'
  | 'landmark'
  | 'secret'
  | 'boss';

type TerrainType =
  | 'neutral'
  | 'water_adjacent'
  | 'forest'
  | 'mist'
  | 'underground'
  | 'hazardous'
  | 'fortified'
  | 'corrupted'
  | 'sacred';

type ActivityType =
  | 'combat'
  | 'event'
  | 'merchant'
  | 'rest'
  | 'treasure'
  | 'training'
  | 'story_event';

type PathType =
  | 'forward'
  | 'branch'
  | 'loop'
  | 'secret'
  | 'boss';
```

## Region Types

```typescript
interface Region {
  id: string;
  name: string;
  theme: string;
  description: string;

  // Navigation
  entryPoints: LocationId[];
  bossLocation: LocationId;

  // Content
  locations: Location[];
  paths: Path[];

  // Enemies
  enemyPool: Enemy[];
  elitePool: Elite[];
  boss: Boss;

  // Loot
  lootTheme: LootTheme;

  // Story
  storyTrees: StoryTree[];
}

interface LootTheme {
  primaryElement: ElementType;
  equipmentFocus: string[];
  goldMultiplier: number;
}
```

## Location Types

```typescript
interface Location {
  // Identity
  id: string;
  name: string;
  type: LocationType;
  icon: string;

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
  atmosphereEvents: EventId[];
  tiedStoryEvents?: EventId[];

  // Room 10
  intelMission: IntelMission;

  // Navigation
  forwardPaths: PathId[];
  loopPaths?: PathId[];
  secretPaths?: PathId[];

  // Flags
  flags: LocationFlags;

  // Secret unlock
  unlockCondition?: UnlockCondition;
}

interface LocationFlags {
  isEntry: boolean;
  isBoss: boolean;
  isSecret: boolean;
  hasMerchant: boolean;
  hasRest: boolean;
  hasTraining: boolean;
}

interface TerrainEffect {
  type: string;
  value: number;
}
```

## Room Types

```typescript
interface Room {
  index: number;
  activity: ActivityType | 'intel_mission';
  connections: number[];
  completed: boolean;
  data: RoomData | null;
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

interface MerchantData {
  type: 'merchant';
  inventory: Item[];
  buyModifier: number;
  sellModifier: number;
}

interface RestData {
  type: 'rest';
  hpRestore: number;
  chakraRestore: number;
}

interface TreasureData {
  type: 'treasure';
  lootTable: LootTableId;
  trapped: boolean;
}

interface TrainingData {
  type: 'training';
  statOptions: PrimaryStat[];
  bonusAmount: number;
}

interface StoryEventData {
  type: 'story_event';
  eventId: EventId;
  choices: EventChoice[];
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

## Intel Types

```typescript
interface IntelMission {
  elite?: EliteEnemy;
  boss?: BossEnemy;
  flavorText: string;
  skipAllowed: boolean;
  intelReward: IntelReward | null;
  lootReward?: LootTableId;
}

interface IntelReward {
  revealedPaths: PathInfo[];
  secretHint?: string;
  loopHint?: string;
  bossInfo?: string;
}

interface PathInfo {
  pathId: PathId;
  destinationName: string;
  destinationIcon: string;
  dangerLevel: number;
  hint: string;
}
```

## Path Types

```typescript
interface Path {
  id: PathId;
  from: LocationId;
  to: LocationId;
  type: PathType;
  hidden: boolean;
  unlockCondition?: UnlockCondition;
}

interface LoopPath extends Path {
  type: 'loop';
  loopDescription: string;
  oneTimeUse: boolean;
}

interface UnlockCondition {
  type: 'intel' | 'item' | 'karma' | 'story_flag' | 'always';
  requirement: string | number;
}
```

## Navigation State Types

```typescript
interface NavigationState {
  currentRegion: RegionId;
  currentLocation: LocationId;
  currentRoom: number;

  visitedLocations: Set<LocationId>;
  completedRooms: Map<LocationId, Set<number>>;

  hasIntel: boolean;
  revealedPaths: Set<PathId>;
  discoveredSecrets: Set<LocationId>;
  availableLoops: Set<PathId>;

  availablePaths: PathId[];
}
```

## Enemy Types

```typescript
interface EliteEnemy {
  id: string;
  name: string;
  level: number;
  hp: number;
  skills: string[];
  element: ElementType;
}

interface BossEnemy extends EliteEnemy {
  title: string;
  phases?: BossPhase[];
}

interface BossPhase {
  hpThreshold: number;
  skills: string[];
  buffs?: Buff[];
}
```

## Activity Weights

```typescript
interface ActivityWeights {
  combat: number;
  event: number;
  merchant: number;
  rest: number;
  treasure: number;
  training: number;
  story_event: number;
}

const BASE_WEIGHTS: ActivityWeights = {
  combat: 40,
  event: 25,
  merchant: 10,
  rest: 8,
  treasure: 8,
  training: 5,
  story_event: 4
};
```

## Constants

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
  10: []
};

const ROOMS_PER_LOCATION = 10;
const PLAYER_PATH_LENGTH = 5;
const MIN_LOCATIONS_PER_REGION = 10;
const MAX_LOCATIONS_PER_REGION = 15;
const MAX_LOOPS_PER_LOCATION = 2;
```
