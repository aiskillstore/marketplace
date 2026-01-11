# Common Prompt Anti-Patterns

A reference guide for identifying and fixing common prompt engineering mistakes.

## Anti-Pattern Categories

### 1. Clarity Issues

**Vague Action Verbs**
- Bad: "Deal with the data"
- Good: "Analyze the data to identify outliers and calculate summary statistics"

**Ambiguous Scope**
- Bad: "Review this document"
- Good: "Review this document for grammatical errors and clarity issues. Do not assess content accuracy."

**Undefined Terms**
- Bad: "Use the standard format"
- Good: "Format as JSON with fields: {name: string, id: number, active: boolean}"

**Missing Success Criteria**
- Bad: "Make this better"
- Good: "Improve this text for clarity by: reducing sentence length, removing jargon, adding transitions between paragraphs"

### 2. Structural Problems

**Information Overload**
- Bad: 2000-word monolithic prompt with no structure
- Good: Hierarchical organization with clear sections and headers

**Critical Info Buried**
- Bad: Key requirement mentioned casually in paragraph 3
- Good: Critical requirements stated explicitly at start and reiterated at end

**Poor Delimiter Usage**
- Bad: Instructions and data mixed together without separation
- Good: Clear delimiters (```, XML tags, etc.) separating different content types

**Lack of Hierarchy**
- Bad: Flat list of 50 requirements
- Good: Grouped requirements with clear priorities and categories

### 3. Context Issues

**Assumed Knowledge**
- Bad: "Use the company guidelines" (without providing them)
- Good: "Use these company guidelines: [provides actual guidelines]"

**Missing Background**
- Bad: "Analyze this code for issues"
- Good: "Analyze this Python code for security issues. Context: This handles user authentication in a web app."

**Undefined Audience**
- Bad: "Explain quantum computing"
- Good: "Explain quantum computing to a high school student with basic physics knowledge"

**Unstated Constraints**
- Bad: Expecting JSON output without saying so
- Good: "Output must be valid JSON matching this schema: {...}"

### 4. Logic and Consistency Problems

**Contradictory Requirements**
- Bad: "Be comprehensive but brief"
- Good: "Provide a 200-word summary followed by detailed sections"

**Impossible Specifications**
- Bad: "List all possible causes" (in an open-ended domain)
- Good: "List the 5 most common causes based on frequency in literature"

**Circular Definitions**
- Bad: "Make it more optimized by optimizing it better"
- Good: "Reduce time complexity from O(n²) to O(n log n) by using a more efficient sorting algorithm"

**Conflicting Priorities**
- Bad: "Minimize cost, maximize features, ensure highest quality, deliver immediately"
- Good: "Prioritize quality and core features. Secondary priority is cost optimization. Timeline is flexible."

### 5. Edge Case Neglect

**No Empty/Null Handling**
- Bad: "Extract all emails from the text"
- Good: "Extract all emails. Return empty array if none found. Skip invalid format emails."

**Missing Error Cases**
- Bad: "Parse the JSON data"
- Good: "Parse JSON data. If invalid, return error message specifying the issue."

**Unhandled Variations**
- Bad: "Format dates consistently"
- Good: "Convert all dates to ISO 8601 format (YYYY-MM-DD). Handle formats: MM/DD/YYYY, DD-MM-YYYY, 'Month DD, YYYY'."

**Boundary Conditions Ignored**
- Bad: "Summarize the text"
- Good: "Summarize the text in 100-200 words. If text is <50 words, return it unchanged. If >5000 words, summarize in 500 words."

### 6. Bias and Leading Language

**Loaded Questions**
- Bad: "Explain why this obviously flawed approach fails"
- Good: "Analyze this approach's strengths and weaknesses"

**Presumed Conclusions**
- Bad: "Describe how much better X is than Y"
- Good: "Compare X and Y objectively across these criteria: [...]"

**Emotional Language**
- Bad: "Urgently and immediately analyze..."
- Good: "Analyze this data systematically..."

**False Dichotomies**
- Bad: "Is this good or bad?"
- Good: "Evaluate this approach, noting tradeoffs and contexts where it excels or struggles"

### 7. Output Specification Problems

**Format Ambiguity**
- Bad: "Organize the results"
- Good: "Organize results as a numbered list with category headers"

**Length Vagueness**
- Bad: "Keep it short"
- Good: "Limit response to 250-300 words"

**Unstated Ordering**
- Bad: "List the factors"
- Good: "List factors in order of importance, from most to least significant"

**Missing Components**
- Bad: "Write a report"
- Good: "Write a report including: executive summary, methodology, findings, recommendations, and appendix"

### 8. Technique Misapplication

**Inappropriate Complexity**
- Bad: Using complex chain-of-thought for trivial tasks
- Good: Match technique sophistication to task complexity

**Missing Appropriate Techniques**
- Bad: Analytical task without self-consistency checks
- Good: "Analyze X from multiple perspectives and validate conclusions against evidence"

**Over-Engineering Simple Tasks**
- Bad: 10-stage plan-and-solve for basic arithmetic
- Good: Simple direct instruction for simple tasks

**Wrong Pattern for Task Type**
- Bad: Creative writing with rigid step-by-step constraints
- Good: Creative writing with guidelines and examples, allowing flexibility

## Diagnostic Questions

When analyzing a prompt that's not working well, ask:

**About Clarity:**
- Can I understand exactly what's being requested?
- Are success criteria explicit?
- Would different people interpret this the same way?

**About Structure:**
- Is the most important information prominent?
- Does the organization guide me naturally through the task?
- Are different types of content clearly separated?

**About Context:**
- Do I have all the information needed to complete the task?
- Are assumptions made explicit?
- Is the audience and purpose clear?

**About Logic:**
- Are all requirements compatible with each other?
- Are specifications achievable?
- Is there internal consistency?

**About Completeness:**
- What happens in edge cases?
- Are error conditions handled?
- Are all likely variations addressed?

**About Bias:**
- Does the prompt prejudge conclusions?
- Is language neutral and objective?
- Are multiple perspectives invited?

**About Output:**
- Is the desired format explicit?
- Are length expectations clear?
- Are required components specified?

**About Techniques:**
- Are evidence-based patterns applied appropriately?
- Is technique sophistication matched to task complexity?
- Are the right prompting patterns used for the task type?

## Quick Fixes

Common problems and their solutions:

| Problem | Quick Fix |
|---------|-----------|
| Too vague | Add specific action verbs and concrete objectives |
| Too complex | Break into smaller prompts or use hierarchical structure |
| Inconsistent output | Add explicit format specification and examples |
| Missing edge cases | List common variations and specify handling |
| Low reliability | Add self-consistency checks and validation steps |
| Wrong results | Provide few-shot examples showing desired patterns |
| Contradictions | Prioritize requirements explicitly with "primary/secondary" |
| Context missing | State assumptions explicitly and provide background |

## Prevention Strategies

To avoid anti-patterns from the start:

1. **Start with concrete examples** of desired inputs and outputs
2. **Test edge cases early** rather than as an afterthought
3. **Be explicit rather than implicit** about requirements
4. **Structure hierarchically** for any prompt over ~200 words
5. **Validate against the framework** before deploying
6. **Iterate based on actual failures** not theoretical perfection
7. **Document what works** for future reference

Remember: The goal isn't perfect prompts but prompts that work reliably for your specific use case. Practical effectiveness beats theoretical optimization.
