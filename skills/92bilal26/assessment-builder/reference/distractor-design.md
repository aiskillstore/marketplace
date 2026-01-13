# Distractor Design for Multiple-Choice Questions

## Overview

Effective distractors (incorrect answer options) are based on common misconceptions and errors, making them plausible to students who don't fully understand the concept.

## What Makes a Good Distractor

### Characteristics

1. **Plausible**: Seems correct if you have a specific misunderstanding
2. **Diagnostic**: Reveals specific gaps in understanding
3. **Based on Research**: Derived from actual student errors
4. **Not Trick**: Tests concept, not reading comprehension
5. **One Clearly Correct**: No ambiguity about right answer

## Common Misconception Categories

### Type 1: Conceptual Misunderstanding

**Example: Mutability**
```
Question: After this code, what does y contain?
x = [1, 2, 3]
y = x
x.append(4)

A) [1, 2, 3, 4]  ← Correct (understands references)
B) [1, 2, 3]     ← Thinks y is independent copy
C) [4]           ← Thinks append replaces, not adds
D) Error         ← Thinks you can't modify through different name
```

**Distractor B** tests: Understanding of assignment vs. copying
**Distractor C** tests: Understanding of append operation
**Distractor D** tests: Understanding of reference semantics

---

### Type 2: Off-by-One Errors

**Example: Range Function**
```
Question: How many times does this loop execute?
for i in range(5):
    print(i)

A) 5    ← Correct
B) 6    ← Thinks range(5) includes 5
C) 4    ← Thinks range starts at 1
D) 0    ← Doesn't understand loops
```

---

### Type 3: Type Confusion

**Example: String vs Integer**
```
Question: What does this print?
x = "10"
y = "20"
print(x + y)

A) "1020"   ← Correct (string concatenation)
B) 30       ← Thinks strings auto-convert to numbers
C) "30"     ← Thinks + adds numerically but returns string
D) Error    ← Thinks you can't add strings
```

---

### Type 4: Operator Precedence

**Example: Boolean Logic**
```
Question: What does this evaluate to?
x = 5
result = x > 3 and x < 10

A) True     ← Correct
B) False    ← Confuses and/or logic
C) 5        ← Thinks and returns a value
D) "True"   ← Type confusion
```

---

### Type 5: Scope Misunderstanding

**Example: Variable Scope**
```
Question: What does this print?
x = 10

def foo():
    x = 5

foo()
print(x)

A) 10       ← Correct (understands local scope)
B) 5        ← Thinks function modifies global
C) Error    ← Thinks x is undefined
D) None     ← Confuses return value with variable
```

---

## Distractor Design Process

### Step 1: Identify the Concept

What specific understanding are you testing?
- Example: "Understanding that lists are mutable and assigned by reference"

### Step 2: List Common Errors

What mistakes do students actually make?
- Think lists are copied on assignment
- Confuse list methods (append vs extend)
- Think modifying one reference doesn't affect others

### Step 3: Create Distractor for Each Error

Each distractor represents one specific misconception:

```
Correct answer: Tests full understanding
Distractor A: Thinks X (specific error)
Distractor B: Thinks Y (different error)
Distractor C: Thinks Z (third error)
```

### Step 4: Validate Plausibility

- Would a student with partial understanding choose this?
- Is it based on a real misconception (not random)?
- Does it help diagnose specific knowledge gaps?

## Distractor Anti-Patterns

### Bad: "All of the above"

Makes guessing easier, doesn't test understanding.

### Bad: Obviously Wrong Options

```
Question: What does list.append() do?
A) Adds item to end of list  ← Correct
B) Deletes all items         ← Too obviously wrong
C) Converts list to string   ← No one would think this
D) Crashes the program       ← Silly distractor
```

Better distractors based on real confusion:
```
A) Adds item to end of list          ← Correct
B) Adds item to beginning of list    ← Confuses append/prepend
C) Adds all elements from iterable   ← Confuses append/extend
D) Returns new list with item added  ← Thinks append returns new list
```

### Bad: Trick Wording

Distractors shouldn't rely on misreading the question.

### Bad: Multiple Correct Answers

Ambiguity frustrates learners and doesn't assess fairly.

## Distractor Quality Checklist

For each distractor, ask:
- [ ] Is it plausible to someone with partial understanding?
- [ ] Does it represent a common misconception?
- [ ] Would choosing it reveal a specific knowledge gap?
- [ ] Is it clearly wrong to someone with full understanding?
- [ ] Is it not a trick or wordplay trap?

## Cognitive Level and Distractors

### Lower-Level Questions (Remember/Understand)

Distractors test basic concept confusion:
```
What is a variable?
A) A name that refers to a value       ← Correct
B) A permanent storage location        ← Confusion about mutability
C) A type of function                  ← Category confusion
D) A Python keyword                    ← Confusion about terminology
```

### Higher-Level Questions (Analyze/Evaluate)

Distractors test subtle understanding:
```
Which is most Pythonic?
A) [x for x in items if x > 0]              ← Correct
B) filter(lambda x: x > 0, items)           ← Valid but less Pythonic
C) [x for x in items where x > 0]           ← Syntax error (shows lack of practice)
D) list(filter(lambda x: x > 0, items))     ← Verbose (shows coming from another language)
```

## Validating Distractors with Data

If possible, field-test questions:
- Each distractor should be chosen by 10-30% of students
- If distractor chosen by <5%, it's too obviously wrong
- If distractor chosen by >40%, question may be ambiguous or too hard

## Example: Complete Distractor Analysis

```python
Question: What will this code print?

def modify(lst):
    lst.append(4)
    return lst

x = [1, 2, 3]
y = modify(x)
print(len(x))

A) 4        ← CORRECT (understands mutation and references)
B) 3        ← Thinks lst is local copy, x unchanged
C) 5        ← Misunderstands how append works
D) Error    ← Thinks you can't modify parameter

Analysis:
- Distractor B: Most common (30%+ choose) - tests core reference concept
- Distractor C: Less common (~10%) - basic append confusion
- Distractor D: Rare (~5%) - misunderstands function parameters

Validation: Good distribution, clearly one correct answer
```

## Further Reading

- Haladyna et al. (2002) "A review of multiple-choice item-writing guidelines"
- "Classroom Assessment Techniques" (Angelo & Cross)
- Porter et al. (2011) "Multi-institutional study on CS concept inventories"
