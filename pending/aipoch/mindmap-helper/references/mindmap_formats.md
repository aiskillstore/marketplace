# Mind Map Document Formats and Examples

## Markdown Template (Default)

Use unordered lists and indentation to represent hierarchy:

```markdown
- Topic
  - Level 1 Branch A
    - Level 2 Branch A1
      - Level 3 Branch A1a
  - Level 1 Branch B
    - Level 2 Branch B1
```

## JSON Template

Basic structure:

```json
{
  "title": "Topic",
  "children": [
    {
      "title": "Level 1 Branch A",
      "children": [
        {
          "title": "Level 2 Branch A1",
          "children": [
            {"title": "Level 3 Branch A1a", "children": []}
          ]
        }
      ]
    },
    {
      "title": "Level 1 Branch B",
      "children": [
        {"title": "Level 2 Branch B1", "children": []}
      ]
    }
  ]
}
```

Optional fields (add only when requested by the user):

- `id`: String, ensures uniqueness at the same level
- `notes`: Node description
- `tags`: String array

Example:

```json
{
  "title": "Project Planning",
  "children": [
    {
      "title": "Objectives",
      "children": [
        {"title": "Scope", "children": [], "notes": "Clarify what not to do"}
      ]
    },
    {
      "title": "Milestones",
      "children": [
        {"title": "Project Initiation", "children": [], "id": "m1"},
        {"title": "Acceptance", "children": [], "id": "m2"}
      ]
    }
  ]
}
```

## Output Checklist

- Only one root node
- All `children` are arrays
- Hierarchy depth meets requirements
- Consistent naming style at the same level (primarily noun phrases)