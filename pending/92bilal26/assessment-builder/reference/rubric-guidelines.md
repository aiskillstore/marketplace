# Rubric Design Guidelines

## Overview

Rubrics provide clear evaluation criteria for open-ended questions and projects, ensuring consistent, fair assessment and giving students transparent expectations.

## Types of Rubrics

### Analytic Rubric
Evaluates each criterion separately

**Use When**: Need detailed feedback on multiple dimensions

**Structure**: Multiple criteria, each with performance levels

### Holistic Rubric
Single overall score

**Use When**: Quick assessment, overall quality matters more than parts

**Structure**: Single rating scale with level descriptions

## Analytic Rubric Structure

### Components

1. **Criteria**: Specific aspects being evaluated
2. **Performance Levels**: Usually 3-5 levels (e.g., Excellent, Good, Fair, Poor)
3. **Descriptors**: Clear description of what each level looks like
4. **Points**: Numerical values for scoring

### Template

```
Criterion: [Aspect being evaluated]
Points Possible: X

Excellent (4 pts):
[Specific, observable description]

Good (3 pts):
[Specific, observable description]

Fair (2 pts):
[Specific, observable description]

Poor (1 pt):
[Specific, observable description]
```

## Common Criteria for Programming Assignments

### 1. Correctness / Functionality
**Weight**: 40-50% typically

**Levels**:
- **Excellent**: Works for all test cases, handles edge cases
- **Good**: Works for standard cases, minor edge case issues
- **Fair**: Works for simple cases, fails on some inputs
- **Poor**: Doesn't produce correct output or doesn't run

### 2. Code Quality / Readability
**Weight**: 20-30%

**Levels**:
- **Excellent**: Clear naming, proper structure, well-commented
- **Good**: Mostly readable, minor naming/structure issues
- **Fair**: Some poor naming, hard to follow in places
- **Poor**: Confusing structure, poor names, hard to understand

### 3. Efficiency / Algorithm Choice
**Weight**: 15-20%

**Levels**:
- **Excellent**: Optimal approach, appropriate data structures
- **Good**: Reasonable approach, minor inefficiencies
- **Fair**: Works but inefficient algorithm/structure chosen
- **Poor**: Very inefficient or inappropriate approach

### 4. Error Handling
**Weight**: 10-15%

**Levels**:
- **Excellent**: Handles all edge cases and invalid inputs gracefully
- **Good**: Handles most edge cases
- **Fair**: Minimal error handling
- **Poor**: No error handling, crashes on edge cases

### 5. Style / Best Practices
**Weight**: 5-10%

**Levels**:
- **Excellent**: Follows PEP 8, uses Pythonic idioms
- **Good**: Generally follows conventions, minor style issues
- **Fair**: Some style violations, non-Pythonic patterns
- **Poor**: Ignores style guidelines

## Example: Complete Analytic Rubric

```
Assignment: Write a function to find duplicates in a list

Criterion 1: Correctness (40 points)
Excellent (40 pts): Correctly identifies all duplicates, handles empty lists,
returns appropriate data structure, works for all test cases

Good (30 pts): Correctly identifies duplicates in standard cases, minor issue
with edge cases (empty list, no duplicates, all duplicates)

Fair (20 pts): Partially works, misses some duplicates or incorrect for certain
input types

Poor (10 pts): Doesn't produce correct results or doesn't execute

Criterion 2: Code Quality (25 points)
Excellent (25 pts): Clear function/variable names, logical structure, helpful
comments, includes docstring

Good (19 pts): Readable with mostly clear names, minor structure issues, has
docstring

Fair (13 pts): Some confusing names or structure, missing docstring or comments

Poor (6 pts): Very poor names (x, y, z), confusing logic, no documentation

Criterion 3: Efficiency (20 points)
Excellent (20 pts): Uses optimal approach (e.g., set for O(n) lookup), appropriate
data structure

Good (15 pts): Reasonable approach with minor inefficiencies (e.g., nested loops
but small data)

Fair (10 pts): Inefficient approach (e.g., nested loops with repeated checks)

Poor (5 pts): Very inefficient (e.g., triple-nested loops)

Criterion 4: Error Handling (10 points)
Excellent (10 pts): Handles empty list, non-list inputs, validates types

Good (7 pts): Handles empty list and basic edge cases

Fair (5 pts): Minimal error handling (e.g., only checks if list is empty)

Poor (2 pts): No error handling, crashes on edge cases

Criterion 5: Python Style (5 points)
Excellent (5 pts): Follows PEP 8, uses list comprehensions or sets appropriately

Good (4 pts): Generally Pythonic, minor style issues

Fair (3 pts): Some non-Pythonic patterns, style violations

Poor (1 pt): Ignores Python conventions

Total: 100 points
Passing: 60 points
```

## Rubric Design Principles

### Principle 1: Specific and Observable
Use concrete descriptions, not vague terms.

**Vague**: "Code is good"
**Specific**: "Function names describe purpose, variables use descriptive names,
code includes docstring with parameter descriptions"

### Principle 2: Progressive Levels
Each level should represent a meaningful step in quality.

### Principle 3: Achievable Top Level
Excellent should be attainable with reasonable effort, not perfection.

### Principle 4: Clear Distinction
Levels should be clearly different, not ambiguous.

### Principle 5: Aligned with Learning Objectives
Criteria match what was taught and intended to be assessed.

## Common Pitfalls

### Pitfall 1: Vague Descriptors
"Good code quality" - What does this mean specifically?

**Fix**: "Clear variable names, logical organization, helpful comments"

### Pitfall 2: All-or-Nothing
Only "perfect" or "completely wrong" levels

**Fix**: Include intermediate levels for partial understanding

### Pitfall 3: Overlapping Criteria
Same thing assessed in multiple criteria

**Fix**: Ensure each criterion is distinct

### Pitfall 4: Subjective Language
"Nice code", "Pretty good", "Okay"

**Fix**: Use objective, measurable descriptors

## Single-Point Rubric (Alternative)

Lists criteria and only describes proficient level. Feedback noted in two columns:
- **Concerns**: Areas below proficiency
- **Strengths**: Areas above proficiency

**Advantage**: Less time to create, focuses on feedback

**Disadvantage**: Less transparent scoring

## Rubric Validation

Before using rubric:
- [ ] All criteria aligned with learning objectives
- [ ] Descriptors are specific and observable
- [ ] Levels are clearly distinguishable
- [ ] Top level is achievable
- [ ] Points/weights reflect relative importance
- [ ] Clear passing threshold
- [ ] No overlapping or redundant criteria
- [ ] Language is objective, not subjective

## Providing Feedback with Rubrics

**Include**:
1. Score for each criterion
2. Explanation of score (which descriptor matched)
3. Specific examples from student work
4. Suggestions for improvement

**Example Feedback**:
```
Correctness: 30/40 (Good)
Your function works correctly for standard lists like [1,2,3,2,4,3] but doesn't
handle the edge case of an empty list (raises error). Add a check at the
beginning: if not numbers: return []

Code Quality: 25/25 (Excellent)
Great use of descriptive names (find_duplicates, seen_items). Your docstring
clearly explains parameters and return value. Code is easy to follow.
```

## Further Reading

- "Classroom Assessment Techniques" (Angelo & Cross)
- Stevens & Levi (2013) "Introduction to Rubrics"
- AAC&U VALUE Rubrics
