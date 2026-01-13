# Prerequisite Analysis for Programming Education

## Overview

This document provides strategies for identifying prerequisite knowledge chains—the foundational concepts learners must master before tackling advanced topics.

---

## Core Principle

**Every learning objective has prerequisites**. Identifying them prevents:
- Frustrated learners without foundation
- Misconceptions building on weak understanding
- Unmet expectations about learner preparation

---

## Strategy 1: Dependency Mapping

### Technique
Create a directed graph where:
- **Nodes** = Concepts
- **Edges** = "Must know X before learning Y"

### Example: Python OOP

```
Variables & Data Types (base)
           ↓
Functions & Scope
    ↙       ↘
Classes   Modules
    ↓       ↓
Inheritance → Polymorphism
```

### How to Apply
1. List all concepts in your learning objective
2. For each, ask: "What must learners know to understand this?"
3. Trace chains backward to foundational knowledge
4. Identify gaps if you find missing steps

---

## Strategy 2: Cognitive Prerequisite Categories

### Category 1: Conceptual Prerequisites
**What ideas must exist in learner's mind?**

*Example: Before teaching decorators, learners need:*
- Functions as first-class objects
- Closures
- Function arguments and return values
- Basic function definition syntax

### Category 2: Procedural Prerequisites
**What can learners do already?**

*Example: Before async/await, learners need:*
- Write regular functions
- Handle function calls
- Understand callbacks (or promises/futures)
- Debug functions

### Category 3: Tool Prerequisites
**What development environments/tools?**

*Example: Before testing, learners need:*
- IDE or text editor comfort
- Command line basics (pip install, pytest run)
- Package management concepts

---

## Strategy 3: Bloom's Taxonomy Alignment

### Rule: Can't Apply Without Understanding

Before learners can write code (Apply level), they must:
1. **Remember**: Term definitions
2. **Understand**: Concept explanation

### Rule: Can't Analyze Without Application

Before learners analyze code (Analyze level), they must:
1. Remember + Understand
2. Apply in guided contexts

### Implications for Prerequisite Setting
- Set prerequisites to **minimum foundational level needed**
- Don't require "mastery"—students learn by doing
- List prerequisites at Remember/Understand level when possible

---

## Strategy 4: Knowledge Audit

### Questions to Ask

For each learning objective, answer:

**Conceptual Clarity**
- □ Can a learner without [prerequisite] understand this objective?
- □ Does this objective use terminology from [prerequisite]?
- □ Would examples of this objective demonstrate [prerequisite] concepts?

**Skill Building**
- □ Have learners practiced the prerequisite skills?
- □ Does this objective build directly on that practice?

**Context**
- □ Is [prerequisite] commonly known by target audience?
- □ If not, can it be taught in 5 minutes, or does it need full unit?

---

## Strategy 5: Common Python Prerequisite Chains

### Variables & Data Structures
```
Basic Syntax
    ↓
Variables & Assignment
    ↓
Data Types (int, str, list, dict)
    ↓
List/Dict Methods & Operations
    ↓
Nested Data Structures
```

### Control Flow
```
Variables & Comparison Operators
    ↓
Boolean Logic (and, or, not)
    ↓
if/elif/else Statements
    ↓
for Loops & Iteration
    ↓
while Loops & Break/Continue
    ↓
Loop Comprehension (list comp)
```

### Functions
```
Variables & Data Types
    ↓
Code Blocks & Indentation
    ↓
Function Definition & Calling
    ↓
Parameters & Arguments
    ↓
Return Values
    ↓
Scope & Namespaces
    ↓
Closures & Default Arguments
    ↓
Decorators & Higher-Order Functions
```

### Object-Oriented Programming
```
Functions (complete)
    ↓
Classes & Object Creation
    ↓
Attributes & Methods
    ↓
Constructors (__init__)
    ↓
Encapsulation & Property Access
    ↓
Inheritance & Hierarchy
    ↓
Polymorphism & Method Overriding
    ↓
Abstract Base Classes & Protocols
```

### Asynchronous Programming
```
Functions & Return Values
    ↓
Callbacks (or use of Promises if prior JS)
    ↓
Event Loops (concept)
    ↓
async/await Syntax
    ↓
asyncio Module
    ↓
Concurrent Programming Patterns
```

---

## Strategy 6: Red Flags for Missing Prerequisites

### Indicator 1: "Everyone Knows This"
**❌ Problem**: You skip fundamentals assuming they're obvious
- *Example*: Teaching decorators without explaining closures
- *Solution*: Define all technical terms even if "obvious"

### Indicator 2: Learner Confusion
**❌ Problem**: High failure rate or "just memorizing" without understanding
- *Solution*: Trace back—likely missing prerequisites

### Indicator 3: Circular Dependencies
**❌ Problem**: "Need to know A to learn B; need B to learn A"
- *Solution*: Break cycle by teaching A in isolation first, OR find different teaching order

### Indicator 4: Terminology Mismatch
**❌ Problem**: Objective uses terms not yet defined
- *Solution*: Add definition of those terms as prerequisites OR include brief term definitions in objective

---

## Strategy 7: Writing Clear Prerequisites

### Good Prerequisite Statement
```
Prerequisites for "Implement Custom Iterator Classes":
- Understand for loops and iteration
- Define classes with __init__ and methods
- Understand the difference between class and instance attributes
- Explain how __init__ initializes objects
```

✅ **Clear?** Yes—each is specific and verifiable
✅ **Necessary?** Yes—can't succeed without these
✅ **Sufficient?** Yes—having these is enough to begin

### Poor Prerequisite Statement
```
"Know Python" / "Understand OOP"
```

❌ **Clear?** No—too vague
❌ **Sufficient?** Unclear—what parts of OOP?

---

## Strategy 8: Prerequisite Depth Levels

### Level 1: Awareness (Shallow)
- Learner has heard the term
- Recognizes it in code
- Might not apply it yet
- *Use for*: Optional context, enrichment

### Level 2: Fluency (Medium)
- Learner understands the concept
- Can explain it in own words
- Can apply in basic contexts
- *Use for*: Most prerequisites

### Level 3: Mastery (Deep)
- Learner can apply in any context
- Can debug related issues
- Can teach it to others
- *Use for*: Only critical foundations

---

## Quick Checklist for Prerequisite Identification

For each learning objective:

- [ ] List all technical terms used
- [ ] For each term: Is it defined in objective, or is learner expected to know it?
- [ ] Trace dependency chain backward (A requires B, B requires C, ...)
- [ ] Stop when you reach foundational knowledge (everyone should have this)
- [ ] Verify each prerequisite is Remember/Understand level (not Apply or Create)
- [ ] Check: Is this the minimal set? Can any be removed?
- [ ] Validate: Could someone with these prerequisites actually learn this objective?

---

## Examples: Building Prerequisite Lists

### Example 1: "Implement a Binary Search Algorithm"

**Main Objective**: Implement a binary search algorithm

**Prerequisite Chain**:
1. Understand array/list indexing
2. Understand comparison operators (<, >, ==)
3. Understand while loops
4. Understand the concept of "divide and conquer"
5. Know logarithmic vs linear time complexity (at high level)

**Minimal Prerequisites**:
- Understand list indexing
- Understand while loops
- Understand comparison operators

### Example 2: "Design a REST API with FastAPI"

**Main Objective**: Design and implement a REST API endpoint

**Prerequisite Chain**:
1. Understand HTTP methods (GET, POST, PUT, DELETE)
2. Understand JSON format
3. Define functions with decorators
4. Understand route parameters and request bodies
5. Handle errors and status codes

**Minimal Prerequisites**:
- Functions and parameters
- Basic understanding of HTTP
- JSON basics
- Decorators (syntax, not deep understanding)

---

## Summary

**Prerequisites are not barriers; they're the foundation**. Identify them to:
- Help learners assess readiness
- Design effective learning sequences
- Support struggling learners (identify gaps!)
- Document your curriculum clearly
