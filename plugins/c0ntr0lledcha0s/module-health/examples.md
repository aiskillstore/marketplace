# Module Health - Examples

This file contains example health checks and reorganization strategies for the modular template architecture.

## Example 1: Quick Health Check

**User Request:**
> "Check module health"

**Output:**
```
🏥 Module Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 2025-11-08
Overall Health: 73/100 (Good)

✅ Healthy Modules: 8/11
⚠️  Needs Attention: 2/11
❌ Critical Issues: 1/11

Module Summary:
┌─────────────────┬────────┬───────┬────────┬────────┬─────────┐
│ Module          │ Score  │ Cls   │ Props  │ Ratio  │ Status  │
├─────────────────┼────────┼───────┼────────┼────────┼─────────┤
│ person          │ 95/100 │     2 │     36 │  18.0  │ ✅ Great │
│ organization    │ 90/100 │     4 │     15 │   3.8  │ ✅ Good  │
│ event           │ 88/100 │    17 │      6 │   0.4  │ ✅ Good  │
│ creative-work   │ 85/100 │    14 │      7 │   0.5  │ ✅ Good  │
│ place           │ 85/100 │     2 │      9 │   4.5  │ ✅ Good  │
│ base            │ 80/100 │     2 │      0 │   0.0  │ ✅ Good  │
│ common          │ 85/100 │     0 │    189 │   ∞    │ ✅ Good  │
│ intangible      │ 75/100 │     9 │      9 │   1.0  │ ⚠️  OK   │
│ product         │ 70/100 │     1 │      2 │   2.0  │ ⚠️  Small│
│ action          │ 60/100 │     1 │      1 │   1.0  │ ⚠️  Small│
│ misc            │ 35/100 │    82 │     59 │   0.7  │ ❌ Bloat │
└─────────────────┴────────┴───────┴────────┴────────┴─────────┘

Top Priority Issues:
1. ❌ misc/ module is bloated (82 classes = 61% of total)
2. ⚠️  product/ and action/ are very small (1 class each)

Recommendation: Split misc/ module → Expected improvement: 73 → 85
```

---

## Example 2: Detailed misc/ Analysis

**User Request:**
> "Analyze misc/ module in detail"

**Output:**
```
🔍 Detailed Analysis: misc/ Module
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current Status: ❌ Critical (35/100)
- Classes: 82 (61% of total)
- Properties: 59
- Average properties per class: 0.7
- Issue: Too many disparate items

Classes by Domain:
┌──────────────────┬───────┬────────────────────────────┐
│ Domain           │ Count │ Examples                   │
├──────────────────┼───────┼────────────────────────────┤
│ Communication    │    10 │ EmailMessage, Comment      │
│ Medical          │    15 │ MedicalCondition, Drug     │
│ Financial        │    12 │ Invoice, PaymentCard       │
│ Education        │     8 │ Course, EducationalProgram │
│ Transportation   │     6 │ Vehicle, Flight            │
│ Food             │     7 │ Recipe, Restaurant         │
│ Legal            │     5 │ LegalDocument, Legislation │
│ Government       │     4 │ GovernmentOrganization     │
│ Sports           │     3 │ SportsTeam, SportsEvent    │
│ Truly Misc       │    12 │ Various unrelated items    │
└──────────────────┴───────┴────────────────────────────┘

Recommended Split Strategy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Create communication/ module (10 classes)
   Classes: EmailMessage, Message, Conversation, Comment,
            Question, Answer, Review, Rating, Quotation, Thread
   Properties: messageText, dateReceived, sender, recipient, etc.
   Effort: 1 hour

2. Create medical/ module (15 classes)
   Classes: MedicalCondition, Drug, Hospital, Physician,
            MedicalProcedure, Symptom, Therapy, Diagnosis, etc.
   Properties: medicalCode, medicine, adverseReaction, etc.
   Effort: 1.5 hours

3. Create financial/ module (12 classes)
   Classes: Invoice, PaymentCard, BankAccount, Order,
            Transaction, Quote, Receipt, etc.
   Properties: paymentMethod, totalAmount, currency, etc.
   Effort: 1 hour

4. Create education/ module (8 classes)
   Classes: Course, EducationalProgram, Quiz, Assignment,
            Syllabus, Lecture, etc.
   Properties: courseCode, instructor, credits, etc.
   Effort: 45 minutes

5. Keep in misc/ (37 classes)
   Everything else that doesn't form a coherent domain
   Estimated misc/ health after split: 75/100

Total Effort: ~4.5 hours
Expected Overall Health: 73 → 85 (+12 points)
```

---

## Example 3: Module Reorganization Plan

**User Request:**
> "How should I reorganize modules?"

**Output:**
```
📋 Module Reorganization Plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current State: 11 modules, 73/100 health
Target State: 15 modules, 85/100 health

Step 1: Create New Modules
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commands:
```bash
mkdir -p source/communication/{classes,properties}
mkdir -p source/medical/{classes,properties}
mkdir -p source/financial/{classes,properties}
mkdir -p source/education/{classes,properties}
```

Step 2: Move Classes from misc/
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Communication (10 classes):
- Move EmailMessage, Message, Conversation → communication/classes.edn
- Move related properties → communication/properties.edn

Medical (15 classes):
- Move MedicalCondition, Drug, Hospital → medical/classes.edn
- Move related properties → medical/properties.edn

Financial (12 classes):
- Move Invoice, PaymentCard, BankAccount → financial/classes.edn
- Move related properties → financial/properties.edn

Education (8 classes):
- Move Course, EducationalProgram, Quiz → education/classes.edn
- Move related properties → education/properties.edn

Step 3: Update Build Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit scripts/build.clj:
```clojure
(def modules
  [:base :common :person :organization :event :creative-work
   :place :product :intangible :action
   :communication :medical :financial :education  ; NEW
   :misc])
```

Step 4: Create Module READMEs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each new module, create README.md with:
- Purpose and scope
- Key classes
- Common use cases
- Examples

Step 5: Test Build
━━━━━━━━━━━━━━━━━

```bash
npm run build:full
# Verify all classes/properties intact
# Check file sizes
# Test import in Logseq
```

Step 6: Validate & Commit
━━━━━━━━━━━━━━━━━━━━━━━

```bash
npm run validate
git add source/
git commit -m "refactor(modular): split misc into focused modules

Reorganized 45 classes from misc/ into four focused modules:
- communication/ - Messaging and communication classes
- medical/ - Health and medical classes
- financial/ - Financial and payment classes
- education/ - Educational and learning classes

This improves overall module health from 73/100 to 85/100."
```

Timeline:
- Step 1-2: 3 hours (moving classes)
- Step 3-4: 1.5 hours (config + docs)
- Step 5-6: 30 minutes (testing + commit)
- Total: ~5 hours

Benefits:
✅ Easier navigation
✅ Better organization
✅ Clearer module purposes
✅ Health score: 73 → 85
```

---

## Example 4: Module Growth Tracking

**User Request:**
> "How have modules changed over time?"

**Output:**
```
📈 Module Growth Trends (Last 90 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Most Active Modules:
┌─────────────────┬─────────┬──────────┬──────────┐
│ Module          │ Changes │ +Classes │ +Props   │
├─────────────────┼─────────┼──────────┼──────────┤
│ person          │       8 │       +1 │       +5 │
│ organization    │       6 │       +2 │       +3 │
│ creative-work   │       5 │       +2 │       +4 │
│ misc            │      12 │      +18 │      +12 │
│ event           │       3 │       +1 │       +1 │
└─────────────────┴─────────┴──────────┴──────────┘

Growth Rate:
- misc/ growing fastest (18 classes in 90 days)
- person/ stable with quality additions
- organization/ expanding steadily

⚠️  Warning: misc/ growth rate is unsustainable
   Recommendation: Implement reorg plan soon

Historical Health Scores:
┌────────────┬─────────┬────────────────────┐
│ Date       │ Score   │ Notes              │
├────────────┼─────────┼────────────────────┤
│ 2024-08-01 │ 82/100  │ Before misc bloat  │
│ 2024-09-01 │ 78/100  │ misc growing       │
│ 2024-10-01 │ 75/100  │ misc at 50 classes │
│ 2024-11-01 │ 73/100  │ misc at 82 classes │
└────────────┴─────────┴────────────────────┘

Trend: Declining health due to misc/ bloat
Action needed: Reorganize to reverse trend
```

---

## Example 5: Small Module Strategy

**User Request:**
> "What should I do with product/ and action/ modules?"

**Output:**
```
🔍 Small Module Analysis: product/ & action/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

product/ Module:
- Classes: 1 (Product)
- Properties: 2 (price, brand)
- Score: 70/100 (⚠️ Small)

action/ Module:
- Classes: 1 (Action)
- Properties: 1 (actionStatus)
- Score: 60/100 (⚠️ Small)

Strategy Options:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1: Expand (Recommended for product/)
✅ Add related classes to product/:
   - Offer (price offers, deals)
   - Brand (brand information)
   - ProductModel (specific models)
   - Review (product reviews)

Effort: 2-3 hours
Outcome: product/ becomes 5+ classes, 70 → 90 score

Option 2: Merge (Recommended for action/)
✅ Merge action/ into intangible/:
   - Action is conceptually intangible
   - Combines well with existing classes
   - Simplifies module structure

Effort: 30 minutes
Outcome: One less module to maintain

Option 3: Keep As-Is
⚠️  Only if planning future expansion
   - Document intent in README
   - Set timeline for expansion
   - Monitor for 3 months

Recommendation:
1. Expand product/ with related e-commerce classes
2. Merge action/ into intangible/
3. Expected health impact: 73 → 76 (+3 points)
```

---

## Example 6: Module Dependency Analysis

**User Request:**
> "Show module dependencies"

**Output:**
```
🔗 Module Dependency Map
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Legend:
→ Uses classes from
⇄ Mutual dependency
* Root module (no dependencies)

Dependency Tree:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

base/* (Thing, Agent)
  ↓
  └─→ All other modules depend on base/

common/* (shared properties)
  ↓
  └─→ Used by all modules with properties

person/
  → base/ (inherits Thing)
  → common/ (uses shared properties)
  ← organization/ (Person references Organization)
  ← event/ (Person as attendee, organizer)

organization/
  → base/ (inherits Thing)
  → common/ (uses shared properties)
  → person/ (employee, member references Person)

event/
  → base/ (inherits Thing)
  → person/ (attendee, organizer)
  → place/ (location)
  → organization/ (organizer)

creative-work/
  → base/ (inherits Thing)
  → person/ (author, creator)
  → organization/ (publisher)

place/
  → base/ (inherits Thing)
  → common/ (uses shared properties)

product/
  → base/ (inherits Thing)
  → organization/ (brand, manufacturer)

intangible/
  → base/ (inherits Thing)

action/
  → base/ (inherits Thing)
  → person/ (agent)

misc/
  → base/ (inherits Thing)
  → person/ (various references)
  → organization/ (various references)
  → place/ (various references)

Complexity Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Independent Modules (can work standalone):
  base/, common/, intangible/

Low Coupling (1-2 dependencies):
  place/, product/, action/

Medium Coupling (3-4 dependencies):
  person/, organization/, creative-work/

High Coupling (5+ dependencies):
  event/, misc/

✅ No circular dependencies detected
⚠️  misc/ has high coupling (refactor will reduce)
```

---

## Example 7: Health Score Breakdown

**User Request:**
> "Explain the health score for person/ module"

**Output:**
```
📊 Health Score Breakdown: person/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Score: 95/100 (✅ Excellent)

Component Scores:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Size Balance (30/30) ✅
   Classes: 2 (Person, PersonalRelationship)
   Target: 5-30 classes
   Status: Within ideal range

2. Documentation (20/20) ✅
   README exists: ✅ Yes
   README quality: ✅ Detailed with examples
   Includes usage guide: ✅ Yes

3. Organization (25/25) ✅
   Theme clarity: ✅ Very clear (people & relationships)
   Cohesion: ✅ All items belong together
   Schema.org alignment: ✅ Perfect match

4. Property Ratio (15/15) ✅
   Properties per class: 18.0 (36 props / 2 classes)
   Target: 2-8 per class
   Note: High ratio indicates rich, detailed classes

5. Completeness (10/10) ✅
   Has classes: ✅ Yes (2)
   Has properties: ✅ Yes (36)
   Properties assigned: ✅ All in use

Bonus Points (+5):
  ✅ Excellent documentation
  ✅ Heavy reuse of common properties
  ✅ Clean inheritance hierarchy

Deductions (-0):
  (none)

Total: 95/100 (Excellent)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strengths:
✅ Well-documented
✅ Clear purpose
✅ Rich property set
✅ Good examples
✅ Schema.org compliant

Areas for Improvement:
(none - this is a model module!)

Recommendation: Use person/ as template for other modules
```

---

## Example 8: Module Creation Checklist

**User Request:**
> "How do I create a new module?"

**Output:**
```
📝 New Module Creation Checklist
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Planning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Define module purpose (clear domain)
☐ Identify 5+ classes that belong together
☐ List required properties
☐ Check Schema.org for standard naming
☐ Verify no overlap with existing modules

Step 2: Create Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ mkdir -p source/MODULE-NAME
☐ Create source/MODULE-NAME/classes.edn
☐ Create source/MODULE-NAME/properties.edn
☐ Create source/MODULE-NAME/README.md

Step 3: Add Classes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Define each class with unique ID
☐ Set parent class (usually Thing)
☐ Add icon emoji
☐ Write clear description
☐ List class properties

Step 4: Add Properties
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Define each property with unique ID
☐ Set cardinality (:one or :many)
☐ Choose property type (:default, :node, :date, etc.)
☐ Add icon emoji
☐ Write clear description
☐ Assign to classes

Step 5: Documentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Write README with:
  ☐ Module purpose
  ☐ List of classes
  ☐ Common use cases
  ☐ Usage examples
  ☐ Schema.org references

Step 6: Build Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Add module to scripts/build.clj
☐ Add to preset configurations (if applicable)
☐ Update .gitignore if needed

Step 7: Testing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Run npm run build:full
☐ Check build/logseq_db_Templates_full.edn
☐ Import into test Logseq graph
☐ Verify classes appear
☐ Test properties work
☐ Check module health score

Step 8: Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Run npm run validate
☐ Check for EDN syntax errors
☐ Verify no duplicate IDs
☐ Confirm all references valid
☐ Run health check

Step 9: Documentation Updates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Update main README.md
☐ Update CLAUDE.md if needed
☐ Add to DOCS_INDEX.md
☐ Create examples in docs/

Step 10: Commit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Stage changes: git add source/MODULE-NAME
☐ Commit with conventional message:
  git commit -m "feat(modular): add MODULE-NAME module"

Quality Checklist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ 5-30 classes (ideal range)
☐ Clear, focused domain
☐ All classes have parents (except Thing/Agent)
☐ All properties assigned to classes
☐ Schema.org compliant naming
☐ Icons for all classes/properties
☐ Descriptions for all items
☐ README with examples
☐ Health score > 80

Estimated Time: 2-4 hours for new module
```

---

## Quick Reference

### Health Score Ranges

| Score | Status | Meaning |
|-------|--------|---------|
| 90-100 | Excellent | Model module, no changes needed |
| 80-89 | Good | Minor improvements possible |
| 70-79 | OK | Some attention needed |
| 60-69 | Fair | Improvements recommended |
| 50-59 | Poor | Significant issues |
| 0-49 | Critical | Immediate action required |

### Module Size Guidelines

| Classes | Status | Action |
|---------|--------|--------|
| 0 | Empty | Delete or add content |
| 1-4 | Small | Expand or merge |
| 5-30 | Ideal | Maintain |
| 31-50 | Large | Consider splitting |
| 50+ | Bloated | Split immediately |

### Common Commands

```bash
# Check health
"Check module health"

# Analyze specific module
"Analyze misc/ module in detail"

# Get reorganization plan
"How should I reorganize modules?"

# Track changes
"How have modules changed over time?"

# Module strategy
"What should I do with small modules?"

# Dependencies
"Show module dependencies"

# Create new module
"How do I create a new module?"
```
