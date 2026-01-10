# Question Types for Programming Assessments

## Overview

Varied question types assess different cognitive levels and skills. This guide covers effective question patterns for Python assessments.

## Question Type Catalog

### 1. Multiple Choice Questions (MCQ)

**Purpose**: Test concept recognition, understanding, and decision-making

**Best For**: Bloom's levels 1-4 (Remember, Understand, Apply, Analyze)

**Structure**:
- Clear question stem
- One correct answer
- 3-4 plausible distractors based on common misconceptions

**Example**:
```
What will this code print?

x = [1, 2, 3]
y = x
y.append(4)
print(len(x))

A) 3
B) 4
C) Error
D) [1, 2, 3, 4]

Answer: B (lists are mutable and assigned by reference)
Distractors test: immutability (A), type confusion (D), error anticipation (C)
```

**Distractor Design**:
- Based on actual student errors
- Plausible if misunderstanding exists
- Not trick questions—test conceptual understanding

---

### 2. Code-Completion Questions

**Purpose**: Test ability to apply syntax and concepts to fill gaps

**Best For**: Bloom's levels 2-3 (Understand, Apply)

**Example**:
```python
# Complete this function to return the sum of even numbers
def sum_evens(numbers):
    total = 0
    for num in numbers:
        if ___________:  # What goes here?
            total += num
    return total

Answer: num % 2 == 0
```

**Variations**:
- Single blank (easiest)
- Multiple blanks requiring understanding of relationships
- Strategic blanks testing key concept

---

### 3. Code-Tracing Questions

**Purpose**: Test mental execution model

**Best For**: Bloom's level 2-3 (Understand, Apply)

**Example**:
```
Trace this code. What are the values of x and y at the end?

x = 5
y = 10

for i in range(3):
    x += i
    y -= 1

print(f"x={x}, y={y}")

Answer: x=8, y=7

Explanation:
i=0: x=5+0=5, y=10-1=9
i=1: x=5+1=6, y=9-1=8
i=2: x=6+2=8, y=8-1=7
```

---

### 4. Debugging Questions

**Purpose**: Test error recognition and problem-solving skills

**Best For**: Bloom's levels 4-5 (Analyze, Evaluate)

**Example**:
```python
# This code should calculate factorial but has bugs. Find and fix them.

def factorial(n):
    result = 0  # BUG 1
    for i in range(n):  # BUG 2
        result *= i
    return result

Answers:
BUG 1: result should initialize to 1 (not 0)
BUG 2: range should be range(1, n+1) to include n and avoid multiplying by 0
```

---

### 5. Code-Writing Questions

**Purpose**: Test ability to implement solutions from specifications

**Best For**: Bloom's levels 3-6 (Apply, Analyze, Evaluate, Create)

**Example**:
```
Write a function is_palindrome(text) that:
- Returns True if text reads same forwards/backwards
- Ignores case and spaces
- Returns False for empty strings

Test cases:
is_palindrome("racecar") → True
is_palindrome("hello") → False
is_palindrome("A man a plan a canal Panama") → True
is_palindrome("") → False
```

**Difficulty Levels**:
- **Easy**: Single step, clear algorithm
- **Medium**: Multiple steps, edge cases
- **Hard**: Multiple approaches, optimization required

---

### 6. Conceptual Explanation Questions

**Purpose**: Test deep understanding beyond code

**Best For**: Bloom's levels 2-5 (Understand, Analyze, Evaluate)

**Example**:
```
Explain the difference between a list and a tuple in Python.
Include:
1. Key difference in mutability
2. When to use each
3. Example of each

Rubric:
- Correctly identifies mutability (2 pts)
- Explains appropriate use cases (2 pts)
- Provides valid examples (1 pt)
```

---

### 7. Code-Review Questions

**Purpose**: Test ability to evaluate code quality

**Best For**: Bloom's levels 4-5 (Analyze, Evaluate)

**Example**:
```python
Review this code. Identify issues and suggest improvements.

def func(x):
    y = []
    for i in range(len(x)):
        if x[i] % 2 == 0:
            y.append(x[i])
    return y

Issues:
1. Poor names (func, x, y)
2. Using range(len()) instead of direct iteration
3. No docstring
4. Could use list comprehension

Improved:
def filter_even_numbers(numbers):
    """Return list of even numbers from input list."""
    return [num for num in numbers if num % 2 == 0]
```

---

### 8. Prediction Questions

**Purpose**: Test understanding of behavior without running code

**Best For**: Bloom's levels 2-3 (Understand, Apply)

**Example**:
```
Predict output without running:

def mystery(n):
    if n <= 1:
        return 1
    return n * mystery(n-1)

print(mystery(4))

Answer: 24 (factorial function)
```

---

### 9. Comparison Questions

**Purpose**: Test ability to distinguish between similar concepts

**Best For**: Bloom's levels 4-5 (Analyze, Evaluate)

**Example**:
```
Compare these three solutions for finding maximum in a list.
Discuss trade-offs: readability, efficiency, Pythonic style.

Solution A: Manual loop
Solution B: max() built-in
Solution C: reduce(lambda...)

Rubric:
- Analyzes readability (2 pts)
- Discusses efficiency (2 pts)
- Identifies most Pythonic (1 pt)
```

---

### 10. Project-Based Questions

**Purpose**: Test integration of multiple concepts

**Best For**: Bloom's level 6 (Create)

**Example**:
```
Build a simple contact manager that:
- Stores contacts (name, phone, email) in a list of dicts
- Functions: add_contact(), find_contact(), list_all()
- Handles errors (duplicate names, invalid inputs)
- Uses proper function structure with docstrings

Rubric:
- Correct data structure (5 pts)
- All functions work (10 pts)
- Error handling (5 pts)
- Code quality (5 pts)
```

## Bloom's Taxonomy Alignment

| Cognitive Level | Question Types |
|----------------|----------------|
| Remember | MCQ (recall), Fill-in-blank (basic) |
| Understand | Code-tracing, Prediction, Explanation |
| Apply | Code-completion, Code-writing (simple) |
| Analyze | Debugging, Comparison, Code-review |
| Evaluate | Code-review, Best-approach selection |
| Create | Project-based, Build-from-scratch |

## Question Design Principles

### Principle 1: Align with Learning Objectives
Every question should map to specific learning objective(s).

### Principle 2: Test Understanding, Not Memorization
Ask "why" and "how", not just "what".

### Principle 3: Avoid Trick Questions
Assess understanding, not reading comprehension tricks.

### Principle 4: Clear and Unambiguous
Eliminate confusion about what's being asked.

### Principle 5: Appropriate Difficulty
Match to learner level and instruction received.

## Cognitive Distribution Target

**Balanced Assessment** (aim for):
- 20% Remember/Understand (foundational)
- 40% Apply (core skill demonstration)
- 30% Analyze/Evaluate (higher-order thinking)
- 10% Create (synthesis and innovation)

**Avoid**: 80%+ recall questions (tests memory, not understanding)

## Further Reading

- Anderson & Krathwohl (2001) - Bloom's Taxonomy revision
- "Classroom Assessment Techniques" (Angelo & Cross)
