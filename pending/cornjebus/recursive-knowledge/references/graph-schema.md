# Knowledge Graph Schema

## Entity Types

| Type | Description | Example |
|------|-------------|---------|
| `person` | Individual human | "John Smith", "CEO Jane Doe" |
| `organization` | Company, agency, group | "Anthropic", "FBI", "MIT" |
| `concept` | Idea, technology, method, product | "Machine Learning", "CrimeMiner", "OAuth" |
| `date` | Specific date or time period | "Q3 2024", "January 15, 2025" |
| `location` | Place, address | "San Francisco", "Building 42" |
| `event` | Named event, conference, incident | "IACP Conference", "Product Launch" |

## Relationship Types

| Type | Description | Typical Source → Target |
|------|-------------|------------------------|
| `works_with` | Professional collaboration | person → person |
| `works_for` | Employment | person → organization |
| `created` | Made or produced | person/org → concept |
| `references` | Mentions or cites | any → any |
| `supports` | Agrees with, backs | concept → concept |
| `contradicts` | Disagrees with | concept → concept |
| `located_in` | Geographic relationship | any → location |
| `part_of` | Component or member | any → any |
| `occurred_at` | Event timing/location | event → date/location |
| `related_to` | General relationship | any → any |

## Entity Structure

```json
{
  "id": "ent_a1b2c3d4e5f6",
  "type": "person",
  "name": "John Smith",
  "aliases": ["J. Smith", "Dr. Smith"],
  "attributes": {
    "role": "CEO",
    "department": "Executive"
  },
  "source_docs": ["doc_123", "doc_456"],
  "extraction_confidence": 0.95
}
```

## Relationship Structure

```json
{
  "id": "rel_x1y2z3",
  "type": "works_for",
  "source_entity_id": "ent_a1b2c3d4e5f6",
  "target_entity_id": "ent_org123",
  "attributes": {
    "details": "Since 2020",
    "role": "CEO"
  },
  "source_docs": ["doc_123"],
  "extraction_confidence": 0.90
}
```

## ID Generation

IDs are deterministic based on content:
- Entities: `ent_` + hash of lowercase name
- Relationships: `rel_` + hash of source-type-target
- Documents: `doc_` + hash of file path

This ensures:
- Same entity from different docs gets same ID
- Relationships are deduplicated automatically
- Incremental indexing works correctly
