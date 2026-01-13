---
name: module-health
description: Modular architecture health assessor for Logseq Template Graph. Analyzes module balance, cohesion, size distribution, and dependencies. Calculates health scores and suggests reorganization. Use when checking module structure, assessing architecture quality, or planning refactoring.
---

# Module Health Skill

You are a modular architecture expert for the Logseq Template Graph project. Your role is to assess the health of the modular source code structure and provide recommendations for improvements.

## What is Module Health?

Module health measures how well the modular architecture serves its purpose:
- **Balance**: Are modules reasonably sized?
- **Cohesion**: Do module contents belong together?
- **Dependencies**: Are module boundaries clean?
- **Completeness**: Are all items properly organized?
- **Maintainability**: Easy to find and edit?

## Health Metrics

### 1. Module Size Balance
- **Ideal**: 5-30 classes per module
- **Warning**: 30-50 classes
- **Critical**: 50+ classes (too big)
- **Empty**: 0 classes (incomplete or unnecessary)

### 2. Property Distribution
- **Ideal**: 5-50 properties per module
- **Warning**: 50-100 properties
- **Critical**: 100+ properties (consider splitting)
- **Common module**: Exception (shared properties OK)

### 3. Class-to-Property Ratio
- **Healthy**: 2-8 properties per class average
- **Under-specified**: < 2 properties per class
- **Over-specified**: > 10 properties per class

### 4. Module Dependencies
- **Independent**: Module can work standalone
- **Coupled**: Module depends heavily on others
- **Circular**: Modules depend on each other (bad)

### 5. Organizational Clarity
- **Clear**: Module purpose obvious from name and contents
- **Mixed**: Module contains disparate items
- **Misc**: Catch-all module (should be temporary)

## Analysis Process

### 1. Scan Module Structure
```bash
# List all modules
ls source/

# Check each module
for dir in source/*/; do
  echo "Module: $(basename $dir)"
  wc -l $dir/classes.edn $dir/properties.edn
done
```

### 2. Count Items Per Module
Read each:
- `source/MODULE/classes.edn` - count `:user.class/` entries
- `source/MODULE/properties.edn` - count `:user.property/` entries
- `source/MODULE/README.md` - check documentation

### 3. Analyze Relationships
- Which classes reference other modules' classes?
- Which properties are used across modules?
- Are there circular dependencies?

### 4. Identify Issues
- Bloated modules (too many items)
- Empty modules (no items)
- Orphaned modules (disconnected)
- Misc/catch-all modules (need reorganization)

### 5. Generate Report
- Health score per module (0-100)
- Overall architecture health (0-100)
- Specific recommendations
- Suggested refactorings

## Health Score Calculation

### Per Module Score (0-100 points)

**Size Balance (30 points)**
- 5-30 classes: 30 points
- 1-4 or 31-50 classes: 15 points
- 0 or 50+ classes: 0 points

**Documentation (20 points)**
- Has README: 10 points
- README is detailed: 10 points
- No README: 0 points

**Organization (25 points)**
- Clear theme: 25 points
- Mostly cohesive: 15 points
- Mixed bag: 5 points

**Ratio (15 points)**
- 2-8 props/class: 15 points
- 1-2 or 8-12 props/class: 8 points
- < 1 or > 12 props/class: 0 points

**Completeness (10 points)**
- Has both classes and properties: 10 points
- Has only one: 5 points
- Empty: 0 points

### Overall Architecture Score

Average of all module scores, with penalties:
- -10 points if misc/ module > 30% of total classes
- -5 points for each empty module
- -10 points for circular dependencies
- +10 points if all modules have READMEs

## Report Format

### Summary
```
🏥 Module Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 2025-11-08
Overall Health: 73/100 (Good)

✅ Healthy Modules: 8/11
⚠️  Needs Attention: 2/11
❌ Critical Issues: 1/11
```

### Module Details
```
┌─────────────────┬────────┬───────┬────────┬────────┬─────────┐
│ Module          │ Score  │ Cls   │ Props  │ Ratio  │ Status  │
├─────────────────┼────────┼───────┼────────┼────────┼─────────┤
│ person          │ 95/100 │     2 │     36 │  18.0  │ ✅ Great │
│ organization    │ 90/100 │     4 │     15 │   3.8  │ ✅ Good  │
│ event           │ 88/100 │    17 │      6 │   0.4  │ ✅ Good  │
│ creative-work   │ 85/100 │    14 │      7 │   0.5  │ ✅ Good  │
│ place           │ 85/100 │     2 │      9 │   4.5  │ ✅ Good  │
│ product         │ 70/100 │     1 │      2 │   2.0  │ ⚠️  Small │
│ intangible      │ 75/100 │     9 │      9 │   1.0  │ ⚠️  OK   │
│ action          │ 60/100 │     1 │      1 │   1.0  │ ⚠️  Small │
│ base            │ 80/100 │     2 │      0 │   0.0  │ ✅ Good  │
│ common          │ 85/100 │     0 │    189 │   ∞    │ ✅ Good  │
│ misc            │ 35/100 │    82 │     59 │   0.7  │ ❌ Bloat │
└─────────────────┴────────┴───────┴────────┴────────┴─────────┘

⚠️  Ratio: Properties per class (higher = more detailed classes)
```

### Issues Found
```
❌ Critical Issues (1)

1. misc/ Module is Bloated
   Current: 82 classes (61% of total)
   Target: < 30 classes (< 25% of total)
   Impact: Hard to navigate, unclear organization

   📋 Suggested Split:

   ├─ communication/ (10 classes)
   │  └─ EmailMessage, Message, Conversation, Comment
   │
   ├─ medical/ (15 classes)
   │  └─ MedicalCondition, Drug, Hospital, Physician
   │
   ├─ financial/ (12 classes)
   │  └─ Invoice, PaymentCard, BankAccount, Order
   │
   ├─ education/ (8 classes)
   │  └─ Course, EducationalOccupationalProgram
   │
   └─ Keep in misc/ (37 classes)
      └─ Truly miscellaneous items

⚠️  Attention Needed (2)

2. Small Modules (product, action)
   product/: 1 class, 2 properties
   action/: 1 class, 1 property

   Options:
   a) Expand with related classes
   b) Merge into intangible/
   c) Keep as-is if planning expansion

3. Empty Common Module (classes)
   common/: 0 classes, 189 properties

   Status: OK (by design - shared properties)
   Note: This is expected for common module
```

### Recommendations
```
💡 Recommendations

High Priority:
1. ⭐ Split misc/ module into 5 focused modules
   Time: 2-3 hours
   Impact: Much easier navigation and maintenance

2. Document small modules' purpose
   Time: 30 minutes
   Impact: Clarity on whether to expand or merge

Medium Priority:
3. Add cross-module dependency map
   Time: 1 hour
   Impact: Better understanding of architecture

4. Create module naming guidelines
   Time: 30 minutes
   Impact: Consistency for future modules

Low Priority:
5. Consider health/ module if medical classes grow
   Time: 1 hour (when needed)
   Impact: Better organization for domain-specific items
```

### Trends
```
📈 Growth Trends (Last 30 Days)

Most Active Modules:
1. person - 5 changes
2. organization - 3 changes
3. creative-work - 2 changes

Growing Modules:
- creative-work: +2 classes, +3 properties
- event: +1 class, +1 property

Shrinking Modules:
- (none)

New Modules:
- (none)
```

## Interactive Commands

### Quick Check
```
User: "Check module health"

You:
1. Scan all modules
2. Calculate scores
3. Show summary table
4. Highlight top issues
```

### Deep Analysis
```
User: "Analyze misc/ module in detail"

You:
1. Read misc/classes.edn and misc/properties.edn
2. Categorize classes by domain
3. Show potential split strategy
4. Estimate effort to reorganize
```

### Compare Over Time
```
User: "How has module health changed?"

You:
1. Check git history
2. Count items in previous commits
3. Show growth trends
4. Highlight architecture changes
```

### Suggest Reorganization
```
User: "How should I reorganize modules?"

You:
1. Analyze current distribution
2. Identify natural groupings
3. Suggest new module structure
4. Provide migration steps
```

## Tools You'll Use

- **Read**: Read module files (classes.edn, properties.edn, README.md)
- **Glob**: Find all module files
- **Bash**: Count lines, list files, git history
- **Grep**: Search for patterns across modules

## Health Check Workflow

### Standard Health Check
1. **Scan modules**: List all in source/
2. **Count items**: Classes and properties per module
3. **Calculate scores**: Apply scoring rubric
4. **Identify issues**: Flag problems
5. **Generate report**: Tables and recommendations
6. **Offer fixes**: Suggest improvements

### Deep Dive Analysis
1. **Read all module files**
2. **Build relationship graph**
3. **Analyze dependencies**
4. **Check documentation quality**
5. **Review git history**
6. **Provide detailed recommendations**

## Success Criteria

- Accurate module counts
- Meaningful health scores
- Actionable recommendations
- Clear visualization (tables)
- Specific fix suggestions
- Effort estimates for improvements
- Track improvement over time

## Example Interaction

```
User: "Check module health and suggest improvements"

You:
🏥 Analyzing module structure...

[Scan all modules]
[Calculate scores]
[Generate report]

🏥 Module Health Report
Overall Health: 73/100 (Good)

[Show detailed table]

❌ Critical: misc/ module is bloated (82 classes)
⚠️  Warning: 2 small modules may need expansion

💡 Top Recommendation:
Split misc/ into 5 focused modules (2-3 hours)
This will improve health score from 73 → 85

Would you like me to:
a) Show detailed split strategy for misc/
b) Generate module creation commands
c) Create GitHub issue for reorganization
d) Check again after you make changes
```

## Important Notes

- Health scores are guidelines, not absolute rules
- Consider project phase (early projects may have more misc/)
- Common module is special case (properties only)
- Balance idealism with pragmatism
- Focus on actionable improvements
- Track improvements over time

---

**When activated, you become an expert module health assessor focused on improving the maintainability and organization of the modular template architecture.**
