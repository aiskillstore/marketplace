# Spaced Repetition for Programming Skills

## Overview

Spaced repetition is a learning technique that involves reviewing material at increasing intervals. For programming, this means revisiting concepts across multiple lessons and exercises rather than practicing intensively once and never returning.

## The Forgetting Curve

Without review, we forget:
- **20 minutes later**: 40% forgotten
- **1 day later**: 60% forgotten
- **1 week later**: 75% forgotten
- **1 month later**: 80%+ forgotten

Spaced repetition combats this by reviewing just before we'd forget.

## Optimal Review Intervals

**First review**: 1 day after initial learning
**Second review**: 3 days after first review
**Third review**: 1 week after second review
**Fourth review**: 2 weeks after third review
**Fifth review**: 1 month after fourth review

## Application to Python Exercises

### Strategy 1: Spiral Curriculum

Revisit concepts across lessons:

```
Week 1: Introduce lists (.append, .remove, indexing)
Week 2: New topic (dictionaries) + list review exercises
Week 3: New topic (functions) + use lists in examples
Week 4: New topic (classes) + classes with list attributes
Week 6: Project using lists, dictionaries, functions, classes together
```

### Strategy 2: Mixed Exercise Sets

Each exercise set includes:
- **60%** new concept practice
- **30%** recent concepts (last 1-2 lessons)
- **10%** older concepts (3+ lessons ago)

**Example Exercise Set (Lesson 5):**
```
Exercise 1: Current concept (loops)
Exercise 2: Current concept (loops)
Exercise 3: Recent concept (conditionals from Lesson 4)
Exercise 4: Current concept (loops)
Exercise 5: Old concept (variables from Lesson 1)
Exercise 6: Current concept (loops)
Exercise 7: Recent concept (lists from Lesson 3)
```

### Strategy 3: Progressive Complexity

Each time you revisit a concept, increase difficulty:

**Week 1** (Introduction):
```python
# Basic list usage
fruits = ["apple", "banana"]
fruits.append("cherry")
print(fruits)
```

**Week 2** (Review + Slightly More Complex):
```python
# Use lists in conditional logic
scores = [85, 92, 78, 88, 95]
if 90 in scores:
    print("At least one A grade!")
```

**Week 3** (Review + Integration with New Concept):
```python
# Use lists with functions
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

grades = [85, 92, 78, 88, 95]
avg = calculate_average(grades)
```

**Week 5** (Review + Advanced Usage):
```python
# List comprehensions (new) using prior list knowledge
numbers = [1, 2, 3, 4, 5]
squared = [n**2 for n in numbers if n % 2 == 0]
```

### Strategy 4: Cumulative Projects

**Mini-Project Each Week** that requires previous concepts:

- **Week 2 Project**: Use Week 1 + Week 2 concepts
- **Week 3 Project**: Use Week 1 + Week 2 + Week 3 concepts
- **Week 4 Project**: Use all concepts learned so far

## Implementing in Exercise Design

### Tagging Exercises

Tag each exercise with concepts it practices:

```yaml
exercise_id: "EX-305"
primary_concept: "loops"  # New this lesson
secondary_concepts:
  - "lists"  # From Lesson 2
  - "conditionals"  # From Lesson 3
difficulty: "medium"
last_practiced:
  lists: "2 lessons ago"
  conditionals: "1 lesson ago"
```

### Spacing Calculator

Determine when to revisit:

```
Concept: List methods
- Introduced: Lesson 1
- First review: Lesson 2 (1 lesson gap)
- Second review: Lesson 4 (2 lesson gap)
- Third review: Lesson 7 (3 lesson gap)
- Fourth review: Lesson 11 (4 lesson gap)
```

## Practical Patterns

### Pattern 1: "Throwback Thursday"

Every 4th lesson, dedicate time to reviewing concepts from 3-4 weeks ago.

### Pattern 2: Progressive Problem Revisit

Same problem, different complexity:

**Week 1**: Write function to sum a list
**Week 3**: Extend to handle empty lists and non-numeric values
**Week 6**: Optimize for very large lists, add type hints and tests

### Pattern 3: Concept Combination Matrix

Later exercises combine previously learned concepts:

```
Lesson 5 combines:
- Loops (Lesson 2) + Dictionaries (Lesson 4)
- Functions (Lesson 3) + Lists (Lesson 1)
```

## Balancing New vs Review

**Early Course** (Weeks 1-4):
- 70% new concept practice
- 30% review

**Mid Course** (Weeks 5-8):
- 60% new concept practice
- 40% review

**Late Course** (Weeks 9-12):
- 50% new concepts
- 50% review and integration

## Benefits of Spaced Repetition

1. **Reduced cramming**: Knowledge built incrementally
2. **Better retention**: Long-term memory formation
3. **Transfer**: Ability to apply concepts in new contexts
4. **Confidence**: Repeated success builds competence

## Further Reading

- Cepeda et al. (2006) "Distributed practice in verbal recall tasks"
- Rohrer & Taylor (2007) "The shuffling of mathematics problems improves learning"
- "Make It Stick" (Brown, Roediger, McDaniel) - Chapter on spacing
