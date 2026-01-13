# Prompt Engineering Pedagogy: Teaching Effective AI Interaction

## Overview

This document provides pedagogical strategies for teaching prompt engineering to programming students. It covers how to help learners develop intuition for crafting effective prompts, iterate on prompt quality, and understand the tradeoffs between specificity and creativity when working with AI coding assistants.

---

## Why Teach Prompt Engineering in Programming Education

### The New Core Skill

Prompt engineering is becoming as fundamental as debugging, testing, or version control. Modern developers spend significant time:
- Asking AI to generate code scaffolds
- Requesting explanations of complex code
- Getting help debugging errors
- Exploring alternative approaches
- Learning new libraries and frameworks

**Teaching prompt engineering is teaching effective tool use** - a meta-skill that amplifies all other programming skills.

---

### Learning Outcomes for Prompt Engineering

Students should be able to:

1. **Craft Clear, Specific Prompts**
   - State context (what they're working on)
   - Define constraints (language, style, dependencies)
   - Specify desired output format

2. **Iterate on Prompts Based on Results**
   - Recognize when AI output is incomplete or wrong
   - Refine prompts with additional context
   - Use follow-up questions effectively

3. **Evaluate AI-Generated Code Critically**
   - Verify correctness (does it work?)
   - Assess code quality (is it maintainable?)
   - Identify security issues or bad practices

4. **Balance AI Assistance with Learning**
   - Know when to use AI (appropriate contexts)
   - Know when to struggle independently (deep learning)
   - Use AI to accelerate, not replace, understanding

---

## Teaching Framework: The Four Prompt Competencies

### Competency 1: Context Setting

**What**: Providing relevant background information so AI understands the situation.

**Why Important**: AI performs better with context. "Write a function to sort" is vague. "Write a Python function to sort a list of dictionaries by the 'date' key, handling missing dates" is actionable.

**How to Teach**:

#### Lesson Activity: Context Expansion Exercise
```
Starting Prompt (Vague):
  "Write a function to validate email"

Add Context Layer 1 (Language/Environment):
  "Write a Python function to validate email addresses"

Add Context Layer 2 (Requirements):
  "Write a Python function that validates email addresses, returning True/False,
   checking for @ symbol and domain extension"

Add Context Layer 3 (Edge Cases):
  "Write a Python function that validates email addresses, returning True/False.
   Should handle: missing @, multiple @, missing domain, empty string"
```

**Teaching Strategy**:
- Start with vague prompt
- Have students identify missing information
- Build prompt incrementally
- Compare AI outputs at each stage

**Assessment**:
Give students a task (e.g., "Create a password validator"). Have them write:
1. Minimal prompt
2. Context-rich prompt
3. Reflection: How did AI outputs differ?

---

### Competency 2: Constraint Specification

**What**: Defining boundaries and requirements for the AI's output.

**Why Important**: AI can solve problems in many ways. Constraints guide it toward solutions that fit your specific needs (style, dependencies, performance).

**How to Teach**:

#### Common Constraint Categories

**Language and Version**:
```
"Write a Python 3.10+ function using type hints"
"Write JavaScript ES6 code (no var, use const/let)"
```

**Style and Conventions**:
```
"Follow PEP 8 style guidelines"
"Use descriptive variable names, avoid abbreviations"
"Include docstrings with parameter descriptions"
```

**Dependencies**:
```
"Use only standard library, no external packages"
"Use pandas DataFrame for data manipulation"
```

**Performance**:
```
"Optimize for readability, not performance"
"This needs to handle 1M+ records efficiently"
```

**Format**:
```
"Return a dictionary with keys: 'status', 'data', 'error'"
"Output as JSON with pretty formatting"
```

#### Lesson Activity: Constraint Experimentation
Give students a problem and have them request solutions with different constraints:
```
Task: Sort a list of student records by GPA

Prompt 1 (No constraints):
  "Write code to sort students by GPA"

Prompt 2 (Add style constraint):
  "Write Pythonic code to sort students by GPA, using built-in sorted() function"

Prompt 3 (Add performance constraint):
  "Write highly efficient code to sort 100K+ student records by GPA in-place"

Prompt 4 (Add format constraint):
  "Write a function that sorts students by GPA and returns a list of dictionaries
   with keys: name, gpa, rank"
```

**Discussion**: How did constraints change the AI's approach? Which constraints were most important?

---

### Competency 3: Output Format Specification

**What**: Defining exactly how you want the AI to structure its response.

**Why Important**: Clear output format requests save time and reduce back-and-forth. AI can provide code + explanation + tests if you ask for it.

**How to Teach**:

#### Output Format Patterns

**Code Only**:
```
"Provide only the code, no explanations"
```

**Code + Inline Comments**:
```
"Provide the code with inline comments explaining each step"
```

**Code + Explanation**:
```
"Provide:
1. The complete code
2. A brief explanation of how it works
3. Example usage"
```

**Code + Tests**:
```
"Provide:
- The function implementation
- 3-5 unit tests using pytest
- Example outputs for each test"
```

**Step-by-Step Breakdown**:
```
"Break down the solution into steps:
1. Pseudocode outline
2. Implementation of each step
3. Complete code with steps integrated"
```

#### Lesson Activity: Format Specification Practice
Give students a coding task and have them specify different output formats:
```
Task: Parse a CSV file

Format Request 1:
  "Write a Python function to parse CSV. Include the function, a docstring,
   and example usage."

Format Request 2:
  "Write a Python function to parse CSV. Provide:
   1. The function with type hints
   2. Explanation of how it handles edge cases
   3. Three test cases
   4. Error handling examples"
```

**Assessment**: Did students get what they asked for? What format is most useful for learning?

---

### Competency 4: Iterative Refinement

**What**: Using follow-up prompts to clarify, correct, or extend AI outputs.

**Why Important**: First prompts rarely produce perfect results. Learning to iterate effectively is crucial.

**How to Teach**:

#### Refinement Strategies

**Strategy 1: Clarification**
```
Initial prompt: "Write a function to calculate average"
AI provides: [code without handling empty lists]

Follow-up: "How does your function handle an empty list? Add error handling."
```

**Strategy 2: Extension**
```
Initial prompt: "Write a function to read a file"
AI provides: [basic file reading]

Follow-up: "Now add error handling for file not found and permission denied.
             Also add a parameter to specify encoding."
```

**Strategy 3: Correction**
```
Initial prompt: "Write code to find duplicates in a list"
AI provides: [incorrect algorithm]

Follow-up: "This code has a bug - it only finds the first duplicate.
             Fix it to return all duplicate values."
```

**Strategy 4: Alternative Approaches**
```
Initial prompt: "Write code to merge two sorted lists"
AI provides: [solution A]

Follow-up: "Show me an alternative approach using a different algorithm.
             Compare the time complexity of both approaches."
```

#### Lesson Activity: Prompt Dialogue Simulation

**Setup**: Give students a starting prompt and an initial AI response (you provide). Have them write follow-up prompts.

```
Starting Prompt:
  "Write a Python function to calculate factorial"

Initial AI Response:
  def factorial(n):
      result = 1
      for i in range(1, n):
          result *= i
      return result

Student Task:
  This code has a bug. Write follow-up prompts to:
  1. Identify the bug
  2. Fix the bug
  3. Add input validation for negative numbers
  4. Add a docstring
```

**Discussion**: How did students approach refinement? What made follow-ups effective?

---

## Teaching Prompt Quality Evaluation

### Dimensions of Prompt Quality

#### 1. Clarity
**Poor**: "Make a function"
**Good**: "Write a Python function that takes a string and returns the string reversed"

**Teaching**: Have students identify what information is missing from vague prompts.

---

#### 2. Specificity
**Poor**: "Write sorting code"
**Good**: "Write a Python function using the built-in sorted() to sort a list of dictionaries by the 'age' key in descending order"

**Teaching**: Show how specificity reduces ambiguity and gets better first-try results.

---

#### 3. Context Completeness
**Poor**: "Fix this code" [paste code with no context]
**Good**: "I'm building a web scraper. This code should extract product prices from HTML but returns None. Here's the HTML structure: [example]. What's wrong?"

**Teaching**: Have students brainstorm what context is needed for different types of requests (debugging, generating, explaining).

---

#### 4. Testability
**Poor**: "Write good code for data processing"
**Good**: "Write a Python function that filters a list of dictionaries, keeping only entries where 'status' is 'active'. Include test cases for empty list, all active, all inactive, and mixed."

**Teaching**: Discuss how including test criteria in prompts improves output quality and helps verify correctness.

---

## Scaffolding Prompt Engineering Skills

### Stage 1: Guided Templates (Beginner)

Provide fill-in-the-blank prompt templates:

```
Template 1: Basic Code Request
"Write a [LANGUAGE] function that [WHAT IT DOES]. It should [SPECIFIC REQUIREMENTS].
 Use [STYLE/CONSTRAINTS]."

Example:
"Write a Python function that validates passwords. It should check length (min 8 chars),
 require at least one number, and return True/False. Use descriptive variable names."
```

```
Template 2: Debugging Request
"I'm working on [CONTEXT]. This code [WHAT IT SHOULD DO] but instead [WHAT IT DOES].
 Here's the code: [CODE]. What's wrong and how do I fix it?"
```

**Teaching Strategy**: Start with templates. Students fill in blanks. Gradually remove scaffolding.

---

### Stage 2: Prompt Critique and Improvement (Intermediate)

Give students weak prompts and have them improve:

```
Weak Prompt:
  "Write code for a calculator"

Student Task:
  Rewrite this prompt to be more effective. Consider:
  - What language?
  - What operations?
  - Console or GUI?
  - Error handling requirements?
  - Input/output format?

Improved Prompt Example:
  "Write a Python command-line calculator that supports +, -, *, /.
   It should prompt for two numbers and an operator, perform the calculation,
   and handle division by zero with an error message. Display result to 2 decimal places."
```

**Assessment**: Compare improved prompts and AI outputs. What improvements had the biggest impact?

---

### Stage 3: Independent Prompt Crafting (Advanced)

Students design prompts from scratch for complex scenarios:

```
Scenario:
  "You're building a todo list application. You need a data structure and functions
   to add, remove, complete, and list todos. Write prompts to get AI help with this."

Student Task:
  1. Write prompts for each function
  2. Request the prompts in a logical order (data structure first, then operations)
  3. Include test cases in your prompts
  4. Ask AI to identify potential edge cases you missed
```

**Reflection**: What made your prompts effective? What would you do differently next time?

---

## Common Prompt Anti-Patterns (What to Avoid)

### Anti-Pattern 1: "Just Do It" Prompts ❌
```
Bad: "Write an app"
Bad: "Make a website"
Bad: "Create a game"
```

**Why Bad**: Too vague. AI can't infer requirements.

**Fix**: Break down into specific components with clear requirements.

---

### Anti-Pattern 2: Assuming AI Knows Your Context ❌
```
Bad: "Fix this code" [pastes code]
Bad: "Why doesn't this work?" [no context on what 'work' means]
```

**Why Bad**: AI doesn't know your goals, environment, or error messages.

**Fix**: Always provide context: what you're trying to do, what happens instead, error messages, environment details.

---

### Anti-Pattern 3: Overloading Single Prompt ❌
```
Bad: "Write a Python web app with user authentication, database integration,
      API endpoints for CRUD operations, frontend in React, deployment scripts,
      unit tests, and documentation."
```

**Why Bad**: Too many requirements at once. Overwhelming and likely to produce incomplete results.

**Fix**: Break into multiple prompts. Build incrementally.

---

### Anti-Pattern 4: Passive Acceptance ❌
```
Student: "Write a sorting function"
AI: [provides code]
Student: [copies code without reading or testing]
```

**Why Bad**: No learning occurs. Code may be wrong or inappropriate.

**Fix**: Always read, understand, test, and verify AI code before using.

---

## Assessment Strategies for Prompt Engineering

### Formative Assessment: Prompt Journals

Have students keep a journal of prompts they use:
- **Prompt**: What they asked
- **Result Quality**: 1-5 scale
- **Refinement**: How they improved it
- **Reflection**: What made it work/not work

**Review Weekly**: Identify patterns in effective vs. ineffective prompts.

---

### Summative Assessment: Prompt Challenge

Give students a complex coding task. They must:
1. Write a series of prompts to complete the task
2. Document their iteration process
3. Submit final working code + prompt log
4. Reflect on what prompts were most/least effective

**Grading Criteria**:
- Clarity and specificity of prompts
- Effective iteration and refinement
- Critical evaluation of AI outputs
- Quality of final code (correctness, style)

---

### Peer Review: Prompt Effectiveness

Students exchange prompts and evaluate each other's:
- Would this prompt produce useful output?
- What information is missing?
- How could it be improved?

**Benefit**: Seeing others' prompts expands students' repertoire of strategies.

---

## Ethical Considerations in Teaching Prompt Engineering

### Transparency

Teach students to:
- Acknowledge when AI generated code
- Understand licensing of AI-generated content
- Know when AI assistance is/isn't appropriate (exams, job applications)

---

### Critical Thinking

Emphasize:
- AI can be confidently wrong
- Always verify outputs (test, review, validate)
- AI reflects biases in training data
- Don't outsource understanding to AI

---

### Learning Balance

Help students recognize:
- Use AI to speed up, not skip, learning
- Struggle is part of learning (don't reach for AI immediately)
- AI is best for exploration, not memorization substitutes

---

## Practical Exercises for Prompt Engineering

### Exercise 1: Prompt Evolution
Give students a weak prompt. Have them evolve it through 5 iterations, documenting what they add each time.

---

### Exercise 2: Context Scavenger Hunt
Provide a coding problem. Students identify all necessary context to include in a prompt (language, version, constraints, format, edge cases).

---

### Exercise 3: Format Specification Competition
Who can write the prompt that produces the most useful output (code + tests + explanation + examples)?

---

### Exercise 4: Debugging Dialogue
Students practice multi-turn prompt dialogues to debug a complex problem, refining understanding with each prompt.

---

### Exercise 5: Constraint Experimentation
Same problem, different constraints. Compare how constraints change AI behavior and output quality.

---

## Summary: Key Principles for Teaching Prompt Engineering

1. **Teach it explicitly**: Don't assume students will figure it out
2. **Model good prompts**: Show examples of effective vs. ineffective prompts
3. **Practice iteration**: First prompts are rarely perfect
4. **Emphasize verification**: AI outputs must be tested and understood
5. **Balance assistance with learning**: AI accelerates, doesn't replace, understanding
6. **Assess prompt quality**: Not just code quality
7. **Encourage experimentation**: Try different approaches, see what works
8. **Teach context awareness**: AI performs better with rich context
9. **Foster critical evaluation**: Always question AI outputs
10. **Integrate with curriculum**: Prompt engineering enhances all programming tasks

---

**Key Insight**: Prompt engineering is not about tricking AI into giving answers. It's about effective communication, problem specification, and critical evaluation - all valuable software engineering skills.
