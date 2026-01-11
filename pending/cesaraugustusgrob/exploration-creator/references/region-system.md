# Region System

A region is a complete narrative arc containing 10-15 hand-designed locations.

## Region Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         REGION                                  │
├─────────────────────────────────────────────────────────────────┤
│  ENTRY          EARLY         MID           LATE         BOSS  │
│  (Column 0)    (Column 1)   (Column 2)    (Column 3)   (Col 4) │
│                                                                 │
│  ┌──────┐      ┌──────┐     ┌──────┐      ┌──────┐    ┌──────┐ │
│  │Docks │─────►│Forest│────►│Bridge│─────►│Outpost│──►│ GORO │ │
│  └──────┘      └──────┘     └──────┘      └──────┘    │COMPND│ │
│      │             │            │             │        └──────┘ │
│      │         ┌───┴──┐     ┌───┴──┐      ┌───┴──┐        ▲    │
│      ▼         ▼      │     ▼      │      ▼      │        │    │
│  ┌──────┐  ┌──────┐   │ ┌──────┐   │  ┌──────┐   │        │    │
│  │Beach │─►│ Cave │   └►│ Camp │   └─►│Manor │───┼────────┘    │
│  └──────┘  └──────┘     └──────┘      └──────┘   │             │
│      │         │            │                    │             │
│      │     [LOOP]◄──────────┘         ┌──────┐   │             │
│      │                                │Shrine│───┘  (Secret)   │
│      └───────────────────────────────►│  💀  │                 │
│              (Dark Karma path)        └──────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Region Components

| Component | Count | Description |
|-----------|-------|-------------|
| Entry Points | 1-2 | Starting locations |
| Boss Location | 1 | Final destination |
| Regular Locations | 8-12 | Main exploration content |
| Secret Locations | 2-3 | Hidden special content |
| Story Trees | 3 | Narrative event chains |

## Region Data Structure

```typescript
interface Region {
  id: string;
  name: string;
  theme: string;
  description: string;

  // Navigation
  entryPoints: LocationId[];      // 1-2 starting locations
  bossLocation: LocationId;       // Final destination

  // Content
  locations: Location[];          // 12-15 locations
  paths: Path[];                  // All connections

  // Enemies
  enemyPool: Enemy[];
  elitePool: Elite[];
  boss: Boss;

  // Loot
  lootTheme: {
    primaryElement: Element;
    equipmentFocus: string[];
    goldMultiplier: number;
  };

  // Story
  storyTrees: StoryTree[];        // 3 per region
}
```

## Region Definition Template

```typescript
const newRegion: Region = {
  id: 'region_id',
  name: 'Region Display Name',
  theme: 'Core thematic elements: atmosphere, conflict, moral questions',
  description: 'Atmospheric description for the player.',

  entryPoints: ['entry_location_1'],
  bossLocation: 'boss_compound',

  locations: [/* See location-system.md */],
  paths: [/* See navigation-system.md */],

  enemyPool: [/* Region-specific enemies */],
  elitePool: [/* Intel mission elites */],
  boss: {/* Final boss definition */},

  lootTheme: {
    primaryElement: ElementType.WATER,
    equipmentFocus: ['speed', 'dexterity'],
    goldMultiplier: 0.8  // Poor region = less gold
  },

  storyTrees: [/* Narrative chains */]
};
```

## Column Layout

Organize locations into columns for difficulty progression:

| Column | Stage | Danger Range | Purpose |
|--------|-------|--------------|---------|
| 0 | Entry | 1-2 | Safe introduction, tutorials |
| 1 | Early | 3-4 | First real challenges |
| 2 | Mid | 4-5 | Core content, most locations |
| 3 | Late | 5-6 | Pre-boss preparation |
| 4 | Boss | 7 | Final confrontation |

## Validation Checklist

- [ ] Has 10-15 locations total
- [ ] Has 1-2 entry points (isEntry: true)
- [ ] Has exactly 1 boss location (isBoss: true)
- [ ] Boss location has forwardPaths: []
- [ ] All locations reachable from entry points
- [ ] Multiple paths lead to boss (at least 2-3)
- [ ] Difficulty curve: Entry (1-2) → Mid (3-5) → Boss (7)
- [ ] Theme is consistent across locations
- [ ] Loot theme matches region element
