# Bloom's Taxonomy Assessment Alignment

## Overview

Different cognitive levels require different question types and assessment methods. This guide maps Bloom's levels to appropriate Python assessment formats.

## Bloom's Six Cognitive Levels

### Level 1: Remember (Knowledge)

**Definition**: Recall facts, terms, basic concepts

**Action Verbs**: define, list, name, identify, recall, recognize

**Assessment Methods**:
- Multiple-choice (vocabulary, syntax)
- Fill-in-blank (terminology)
- Matching (terms to definitions)

**Python Examples**:
```
Q: What keyword defines a function in Python?
A: def

Q: Which data structure is immutable?
A) List  B) Tuple  C) Dictionary  D) Set
Answer: B

Q: List three built-in Python data types.
A: int, str, list (or others)
```

**Target**: ~10-15% of assessment at this level

---

### Level 2: Understand (Comprehension)

**Definition**: Explain concepts, interpret meaning

**Action Verbs**: explain, describe, summarize, interpret, predict

**Assessment Methods**:
- Code-tracing (predict output)
- Explanation questions
- True/False with justification

**Python Examples**:
```
Q: Explain the difference between append() and extend() for lists.

Q: What will this code print? (code-tracing)
x = [1, 2, 3]
print(x * 2)

Q: Describe what a for loop does in your own words.
```

**Target**: ~15-20% of assessment

---

### Level 3: Apply (Application)

**Definition**: Use concepts in new situations

**Action Verbs**: apply, demonstrate, use, implement, execute

**Assessment Methods**:
- Code-completion
- Code-writing (simple, standard problems)
- Fill-in-blank (strategic gaps)

**Python Examples**:
```
Q: Write a function that takes a list and returns the sum of even numbers.

Q: Complete this code to iterate through a dictionary:
for ___, ___ in my_dict.___():
    print(f"{key}: {value}")

Q: Use a list comprehension to create a list of squares from 1 to 10.
```

**Target**: ~30-40% of assessment (core skill demonstration)

---

### Level 4: Analyze (Analysis)

**Definition**: Break down into parts, find relationships

**Action Verbs**: analyze, compare, contrast, differentiate, examine

**Assessment Methods**:
- Debugging questions
- Comparison questions
- Code-review

**Python Examples**:
```
Q: This code has three bugs. Find and fix them.
[buggy code provided]

Q: Compare these two approaches for finding duplicates in a list.
Discuss time complexity and readability.

Q: Analyze why this code is inefficient and suggest improvements.
```

**Target**: ~20-25% of assessment

---

### Level 5: Evaluate (Evaluation)

**Definition**: Make judgments based on criteria

**Action Verbs**: evaluate, judge, justify, critique, assess

**Assessment Methods**:
- Code-review with justification
- Best-approach selection with reasoning
- Trade-off analysis

**Python Examples**:
```
Q: Evaluate these three solutions for the same problem.
Which is best and why? Consider readability, efficiency, and Pythonic style.

Q: Justify your choice of data structure for this use case.

Q: Critique this implementation. What are its strengths and weaknesses?
```

**Target**: ~10-15% of assessment

---

### Level 6: Create (Synthesis)

**Definition**: Combine concepts to create something new

**Action Verbs**: create, design, develop, construct, produce

**Assessment Methods**:
- Project-based questions
- Design problems
- Build-from-scratch (complex)

**Python Examples**:
```
Q: Design and implement a simple contact manager with these requirements:
- Store contacts (name, phone, email)
- Add, search, delete functions
- Error handling for invalid inputs
- Persistent storage (file or database)

Q: Create a solution to [novel problem] using appropriate data structures
and algorithms. Explain your design decisions.

Q: Build a text-based game that uses classes, file I/O, and error handling.
```

**Target**: ~5-10% of assessment

---

## Cognitive Distribution Guidelines

### Beginner Assessment
```
20% Remember/Understand (foundational concepts)
50% Apply (demonstrate basic skills)
25% Analyze (simple debugging, comparison)
5% Evaluate/Create (simple projects)
```

**Rationale**: Focus on application of basic skills

### Intermediate Assessment
```
10% Remember/Understand (review)
40% Apply (standard problems)
35% Analyze (debugging, optimization)
15% Evaluate/Create (moderate projects)
```

**Rationale**: More higher-order thinking

### Advanced Assessment
```
5% Remember/Understand (terminology check)
30% Apply (complex implementations)
35% Analyze (complex debugging, trade-offs)
30% Evaluate/Create (design problems, projects)
```

**Rationale**: Emphasis on analysis, design, evaluation

## Assessment Type to Bloom's Level Mapping

| Assessment Type | Primary Bloom's Level | Secondary Level |
|----------------|----------------------|----------------|
| MCQ (recall) | Remember | - |
| MCQ (conceptual) | Understand | Analyze |
| Code-tracing | Understand | Apply |
| Fill-in-blank | Remember/Apply | - |
| Code-completion | Apply | - |
| Debugging | Analyze | Apply |
| Code-writing (simple) | Apply | - |
| Code-writing (complex) | Create | Analyze |
| Comparison | Analyze | Evaluate |
| Code-review | Evaluate | Analyze |
| Explanation | Understand | - |
| Project | Create | All others |

## Verifying Cognitive Level

Ask: "What does the student need to DO to answer correctly?"

**Remember**: Recall from memory
**Understand**: Explain in own words, predict
**Apply**: Use in standard situation
**Analyze**: Break down, find errors, compare
**Evaluate**: Judge quality, select best option
**Create**: Build new solution, design system

## Avoiding Over-Reliance on Lower Levels

**Problem**: Assessments that are 80%+ recall/recognition

**Issue**: Tests memorization, not understanding or application

**Fix**: Use cognitive distribution targets above

**Example of Improvement**:
```
BEFORE (mostly recall):
Q1: What does def do?
Q2: List three loop types
Q3: What is a variable?
Q4: Name two string methods
Q5: What does append() do?

AFTER (varied levels):
Q1: What does def do? (Remember)
Q2: Explain when to use a while loop vs for loop (Understand)
Q3: Write a function that [task] (Apply)
Q4: Debug this code (Analyze)
Q5: Design a solution to [problem] (Create)
```

## Further Reading

- Anderson & Krathwohl (2001) "A Taxonomy for Learning, Teaching, and Assessing"
- "Classroom Assessment and the National Science Education Standards"
- Crooks et al. (1996) "The validity of assessment for learning"
