# EDN Analyzer - Examples

This file contains example analyses and use cases for the EDN Analyzer skill.

## Example 1: Basic Template Analysis

**User Request:**
> "Analyze build/logseq_db_Templates_full.edn"

**Output:**
```
📊 Template Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Classes: 632
Total Properties: 1,033
File Size: 497 KB
Lines: 15,422

Property Types:
┌──────────────┬───────┬─────────┐
│ Type         │ Count │ Percent │
├──────────────┼───────┼─────────┤
│ :default     │   620 │  60.0%  │
│ :node        │   280 │  27.1%  │
│ :date        │    89 │   8.6%  │
│ :url         │    32 │   3.1%  │
│ :number      │    12 │   1.2%  │
└──────────────┴───────┴─────────┘

Cardinality Distribution:
┌──────────────┬───────┬─────────┐
│ Cardinality  │ Count │ Percent │
├──────────────┼───────┼─────────┤
│ :one         │   748 │  72.4%  │
│ :many        │   285 │  27.6%  │
└──────────────┴───────┴─────────┘

Top Class Hierarchies:
1. Thing → Person (2 classes, 36 properties)
2. Thing → Organization (4 classes, 15 properties)
3. Thing → CreativeWork (14 classes, 7 properties)
4. Thing → Event (17 classes, 6 properties)
5. Thing → Place (2 classes, 9 properties)

✅ No issues found
```

---

## Example 2: Finding Orphaned Classes

**User Request:**
> "Find orphaned classes in the full template"

**Output:**
```
🔍 Orphaned Classes Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Found 2 orphaned classes (missing :build/class-parent):

1. Schedule
   Location: source/intangible/classes.edn:145
   Current parent: (none)
   → Suggestion: Add :build/class-parent :user.class/Intangible-abc123

2. ProductCategory
   Location: source/product/classes.edn:67
   Current parent: (none)
   → Suggestion: Add :build/class-parent :user.class/DefinedTerm-def456

Note: Thing and Agent classes are root classes and don't need parents.

Would you like me to fix these automatically?
```

---

## Example 3: Comparing Template Variants

**User Request:**
> "Compare the full and CRM templates"

**Output:**
```
📋 Variant Comparison: Full vs CRM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overview:
┌──────────────┬──────┬─────┬────────┬──────────┐
│ Template     │ Size │ Cls │ Props  │ Modules  │
├──────────────┼──────┼─────┼────────┼──────────┤
│ Full         │ 497K │ 632 │ 1,033  │ All (11) │
│ CRM          │ 298K │   8 │   240  │ 4        │
└──────────────┴──────┴─────┴────────┴──────────┘

Size Reduction: 40% smaller (199 KB saved)

CRM Includes:
✅ base/ - Thing, Agent
✅ person/ - Person, PersonalRelationship
✅ organization/ - Organization, Corporation, NGO, LocalBusiness
✅ common/ - All shared properties (189 props)

CRM Excludes:
❌ creative-work/ - 14 classes
❌ event/ - 17 classes
❌ place/ - 2 classes
❌ product/ - 1 class
❌ intangible/ - 9 classes
❌ action/ - 1 class
❌ misc/ - 82 classes

Key CRM Properties:
- Person: jobTitle, email, telephone, worksFor, colleague
- Organization: legalName, employee, member, founder, department
- PersonalRelationship: knows, spouse, parent, children, sibling

Use Case: CRM template is optimized for customer relationship
management, focusing on people and organizations while excluding
creative works, events, and other general-purpose classes.
```

---

## Example 4: Property Distribution Analysis

**User Request:**
> "Show property type distribution by module"

**Output:**
```
📊 Property Types by Module
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────┬─────────┬──────┬──────┬──────┬────────┐
│ Module          │ Default │ Node │ Date │ URL  │ Number │
├─────────────────┼─────────┼──────┼──────┼──────┼────────┤
│ common/         │     145 │   32 │    8 │    3 │      1 │
│ person/         │      18 │   12 │    4 │    1 │      1 │
│ organization/   │       8 │    5 │    1 │    1 │      0 │
│ creative-work/  │       4 │    2 │    1 │    0 │      0 │
│ event/          │       3 │    1 │    2 │    0 │      0 │
│ place/          │       5 │    2 │    0 │    2 │      0 │
│ product/        │       1 │    1 │    0 │    0 │      0 │
│ intangible/     │       6 │    2 │    1 │    0 │      0 │
│ action/         │       1 │    0 │    0 │    0 │      0 │
│ misc/           │      38 │   15 │    4 │    2 │      0 │
└─────────────────┴─────────┴──────┴──────┴──────┴────────┘

Insights:
- common/ module has most properties (189 total)
- :node type used heavily in person/ (33% of properties)
- :date type concentrated in event/ module (33%)
- :url type mostly in common/ and place/ modules
- :number type rarely used (1.2% overall)
```

---

## Example 5: Finding Duplicate IDs

**User Request:**
> "Check for duplicate IDs in the template"

**Output:**
```
🔍 Duplicate ID Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scanning 632 classes and 1,033 properties...

✅ No duplicate IDs found

All IDs are unique:
- Class IDs: 632 unique
- Property IDs: 1,033 unique
- Total IDs: 1,665 unique

ID Format Check:
✅ All class IDs follow pattern: :user.class/ClassName-RandomID
✅ All property IDs follow pattern: :user.property/propertyName-RandomID
✅ All random suffixes are unique (8 characters)
```

---

## Example 6: Class Hierarchy Analysis

**User Request:**
> "Show the complete hierarchy for Person class"

**Output:**
```
🌳 Class Hierarchy: Person
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thing (base)
└── Person
    └── PersonalRelationship

Person Details:
- Location: source/person/classes.edn:12
- ID: :user.class/Person-xY9zK
- Parent: :user.class/Thing-aB1cD
- Properties: 36 total
  - Direct: 28 (jobTitle, email, telephone, etc.)
  - Inherited: 8 (from Thing: name, description, url, etc.)

Person Properties:
1. jobTitle (text, :one)
2. email (text, :one)
3. telephone (text, :one)
4. birthDate (date, :one)
5. spouse (node, :many)
6. worksFor (node, :many)
7. colleague (node, :many)
... (29 more)

Child Classes:
1. PersonalRelationship
   - Properties: 12 (knows, parent, children, sibling, etc.)
   - Inherits all Person properties

Total Tree Size: 48 properties across 2 classes
```

---

## Example 7: Property Usage Analysis

**User Request:**
> "Which classes use the 'email' property?"

**Output:**
```
🔍 Property Usage: email
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Property Definition:
- ID: :user.property/email-pQ2rS
- Location: source/person/properties.edn:45
- Type: :default (text)
- Cardinality: :one
- Description: "Email address"

Used by 3 classes:
1. Person (source/person/classes.edn:12)
   - Direct assignment

2. Organization (source/organization/classes.edn:23)
   - Direct assignment

3. PersonalRelationship (source/person/classes.edn:78)
   - Inherited from Person

Total usage: 3 classes
Direct: 2 classes
Inherited: 1 class
```

---

## Example 8: Module Size Analysis

**User Request:**
> "Are modules balanced in size?"

**Output:**
```
📊 Module Size Balance
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────┬───────┬────────┬─────────┬──────────┐
│ Module          │ Cls   │ Props  │ Ratio   │ Status   │
├─────────────────┼───────┼────────┼─────────┼──────────┤
│ base/           │     2 │      0 │    0.0  │ ✅ Small  │
│ person/         │     2 │     36 │   18.0  │ ✅ Good   │
│ organization/   │     4 │     15 │    3.8  │ ✅ Good   │
│ event/          │    17 │      6 │    0.4  │ ✅ Good   │
│ creative-work/  │    14 │      7 │    0.5  │ ✅ Good   │
│ place/          │     2 │      9 │    4.5  │ ✅ Good   │
│ product/        │     1 │      2 │    2.0  │ ⚠️  Small │
│ intangible/     │     9 │      9 │    1.0  │ ✅ OK     │
│ action/         │     1 │      1 │    1.0  │ ⚠️  Small │
│ common/         │     0 │    189 │    ∞    │ ✅ Good   │
│ misc/           │    82 │     59 │    0.7  │ ❌ Bloat  │
└─────────────────┴───────┴────────┴─────────┴──────────┘

Issues Found:
❌ misc/ is bloated (82 classes = 61% of total)
   Recommended: Split into focused modules

⚠️  product/ and action/ are small (1 class each)
   Options: Expand or merge into other modules

Recommendation: See module-health skill for detailed reorg plan
```

---

## Example 9: Cardinality Patterns

**User Request:**
> "Show all properties with :many cardinality in person module"

**Output:**
```
🔍 :many Cardinality Properties in person/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found 8 properties:

1. spouse
   - Type: :node
   - Classes: Person, PersonalRelationship
   - Reason: Support multiple marriages

2. colleague
   - Type: :node
   - Classes: Person
   - Reason: Multiple work relationships

3. knows
   - Type: :node
   - Classes: PersonalRelationship
   - Reason: Multiple acquaintances

4. parent
   - Type: :node
   - Classes: PersonalRelationship
   - Reason: Two parents

5. children
   - Type: :node
   - Classes: PersonalRelationship
   - Reason: Multiple children

6. sibling
   - Type: :node
   - Classes: PersonalRelationship
   - Reason: Multiple siblings

7. worksFor
   - Type: :node
   - Classes: Person
   - Reason: Multiple jobs/employers

8. memberOf
   - Type: :node
   - Classes: Person
   - Reason: Multiple memberships

Pattern: All are :node type (relationship to other entities)
Use case: Modeling many-to-many relationships
```

---

## Example 10: Template Growth Analysis

**User Request:**
> "How has the template grown over time?"

**Output:**
```
📈 Template Growth Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analyzing git history...

Version History:
┌──────────┬──────┬────────┬────────┬────────────┐
│ Version  │ Cls  │ Props  │ Lines  │ Date       │
├──────────┼──────┼────────┼────────┼────────────┤
│ v0.1.0   │   12 │     45 │    850 │ 2024-09-01 │
│ v0.2.0   │   85 │    215 │  3,200 │ 2024-10-15 │
│ v0.3.0   │  245 │    485 │  7,100 │ 2024-11-20 │
│ v0.4.0   │  450 │    750 │ 11,500 │ 2025-01-10 │
│ v0.5.0   │  632 │  1,033 │ 15,422 │ 2025-02-28 │
└──────────┴──────┴────────┴────────┴────────────┘

Growth Rate:
- Classes: 5166% increase over 6 months
- Properties: 2196% increase
- Average: +104 classes/month, +165 props/month

Recent Additions (last 30 days):
- creative-work/ module: +14 classes
- event/ module: +17 classes
- misc/ module: +45 classes (needs reorg)

Trend: Rapid growth, moving toward modular architecture
```

---

## Quick Command Reference

| Analysis Type | Example Command |
|---------------|-----------------|
| Basic stats | "Analyze build/logseq_db_Templates_full.edn" |
| Find orphans | "Find orphaned classes" |
| Compare variants | "Compare full and CRM templates" |
| Type distribution | "Show property type distribution" |
| Check duplicates | "Check for duplicate IDs" |
| Class hierarchy | "Show hierarchy for Person class" |
| Property usage | "Which classes use email property?" |
| Module balance | "Are modules balanced?" |
| Cardinality | "Show :many properties in person/" |
| Growth analysis | "How has the template grown?" |

---

## Common Patterns

### Count Items
```
"How many classes are in the template?"
"Count properties by type"
"Show module sizes"
```

### Find Issues
```
"Find orphaned classes"
"Check for duplicate IDs"
"Find missing descriptions"
```

### Compare
```
"Compare full and CRM templates"
"What's different between v0.4 and v0.5?"
"Show size differences across variants"
```

### Analyze Structure
```
"Show class hierarchy"
"Map property usage"
"Analyze module dependencies"
```

### Quality Checks
```
"Check template quality"
"Validate EDN structure"
"Find inconsistencies"
```
