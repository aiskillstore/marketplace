# Code Teaching Patterns

## Core Teaching Principles

### 1. Progressive Complexity
Start simple, add complexity incrementally. Never overwhelm with advanced concepts before foundations are solid.

**Pattern:**
- Show minimal working example
- Explain what it does and why
- Add one feature at a time
- Explain each addition thoroughly

### 2. Concrete Before Abstract
Always start with specific examples before generalizing to concepts.

**Example:**
```python
# ❌ Don't start with: "A function is a reusable block of code..."
# ✅ Do start with:
def greet():
    print("Hello!")

greet()  # This prints: Hello!
# Now explain: "This is a function - it lets us reuse this code"
```

### 3. The Why Before The How
Explain the problem before the solution. Learners retain information better when they understand the motivation.

## Teaching Pattern Templates

### Pattern: Building Block Approach
For complex features, break into smallest functional pieces.

```
1. Build minimal version (one feature)
2. Explain every line
3. Run it, show output
4. Add next feature
5. Explain only the new lines
6. Run again, compare output
7. Repeat until complete
```

### Pattern: Comparison Learning
When teaching new concepts, relate to familiar ones.

**Template:**
```
"Remember when we used [familiar concept]? [New concept] is similar, but..."
- Similarity 1: ...
- Key difference: ...
- Why we need it: ...
```

### Pattern: Error-Driven Learning
Intentionally show common mistakes, then fix them.

**Process:**
1. Write code with a deliberate beginner mistake
2. Run it, show the error
3. Explain why it happens
4. Fix it together
5. Explain the correct pattern

### Pattern: Visual Code Mapping
For complex logic, map code flow visually.

```python
# Step 1: Get user input
name = input("Name: ")  # ← Program waits here for typing

# Step 2: Process it
greeting = f"Hello, {name}!"  # ← Creates new string with name inside

# Step 3: Show result
print(greeting)  # ← Displays on screen
```

### Pattern: State Tracking
For variables and data changes, show state at each step.

```python
# Start: x = 0
x = 0

# After line 1: x = 5
x = x + 5

# After line 2: x = 10
x = x + 5

# Result: x = 10
print(x)
```

### Pattern: Concept Scaffolding
Build complex understanding from simple components.

**Example for Functions:**
```
Phase 1: Function that just prints (no params, no return)
Phase 2: Function with parameters (input)
Phase 3: Function with return value (output)
Phase 4: Function with both (transformation)
```

## Learning Style Adaptations

### For Visual Learners
- Use ASCII diagrams
- Show data structure representations
- Include before/after comparisons
- Use tree structures for logic flow

### For Kinesthetic Learners
- Encourage immediate experimentation
- Suggest modifications to try
- Include "Try this" challenges
- Emphasize hands-on building

### For Reading/Writing Learners
- Provide detailed comments
- Write comprehensive explanations
- Include summary sections
- Offer note-taking prompts

### For Verbal Learners
- Use conversational tone
- Explain as if teaching in person
- Include analogies and metaphors
- Ask reflective questions

## Pacing Guidelines

### Signs to Slow Down
- User asks "wait, what does X mean?"
- Confusion about previous concepts
- Questions about basic syntax
- Requests for clarification

**Response:** Review fundamentals, use simpler examples, break into smaller steps.

### Signs to Speed Up
- User grasps concepts quickly
- Asks about more advanced features
- Implements extensions independently
- Questions are about optimization

**Response:** Introduce intermediate concepts, show best practices, discuss design patterns.

## Code Explanation Framework

For every code block, include:

1. **Purpose**: What this code accomplishes
2. **Prerequisites**: What they need to know first
3. **Line-by-line**: Explain each significant line
4. **Output**: What happens when it runs
5. **Common mistakes**: What could go wrong
6. **Next steps**: What to learn/build next

## Interactive Teaching Techniques

### Socratic Questioning
Instead of giving answers immediately, guide with questions:
- "What do you think this line does?"
- "What would happen if we changed X to Y?"
- "How would you solve [problem]?"

### Think-Aloud Protocol
Model problem-solving thought process:
- "First, I think about what data we need..."
- "I'm choosing a loop here because..."
- "Let me break this down into steps..."

### Checkpoint Validation
Periodically verify understanding:
- "Does this make sense so far?"
- "Try explaining what this does in your own words"
- "What questions do you have about this?"
