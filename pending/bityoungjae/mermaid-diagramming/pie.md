# Pie Chart Reference

Display proportional data in Obsidian.

---

## Basic Syntax

```mermaid
pie
    "Label A" : 40
    "Label B" : 35
    "Label C" : 25
```

**Format:** `"Label" : value`

- Labels must be in double quotes
- Values are numbers (no units or %)
- Percentages calculated automatically from total

---

## Title

Add a title with `title`:

```mermaid
pie title Project Time Distribution
    "Development" : 50
    "Testing" : 30
    "Documentation" : 20
```

---

## showData Option

Display actual values alongside percentages:

```mermaid
pie showData
    title Quarterly Revenue (Million)
    "Q1" : 42
    "Q2" : 50
    "Q3" : 35
    "Q4" : 28
```

---

## Configuration

### Text Position

Adjust label position (0 = center, 1 = edge):

```mermaid
%%{init: {"pie": {"textPosition": 0.7}}}%%
pie showData
    title Server Usage (GB)
    "Database" : 120
    "Application" : 80
    "Cache" : 40
```

### Outer Stroke

Adjust border thickness:

```mermaid
%%{init: {"themeVariables": {"pieOuterStrokeWidth": "5px"}}}%%
pie title With Border
    "A" : 50
    "B" : 50
```

---

## Practical Examples

### Example 1: Market Share

```mermaid
pie showData
    title Browser Market Share
    "Chrome" : 65
    "Safari" : 19
    "Firefox" : 8
    "Edge" : 5
    "Other" : 3
```

### Example 2: Survey Results

```mermaid
pie title Customer Satisfaction
    "Very Satisfied" : 45
    "Satisfied" : 30
    "Neutral" : 15
    "Dissatisfied" : 7
    "Very Dissatisfied" : 3
```

### Example 3: Budget Allocation

```mermaid
pie showData
    title Department Budget
    "Engineering" : 40
    "Marketing" : 25
    "Operations" : 20
    "HR" : 10
    "Other" : 5
```

---

## Obsidian Notes

**Labels**: Must use double quotes (`"`). Single quotes won't work.

**Values**: Use pure numbers only. No `%`, `$`, or units.

**Item Count**: Keep to 7 or fewer segments for readability.

**Zero Values**: Avoid 0 or negative values (may cause rendering issues).

**Special Characters**: Avoid special characters in labels.

**Auto Calculation**: Values don't need to sum to 100. Percentages are calculated from total.

---

## Quick Reference

| Element | Syntax | Example |
|---------|--------|---------|
| Basic | `pie` | `pie` |
| Title | `title text` | `title Budget` |
| Show values | `showData` | `pie showData` |
| Data item | `"label" : value` | `"Sales" : 45` |
| Text position | `%%{init: {"pie": {"textPosition": 0.5}}}%%` | 0-1 range |
| Border width | `%%{init: {"themeVariables": {"pieOuterStrokeWidth": "3px"}}}%%` | Any CSS size |
