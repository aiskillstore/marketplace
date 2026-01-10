# Prompt Design Template for AI-Assisted Programming

## Overview

This template provides a structured approach for designing effective prompts when using AI coding assistants for learning programming. Use this template to craft clear, specific prompts that elicit useful responses while maintaining learning integrity.

---

## Basic Prompt Structure

### Minimal Effective Prompt

```
[CONTEXT] I'm working on [brief description of task/project]
[TASK] [What you want AI to do]
[CONSTRAINTS] [Important requirements or limitations]
```

**Example**:
```
I'm working on a Python data analysis script.
Write a function to calculate the median of a list of numbers.
Use only standard library (no numpy), include error handling for empty lists.
```

---

## Detailed Prompt Template

### 1. Context Setting

**Purpose**: Help AI understand your situation

```
Context:
- Topic/Concept: [What you're learning or working on]
- Your Level: [Beginner/Intermediate/Advanced in this topic]
- Current Stage: [What you've done so far]
- Environment: [Language, version, tools, constraints]
```

**Example**:
```
Context:
- Topic: Python exception handling
- My Level: Beginner - just learned try/except basics
- Current Stage: Writing a file-reading function
- Environment: Python 3.10, no external libraries
```

---

### 2. Task Specification

**Purpose**: Clearly state what you want

```
Task:
[Specific, actionable request]

OR choose type:
□ Generate code: [What the code should do]
□ Explain code: [What you want explained]
□ Debug code: [What's wrong, expected vs. actual behavior]
□ Review code: [What aspects to focus on]
□ Explore alternatives: [Current approach, what alternatives you want]
```

**Example - Generate**:
```
Task: Generate code
Write a function that reads a JSON file and returns the data as a Python dictionary.
```

**Example - Explain**:
```
Task: Explain code
Explain how this list comprehension works step-by-step:
result = [x**2 for x in range(10) if x % 2 == 0]
```

**Example - Debug**:
```
Task: Debug code
This function should calculate the average but returns wrong values.
Expected: average([1, 2, 3]) → 2.0
Actual: average([1, 2, 3]) → 2
```

---

### 3. Requirements and Constraints

**Purpose**: Guide AI toward appropriate solutions

```
Requirements:
- Functional: [What it must do]
- Technical: [Language features, style, conventions]
- Quality: [Performance, readability, testability needs]

Constraints:
- What NOT to use: [Forbidden libraries, patterns, approaches]
- Limitations: [Time/space complexity, compatibility]
```

**Example**:
```
Requirements:
- Handle both files that exist and files that don't
- Return None if file not found (don't raise exception)
- Use type hints
- Follow PEP 8 style

Constraints:
- Use only standard library (no external JSON libraries)
- Must work with Python 3.8+
```

---

### 4. Output Format Specification

**Purpose**: Get exactly what you need

```
Please provide:
□ Code only
□ Code with inline comments
□ Code + explanation
□ Code + examples
□ Code + tests
□ Step-by-step breakdown
□ Multiple approaches with comparison
```

**Example**:
```
Please provide:
1. The complete function with type hints and docstring
2. 3-5 test cases covering normal and edge cases
3. Brief explanation of how error handling works
```

---

### 5. Specific Focus Areas (Optional)

**Purpose**: Direct attention to what matters most

```
Focus on:
- [Aspect 1, e.g., "Explain the algorithm clearly"]
- [Aspect 2, e.g., "Show edge case handling"]
- [Aspect 3, e.g., "Compare time complexity with alternatives"]
```

**Example**:
```
Focus on:
- Clear variable names (I struggle with naming)
- Edge case handling (empty file, malformed JSON)
- Error messages that help users understand what went wrong
```

---

## Prompt Templates by Task Type

### Template A: Code Generation

```
I'm learning [TOPIC].

Task: Write [LANGUAGE] code to [SPECIFIC TASK].

Requirements:
- [Requirement 1]
- [Requirement 2]
- [Style/convention requirements]

Constraints:
- [What NOT to use]
- [Performance/compatibility needs]

Please provide:
- The code with [type hints/docstring/comments]
- [Number] test cases
- [Any additional explanations needed]
```

**Example**:
```
I'm learning Python file I/O.

Task: Write Python code to safely read a text file line by line and count word frequency.

Requirements:
- Handle files that don't exist (return empty dict, don't crash)
- Case-insensitive counting (treat "The" and "the" as same word)
- Ignore punctuation
- Use type hints

Constraints:
- Standard library only (no nltk or external packages)
- Should work for files up to 100MB

Please provide:
- The complete function with docstring
- 3 test cases (normal file, empty file, non-existent file)
- Brief explanation of the approach
```

---

### Template B: Explanation Request

```
I'm learning [TOPIC] and I'm confused about [SPECIFIC CONFUSION].

Here's the code I don't understand:
[PASTE CODE]

Please explain:
- [Question 1]
- [Question 2]
- [Question 3]

I understand [WHAT YOU DO UNDERSTAND], but not [WHAT YOU DON'T].
```

**Example**:
```
I'm learning Python decorators and I'm confused about how they work.

Here's the code I don't understand:
def log_function(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_function
def add(a, b):
    return a + b

Please explain:
- What happens when I write @log_function above add()?
- Where does the print statement execute?
- Why does wrapper need *args and **kwargs?

I understand that functions can return other functions, but not how the decorator syntax connects to this.
```

---

### Template C: Debugging Help

```
I'm working on [TASK] and encountering [PROBLEM].

Expected behavior: [WHAT SHOULD HAPPEN]
Actual behavior: [WHAT DOES HAPPEN]

Error message (if any):
[PASTE ERROR]

Code:
[PASTE RELEVANT CODE]

What I've tried:
- [Attempt 1 and result]
- [Attempt 2 and result]

My hypothesis: [YOUR GUESS AT THE ISSUE]

Can you identify the bug and explain why it causes this behavior?
```

**Example**:
```
I'm working on a function to filter a list and encountering unexpected output.

Expected behavior: filter_even([1, 2, 3, 4]) should return [2, 4]
Actual behavior: filter_even([1, 2, 3, 4]) returns []

Error message: None (no error, just wrong output)

Code:
def filter_even(numbers):
    result = []
    for num in numbers:
        if num % 2 = 0:  # Keep even numbers
            result.append(num)
    return result

What I've tried:
- Printing num inside loop - it iterates correctly
- Checking len(result) after loop - it's 0

My hypothesis: Maybe the condition isn't working, but I'm not sure why.

Can you identify the bug and explain why it causes this behavior?
```

---

### Template D: Code Review Request

```
I've written code for [TASK]. Please review it.

Focus on:
- [Aspect 1, e.g., Readability]
- [Aspect 2, e.g., Error handling]
- [Aspect 3, e.g., Performance]
- [Aspect 4, e.g., Best practices]

Code:
[PASTE CODE]

Specific concerns:
- [Concern 1, e.g., "Is my function too long?"]
- [Concern 2, e.g., "Am I handling errors correctly?"]

Please suggest improvements and explain WHY each improvement matters.
```

**Example**:
```
I've written code to parse CSV files. Please review it.

Focus on:
- Error handling (is it robust enough?)
- Code organization (should this be split into multiple functions?)
- PEP 8 compliance

Code:
def readcsv(f):
    d = []
    for l in open(f):
        d.append(l.strip().split(','))
    return d

Specific concerns:
- I'm not closing the file - is this a problem?
- Variable names are short - is this okay?
- No error handling - what should I add?

Please suggest improvements and explain WHY each improvement matters.
```

---

### Template E: Alternative Approaches

```
I solved [PROBLEM] using [CURRENT APPROACH].

Here's my solution:
[PASTE CODE]

Questions:
- What are alternative approaches to this problem?
- What are the pros/cons of each approach (including mine)?
- When would you use each approach?

Context: [Any relevant constraints or goals]
```

**Example**:
```
I solved the problem of finding duplicates in a list using nested loops.

Here's my solution:
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

Questions:
- What are alternative approaches to this problem?
- What are the pros/cons of each approach (including mine)?
- When would you use each approach?

Context: This is for a learning exercise, so I care about understanding different approaches, not just the fastest solution.
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Vague Request
```
Bad: "Write code for sorting"
```

**Why Bad**: AI doesn't know what to sort, which algorithm, what language, what constraints.

**Fix**:
```
Good: "Write a Python function to sort a list of dictionaries by the 'date' key (newest first), handling missing 'date' keys by putting them at the end."
```

---

### ❌ Anti-Pattern 2: No Context
```
Bad: "Fix this code: [paste 100 lines]"
```

**Why Bad**: AI doesn't know what the code should do, what's wrong, or what you've tried.

**Fix**:
```
Good: "This code should calculate Fibonacci numbers but returns wrong values for n > 5. Expected: fib(6) = 8, Actual: fib(6) = 5. Code: [paste specific function]"
```

---

### ❌ Anti-Pattern 3: Assuming AI Knows Your Context
```
Bad: "How do I fix the bug in my calculate function?"
```

**Why Bad**: AI doesn't know what your function does, what the bug is, or what code you have.

**Fix**:
```
Good: "My calculate_discount() function should apply a 10% discount but is only applying 1%. Code: [paste]. I think the issue is in line 5 but not sure why."
```

---

### ❌ Anti-Pattern 4: Overloading Single Prompt
```
Bad: "Write a complete web app with authentication, database, API, frontend, tests, deployment scripts, and documentation."
```

**Why Bad**: Too much at once. Overwhelming for AI and student.

**Fix**:
```
Good: Start with "Write a Python Flask route for user login that checks credentials against a database. Include error handling." Then iterate.
```

---

## Prompt Quality Checklist

Before submitting your prompt, check:

□ **Clear Context**: Did I explain what I'm working on?
□ **Specific Task**: Is it clear what I want AI to do?
□ **Appropriate Constraints**: Did I specify important requirements?
□ **Output Format**: Did I say how I want the response structured?
□ **Testable**: Can I verify if the AI output is correct?
□ **Learning-Focused**: Will this help me learn, not just complete a task?

---

## Progressive Prompt Refinement

### Initial Prompt (Basic)
```
"Write a function to validate emails"
```

### Refined Prompt (Better)
```
"Write a Python function that validates email addresses, checking for @ symbol and domain extension"
```

### Optimized Prompt (Best)
```
"Write a Python function to validate email addresses with these requirements:
- Check for @ symbol
- Verify domain has extension (.com, .org, etc.)
- Return True/False
- Use regex
- Include docstring and type hints
- Provide 3 test cases: valid email, missing @, missing domain

Example inputs/outputs:
- 'user@example.com' → True
- 'userexample.com' → False (no @)
- 'user@example' → False (no domain extension)"
```

**Lesson**: Start simple, but add specificity when needed for better results.

---

## Summary: Keys to Effective Prompts

1. **Context**: Always provide background
2. **Specificity**: Be precise about what you want
3. **Constraints**: State requirements and limitations
4. **Format**: Specify how you want the output
5. **Verifiability**: Make sure you can test the result
6. **Learning Focus**: Ask in ways that promote understanding
7. **Iteration**: Refine prompts based on responses
8. **Critical Thinking**: Always verify and understand AI outputs

**Remember**: The quality of AI output depends heavily on the quality of your prompt. Invest time in crafting good prompts - it's a valuable skill!
