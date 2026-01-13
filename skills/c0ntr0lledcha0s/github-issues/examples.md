# GitHub Issues Management - Examples

Real-world examples of issue validation, triage, and management workflows.

## Example 1: Bug Report - Already Fixed

**Issue #42: "Recipe class is missing from template"**

### Validation Process

```bash
# Step 1: Search codebase
grep -r "Recipe" source/
# Result: Found in source/creative-work/classes.edn

# Step 2: Check when it was added
git log --all --grep="Recipe" --oneline
# Result: a688c4b feat(workflow): add Recipe class

# Step 3: Search for related issues
gh issue list --state all --search "Recipe in:title"
# Result: #35 closed (originally requested Recipe)
```

### Response

```markdown
Thank you for the report! I've investigated this issue.

**Validation Results:**
✅ Already implemented

**Investigation:**
I checked the codebase and found:
- Recipe class exists in `source/creative-work/classes.edn` (line 145)
- Added in commit a688c4b on 2025-11-08
- Includes properties: recipeIngredient, cookTime, prepTime, recipeInstructions, recipeYield
- Parent class: CreativeWork

**Current Status:**
✅ Available in v0.5.0 and later

**Recommendation:**
Please update to the latest version (v0.5.0) which includes the Recipe class. Import the template and you should see Recipe available as a class option.

**Usage:**
1. Import template v0.5.0+
2. Create a new page
3. Add class property: Recipe
4. You'll have access to all cooking-related properties

**Related:**
- Originally implemented in: #35
- Commit: a688c4b
- Documentation: docs/user-guide/classes.md#recipe

Closing as already implemented. If you're using v0.5.0+ and still don't see Recipe, please reopen with your Logseq version and template version!
```

**Actions:**
```bash
gh issue edit 42 --add-label "duplicate"
gh issue close 42 --comment "[response above]"
```

---

## Example 2: Feature Request - Duplicate

**Issue #78: "Add Person class with email and phone properties"**

### Validation Process

```bash
# Step 1: Search for Person class
grep -r "Person" source/
# Result: Exists in source/person/classes.edn

# Step 2: Check properties
grep -A 50 ":user.class/Person" source/person/classes.edn
# Result: Person has email, telephone, and 28 other properties

# Step 3: Search for duplicate requests
gh issue list --state all --search "Person in:title"
# Result: #12 (original Person class request - closed)
```

### Response

```markdown
Thank you for the suggestion!

**Validation:**
✅ This feature already exists!

**Current Implementation:**
- Class: Person in `source/person/classes.edn`
- Properties include:
  - email (:default, :one)
  - telephone (:default, :one)
  - jobTitle, birthDate, spouse, worksFor, colleague, and 28 more

- Added in: v0.1.0 (initial release)

**Usage:**
The Person class is available in all template versions:
1. Import the template
2. Create a new page
3. Add property: `class:: [[Person]]`
4. Access all Person properties (email, telephone, etc.)

**Documentation:**
- Person class guide: docs/user-guide/classes.md#person
- Property reference: docs/reference/properties.md
- Examples: docs/examples/person-examples.md

**Related:**
- Originally implemented in: #12
- See also: PersonalRelationship class (for relationships between people)

Closing as already implemented. If you need additional properties for the Person class that aren't currently available, please open a new issue specifying which Schema.org properties are missing!
```

**Actions:**
```bash
gh issue edit 78 --add-label "duplicate"
gh issue close 78 --comment "[response above]"
```

---

## Example 3: Bug Report - Valid and Confirmed

**Issue #91: "spouse property has wrong cardinality - should be :many"**

### Validation Process

```bash
# Step 1: Check current implementation
grep -A 5 "spouse" source/person/properties.edn
# Result: {:db/cardinality :db.cardinality/one ...}

# Step 2: Check Schema.org
# WebFetch: https://schema.org/spouse
# Result: Schema.org allows multiple spouses

# Step 3: Search for duplicates
gh issue list --state all --search "spouse cardinality"
# Result: No duplicates

# Step 4: Test in Logseq
# - Import template
# - Create Person page
# - Try to add multiple spouses
# Result: Only allows one spouse (bug confirmed!)
```

### Response

```markdown
Thank you for reporting this issue!

**Validation:**
✅ Confirmed - This is a bug

**Investigation:**
I checked the codebase and confirmed:
- spouse property currently has `:db.cardinality/one`
- Location: `source/person/properties.edn:145`
- Schema.org spec allows multiple spouses
- Use cases: historical records, polyamorous relationships, remarriage tracking

**Root Cause:**
The spouse property was incorrectly implemented with single cardinality. This should be `:many` to support:
- Multiple marriages over time
- Polyamorous relationships
- Historical genealogy records

**Related Issues:**
None - this is a unique bug

**Fix Plan:**
I'll create a fix for this. Expected completion: Today

**Implementation:**
1. Change cardinality from `:one` to `:many`
2. Test in Logseq to verify multiple spouses can be added
3. Update documentation examples
4. Include in next patch release

**Labels:** `bug`, `priority:medium`, `scope:properties`

Creating fix now...
```

**Actions:**
```bash
# Label the issue
gh issue edit 91 --add-label "bug,priority:medium,scope:properties,status:in-progress"

# Create branch and fix
git checkout -b fix/spouse-cardinality
# ... make changes ...
git commit -m "fix(properties): correct spouse property cardinality to :many"
git push -u origin fix/spouse-cardinality

# Create PR
gh pr create --title "Fix #91: correct spouse property cardinality" --body "Fixes #91

Changed spouse property from :db.cardinality/one to :many to support:
- Multiple marriages over time
- Polyamorous relationships
- Historical genealogy records

Aligns with Schema.org specification."

# Update issue
gh issue comment 91 --body "✅ Fix created in #92

PR is ready for review. Will be included in next patch release (v0.5.1)."
```

---

## Example 4: Feature Request - Has Dependencies

**Issue #105: "Add MedicalCondition class"**

### Validation Process

```bash
# Step 1: Check if exists
grep -r "MedicalCondition" source/
# Result: Not found

# Step 2: Research Schema.org hierarchy
# MedicalCondition → MedicalEntity → Thing
# MedicalEntity doesn't exist yet!

# Step 3: Check for related issues
gh issue list --state all --search "medical"
# Result: #89 "Add medical module" (open, blocked)

# Step 4: Check module structure
ls source/
# Result: No medical/ module exists
```

### Response

```markdown
Thank you for the feature request!

**Validation:**
✅ New feature - not currently in template
🔍 No duplicates found

**Analysis:**
- Feature: MedicalCondition class
- Use Case: Health tracking, medical research notes
- Complexity: Medium
- Schema.org Alignment: Yes

**Related Issues:**
- **Blocked by #89** (Add medical module)
- **Depends on:** MedicalEntity class (parent class, not yet in template)

**Schema.org Research:**
```
Hierarchy: Thing → MedicalEntity → MedicalCondition

MedicalEntity (parent - not in template):
- code, guideline, legalStatus, medicineSystem, recognizingAuthority

MedicalCondition (14 direct properties):
- associatedAnatomy, cause, differentialDiagnosis, drug
- epidemiology, expectedPrognosis, pathophysiology
- possibleComplication, possibleTreatment, riskFactor
- signOrSymptom, stage, status, typicalTest
```

**Dependencies:**
This feature requires a larger medical module implementation:

**Dependency Chain:**
1. First: Create medical/ module structure (#89)
2. Second: Add MedicalEntity base class (parent)
3. Third: Add MedicalCondition (this issue)
4. Optional: Add related classes (Drug, MedicalTest, etc.)

**Recommended Approach:**
Rather than implement MedicalCondition alone, I recommend implementing the full medical module:

### Comprehensive Medical Module Plan

**Phase 1: Foundation** (Issue #89)
- [ ] Create `source/medical/` module
- [ ] Add MedicalEntity base class
- [ ] Add core medical properties

**Phase 2: Core Classes** (This issue + new issues)
- [ ] Add MedicalCondition (#105 - this issue)
- [ ] Add Drug
- [ ] Add MedicalProcedure
- [ ] Add MedicalTest

**Phase 3: Extended Classes**
- [ ] Add Physician
- [ ] Add Hospital
- [ ] Move medical classes from misc/

**Affected Files:**
- `source/medical/classes.edn` (new)
- `source/medical/properties.edn` (new)
- `source/medical/README.md` (new)
- `scripts/build.clj` (add medical module)

**Estimated Effort:**
- Issue #89 (foundation): 2 hours
- This issue (MedicalCondition): 1 hour
- Full module (Phases 1-3): 6-8 hours

**Labels:** `feature`, `priority:medium`, `scope:classes`, `status:blocked`

**Next Steps:**
I recommend:
1. ⭐ **First complete #89** (medical module foundation)
2. Then implement MedicalEntity (parent class)
3. Then implement MedicalCondition (this issue)
4. Consider implementing full medical module together

Would you like me to:
- [ ] Wait for #89 to complete, then implement this
- [ ] Implement entire medical module as one PR
- [ ] Create separate issues for each medical class

Let me know your preference!
```

**Actions:**
```bash
# Label with dependencies
gh issue edit 105 --add-label "feature,priority:medium,scope:classes,status:blocked"

# Link to blocking issue
gh issue comment 105 --body "🔗 **Dependencies:**
- Blocked by #89 (Add medical module)

Once #89 is complete, I can implement this feature."

# Update blocking issue with reference
gh issue comment 89 --body "🔗 **Blocks:**
- #105 (Add MedicalCondition class)

This foundation is needed before medical classes can be added."
```

---

## Example 5: Feature Request - Related to Multiple Issues

**Issue #120: "Add Event properties for meetings"**

### Validation Process

```bash
# Step 1: Check if Event exists
grep -r "Event" source/
# Result: Event class exists in source/event/classes.edn

# Step 2: Check current Event properties
grep -A 30 ":user.class/Event" source/event/classes.edn
# Result: Has startDate, endDate, location, organizer

# Step 3: What properties are requested?
gh issue view 120
# Request: attendee, eventStatus, duration properties

# Step 4: Check if properties exist
grep "attendee\|eventStatus\|duration" source/event/properties.edn
# Result: Not found

# Step 5: Search for related requests
gh issue list --state all --search "event properties"
# Result: #95 "Add event recurrence" (different but related)
#         #108 "Add virtual meeting support" (related!)
```

### Response

```markdown
Thank you for the feature request!

**Validation:**
✅ Event class exists
❌ Requested properties don't exist yet
🔍 Found related feature requests

**Current Event Implementation:**
- Class: Event in `source/event/classes.edn`
- Current properties (6):
  - startDate, endDate, location, organizer
  - name, description (inherited from Thing)

**Requested Properties (Missing):**
1. attendee - List of participants
2. eventStatus - Status (scheduled, cancelled, postponed)
3. duration - Event duration

**Related Issues:**
- Related to #108 ("Add virtual meeting support")
  - Both requests enhance Event for meetings
  - Could implement together
- Related to #95 ("Add event recurrence")
  - Different focus but same class

**Recommendation:**
I suggest combining #108 and this issue into a comprehensive "Meeting Support" enhancement:

### Combined Implementation Plan

**Properties to Add:**
```
From #120 (this issue):
- attendee (Person, :many) - Meeting participants
- eventStatus (Text, :one) - scheduled/confirmed/cancelled/postponed
- duration (Text, :one) - Duration (e.g., "PT1H30M")

From #108:
- eventAttendanceMode (Text, :one) - online/offline/mixed
- location (virtual) - Already have location, extend for virtual

Bonus (Schema.org standard):
- agenda (Text, :one) - Meeting agenda
- recordedIn (URL, :many) - Recording links
```

**Implementation:**
- [ ] Add 6 meeting-related properties to `source/event/properties.edn`
- [ ] Update Event class to include new properties
- [ ] Add examples for meeting use cases
- [ ] Document virtual vs in-person meetings

**Affected Files:**
- `source/event/properties.edn`
- `source/event/classes.edn`
- `source/event/README.md`
- `docs/examples/event-examples.md`

**Estimated Effort:** 1-2 hours

**Labels:** `feature`, `priority:medium`, `scope:properties`

**Next Steps:**
Would you like me to:
- [ ] Implement just the 3 properties from this issue
- [ ] ⭐ Implement combined meeting support (this + #108)
- [ ] Wait for your feedback on the scope

I recommend the combined approach for complete meeting support!
```

**Actions:**
```bash
# Label this issue
gh issue edit 120 --add-label "feature,priority:medium,scope:properties"

# Link to related issue
gh issue comment 120 --body "🔗 **Related Issues:**
- #108 (Add virtual meeting support)

These could be implemented together for comprehensive meeting support."

# Link from the other issue
gh issue comment 108 --body "🔗 **Related Issues:**
- #120 (Add Event properties for meetings)

Combining these would provide complete meeting functionality."
```

---

## Example 6: Question - Already Documented

**Issue #133: "How do I use the Person class for contact management?"**

### Validation Process

```bash
# Step 1: Check if this is in docs
grep -r "contact management" docs/
# Result: Found in docs/examples/crm-examples.md

grep -r "Person class" docs/user-guide/
# Result: Found in docs/user-guide/classes.md

# Step 2: Check for similar questions
gh issue list --state all --search "Person class usage"
# Result: #45 (similar question, answered and closed)
```

### Response

```markdown
Great question!

**Documentation:**
This is covered in our documentation! The Person class is perfect for contact management.

**Quick Answer:**
1. Import the CRM template preset (optimized for contacts)
2. Create a page for each contact
3. Add the Person class: `class:: [[Person]]`
4. Fill in properties:
   - email, telephone, jobTitle
   - worksFor (link to Organization pages)
   - address, birthDate, etc.

**Relevant Documentation:**
- [Person Class Guide](docs/user-guide/classes.md#person) - Complete property reference
- [CRM Examples](docs/examples/crm-examples.md) - Contact management workflows
- [Getting Started](QUICK_START.md#for-users-import-templates) - Template import

**Example Contact Page:**
```markdown
class:: [[Person]]
email:: john@example.com
telephone:: +1-555-0123
jobTitle:: Software Engineer
worksFor:: [[Acme Corp]]
address:: [[123 Main St]]
birthDate:: [[1990-05-15]]
```

**CRM Template:**
For contact management specifically, use the CRM preset:
```bash
# Import build/logseq_db_Templates_crm.edn
```

This includes Person, Organization, and contact-focused properties.

**See Also:**
- #45 (Similar question with more examples)
- PersonalRelationship class (for personal contacts)
- Organization class (for companies)

**Labels:** `question`, `scope:person`

Does this answer your question? Feel free to ask for clarification or open a new issue if you need specific features not covered in the CRM preset!
```

**Actions:**
```bash
# Label as question
gh issue edit 133 --add-label "question,scope:person"

# Close with answer
gh issue close 133 --comment "[response above]"
```

---

## Common Validation Patterns

### Pattern 1: Check if Feature Exists

```bash
# Search codebase
grep -r "[FeatureName]" source/

# If found - respond "already exists"
# If not found - proceed with feature request workflow
```

### Pattern 2: Find Duplicates

```bash
# Search all issues
gh issue list --state all --search "[keywords] in:title"
gh issue list --state all --search "[keywords] in:body"

# If exact duplicate - close this, link to original
# If similar but different - link both, keep open
# If unique - proceed with implementation
```

### Pattern 3: Check Git History

```bash
# Search commits
git log --all --grep="[feature]" --oneline

# If found - respond "already implemented in [commit]"
# If not found - proceed with feature request
```

### Pattern 4: Map Dependencies

```bash
# List open issues in scope
gh issue list --label "scope:[module]"

# Identify dependencies
# - What must be implemented first?
# - What does this block?
# - What could be implemented together?

# Document all relationships in response
```

---

## Validation Decision Tree

```
Issue Received
    ↓
Does feature/fix exist in codebase?
    ├─ YES → Close with "already implemented"
    └─ NO → Continue
           ↓
Is it a duplicate of existing issue?
    ├─ YES → Close with link to original
    └─ NO → Continue
           ↓
Was it fixed in recent commits?
    ├─ YES → Close with commit reference
    └─ NO → Continue
           ↓
For bugs: Can you reproduce?
    ├─ NO → Request more info or close as invalid
    └─ YES → Continue
           ↓
Are there related/blocking issues?
    ├─ YES → Document relationships, may block this
    └─ NO → Continue
           ↓
Is it valid and feasible?
    ├─ YES → Plan implementation
    └─ NO → Close with explanation
```

---

## Response Templates Summary

| Situation | Template | Action |
|-----------|----------|--------|
| Already implemented | "Feature Already Exists" | Close, link to code |
| Exact duplicate | "Duplicate" | Close, link to original |
| Already fixed | "Invalid/Already Fixed" | Close, link to commit |
| Valid bug | "Bug is Valid" | Label, plan fix |
| Valid feature | "Feature is New and Valid" | Label, plan implementation |
| Has dependencies | Include "Dependencies" section | Document blockers |
| Related issues | Include "Related Issues" section | Link all related |
| Needs info | "Needs Information" | Request clarification |

---

## Success Metrics

- **Response includes validation** ✅
- **Evidence cited** (commits, code, issues) ✅
- **Relationships documented** ✅
- **Appropriate labels applied** ✅
- **User thanked** ✅
- **Clear next steps** ✅
