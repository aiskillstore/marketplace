# Knowledge Sharing and Reference Protocol

## Purpose
This protocol defines how to detect knowledge gaps, request information from users, and document external references during development. Use this when you need information beyond your training data or codebase exploration to implement correctly without hallucination.

## Application Philosophy
These guidelines are designed to be applied thoughtfully, not rigidly:

- **Strive to follow** - Aim to apply these principles consistently, but use judgment when exceptions are warranted
- **Apply incrementally** - Build good habits gradually; it's acceptable to apply these imperfectly at first and improve over time
- **Context matters** - Adapt guidelines to project size, team structure, and specific requirements
- **Progress over perfection** - Moving in the right direction is better than perfect adherence that delays delivery
- **Question and clarify** - When unsure, err on the side of asking or documenting your reasoning

## Decision Point 1: Knowledge Gap Detection

### Trigger Conditions (ALL must be true to proceed with knowledge request)
- [ ] Task requires specific technical information not in your training data
- [ ] Information is NOT discoverable through codebase exploration (Grep, Glob, Read)
- [ ] Information is NOT reliably available through web search
- [ ] Proceeding without this information will result in incorrect or speculative implementation

### Knowledge Gaps That Justify This Protocol
- API specifications for third-party services not in training data
- Custom internal frameworks or libraries unique to this project
- Version-specific behavior changes in recently updated dependencies
- Domain-specific business rules not inferable from code
- Organization-specific conventions or architectural decisions

### Action: Initiate Knowledge Request Protocol
If ALL trigger conditions are met:
1. Create directory: `references/[topic-name]/` (use kebab-case)
2. Create file: `references/[topic-name]/REFERENCE.md`
3. Proceed to Decision Point 3 (User Information Request)

---

## Decision Point 2: Web Search Documentation

### Trigger Conditions (ANY = document search results)
- [ ] Performed web search for technical information related to current task
- [ ] Found information that will be referenced repeatedly during implementation
- [ ] Information is version-specific or subject to future changes
- [ ] Search results provide critical context not in training data

### Action: Document Search Results
1. Create file: `references/[topic-name]/SEARCH.md`
2. Use this template:

```markdown
# [Search Query]
[Why this search query was used and what results were sought]

## Search Date
[YYYY-MM-DD]

## Result
[Full search results - paste relevant content here]

## Key Findings
- [Specific finding with URL]
- [Specific finding with URL]
- [Specific finding with URL]
```

3. Reference in `REFERENCE.md`: "@ references/[topic]/SEARCH.md for search results"

---

## Decision Point 3: User Information Request

### Trigger Conditions (ANY = request user input)
- [ ] REFERENCE.md created but lacks specific information to proceed
- [ ] Web search performed but results are ambiguous or conflicting
- [ ] Multiple valid interpretations exist that code exploration doesn't resolve
- [ ] Domain-specific business logic is required
- [ ] User's intent cannot be determined from available context

### Action Protocol
1. **Create REFERENCE.md with this template:**

```markdown
# [Reference Title - Topic Name]

## Purpose
[Explain why this reference is needed for the current task]
[Describe how this information will be used in implementation]

## Required References
[List specific information needed:]
- [API documentation links]
- [Framework specification documents]
- [Business rule definitions]
- [Code examples or patterns]

## Current Understanding
[What you already know from codebase/search]

## Information Gaps
[Specific questions that need answers]
```

2. **Explicitly communicate to user:**
   - "I need additional information to proceed correctly without speculation"
   - Reference the REFERENCE.md file you created
   - Ask SPECIFIC questions (avoid "please provide more details")

3. **Offer input methods:**
   - "You can provide this information as:"
     - "A. Explanation in your response (I'll create a markdown file)"
     - "B. Upload documentation files to `references/[topic]/` directory"
     - "C. Provide URLs to official documentation"

4. **Wait for user response** - DO NOT proceed with speculative implementation

### User Response Handling

**If user provides explanation in text:**
- Create `references/[topic]/[descriptive-name].md` with their explanation
- Update `REFERENCE.md` to reference the new file
- Confirm understanding: "Based on your explanation, I understand..."

**If user uploads files:**
- Acknowledge: "I see you've added files to references/[topic]/"
- Read and confirm understanding
- Update `REFERENCE.md` to list uploaded files

**If user provides URLs:**
- Use WebFetch to retrieve content
- Document findings in `SEARCH.md` or new markdown file
- Update `REFERENCE.md` with URL references

---

## Decision Point 4: When NOT to Request Knowledge

### Skip This Protocol When (ANY = do not create reference)
- [ ] Information is discoverable through codebase exploration
- [ ] Standard programming patterns apply (no special domain knowledge needed)
- [ ] Answer is in your training data and hasn't fundamentally changed
- [ ] User already provided sufficient context in their request
- [ ] Question can be answered through web search with high confidence

### Counter-Examples (DO NOT create references for these)
- How to implement a REST API (general knowledge)
- How to use standard library functions (training data)
- How to loop through an array (basic programming)
- How to use well-documented public frameworks (web search sufficient)
- Code patterns already visible in the codebase (use codebase exploration)

### Action
Proceed with implementation using existing knowledge and codebase patterns.

---

## Naming and Organization

### Directory Naming Rules
- Use kebab-case: `oauth-integration`, `payment-processing`, `custom-framework`
- Be specific: `stripe-api-v2023` NOT `payments`
- One concern per directory
- Maximum depth: `references/[topic]/` (no subdirectories)

### File Structure
Each reference directory may contain:
- `REFERENCE.md` (required) - Index of what information is needed/provided
- `SEARCH.md` (optional) - Web search results and findings
- `[descriptive-name].md` (optional) - User-provided explanations
- Uploaded files from user (PDFs, code examples, specs)

---

## Process Workflow

### Complete Knowledge Request Flow
1. **Detect knowledge gap** (Decision Point 1)
   - Verify ALL trigger conditions met
   - Confirm information not in codebase or training data

2. **Attempt web search** (Decision Point 2 - optional)
   - Search for official documentation
   - If found and sufficient: Document in SEARCH.md, proceed
   - If not found or insufficient: Continue to step 3

3. **Request user information** (Decision Point 3)
   - Create REFERENCE.md with template
   - Clearly state what information is needed and why
   - Offer multiple input methods
   - WAIT for user response

4. **Process user information**
   - Create markdown files from text explanations
   - Read uploaded files
   - Fetch and document URLs
   - Update REFERENCE.md with references

5. **Validate understanding**
   - Confirm with user: "Based on [source], I understand..."
   - Ask clarifying questions if ambiguity remains
   - Repeat process if still insufficient

6. **Proceed with implementation**
   - Once knowledge gap is filled, continue with task
   - Reference created documents during implementation

---

## Maintenance

### Update Triggers
- [ ] Implementation reveals REFERENCE.md assumptions were incorrect
- [ ] User provides additional clarification or corrections
- [ ] External API or library version changes
- [ ] Documentation links become outdated

### Action
- Update relevant markdown files in `references/[topic]/`
- Add "Last Updated: YYYY-MM-DD" to modified files
- Note what changed and why

### Cleanup Triggers
- [ ] Feature implementation complete and validated
- [ ] Information has been incorporated into permanent codebase documentation
- [ ] Reference no longer consulted for 3+ development sessions
- [ ] Topic is no longer relevant to project

### Action
- Archive or delete `references/[topic]/` directory
- Update any cross-references in other documents
