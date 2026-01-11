# Intent Interpretation Quick Reference

A practical guide for recognizing common request patterns and their underlying intents.

## High-Confidence Interpretation Patterns

These patterns typically have clear intent and can be interpreted with >80% confidence:

| User Says | Likely Intent | Proceed With |
|-----------|--------------|--------------|
| "Explain [concept] like I'm 5" | Simple, accessible explanation | Analogies, simple language, no jargon |
| "Debug this [code/error]" | Fix specific problem | Technical solution with explanation |
| "Summarize in [X] words" | Concise extraction of key points | Structured summary at specified length |
| "Compare [A] vs [B]" | Understand differences and tradeoffs | Balanced comparison with criteria |
| "Generate [number] examples of [X]" | Concrete instances | Diverse, realistic examples |
| "Rewrite this to be more [adjective]" | Improve specific quality | Targeted refinement maintaining core content |

## Ambiguous Patterns Requiring Clarification

These patterns have multiple likely interpretations and benefit from clarification:

### "Help me with [X]"

**Possible intents**:
1. Do X for me (wants output)
2. Teach me how to do X (wants understanding)
3. Review my attempt at X (wants feedback)
4. Troubleshoot my failing attempt at X (wants debugging)
5. Brainstorm approaches to X (wants options)

**Clarification strategy**:
- If they've shared work already → Likely wants review/troubleshooting
- If no work shared → Ask: "Would you like me to [do this] for you, or walk you through how to do it yourself?"

### "Is [X] good?"

**Possible intents**:
1. Validate my positive opinion (wants confirmation)
2. Should I choose X over alternatives (wants decision help)
3. What are X's tradeoffs (wants balanced analysis)
4. Is X technically correct/accurate (wants accuracy check)
5. Is X appropriate for my situation (wants suitability assessment)

**Clarification strategy**:
- Check context: Is there a decision to make? An alternative mentioned?
- Ask: "Are you trying to decide between options, or wanting to understand X's strengths and weaknesses?"

### "Make [X] better"

**Possible intents**:
1. Fix specific problems (needs diagnosis of issues)
2. Optimize for specific metric (needs target defined)
3. Complete rewrite (wants fresh approach)
4. Polish for presentation (needs refinement only)
5. Adapt for different audience (needs context)

**Clarification strategy**:
- Ask: "What aspects would you like improved?" or "What does 'better' mean in this context?"

### "Write [something]"

**Possible intents**:
1. Generate finished output ready to use (wants complete product)
2. Create draft for refinement (wants starting point)
3. Provide multiple options (wants variety)
4. Generate template to fill in (wants structure)
5. Show example of style/format (wants model)

**Clarification strategy**:
- Check if there's context about purpose/audience
- Ask: "Is this for [immediate use] or as a [draft/starting point]?"

### "Analyze [X]"

**Possible intents**:
1. Find specific information (needs targeted extraction)
2. Make a decision (needs actionable insights)
3. Understand deeply (needs educational explanation)
4. Validate existing opinion (needs objective assessment)
5. Find problems (needs critical analysis)
6. Identify patterns (needs pattern recognition)

**Clarification strategy**:
- Ask: "What are you trying to learn or decide from this analysis?"

## Domain-Specific Patterns

### Coding Requests

**"Write code to [do X]"**

High-confidence scenarios:
- With specs, language, constraints → Production code
- "Show me how to" phrasing → Educational code with comments
- "Quick script to" → Simple, functional solution

Ambiguous scenarios:
- Minimal context → Clarify: learning vs. production, language preference, constraints

**"Fix this code"**

High-confidence: Code provided, specific error → Debug and fix
Ambiguous: No error message → Ask what's not working

### Writing Requests

**"Write an essay about [X]"**

Ambiguous scenarios:
- Academic context? → Clarify: level, citation style, audience
- Blog post? → Clarify: tone, length, target audience
- Personal? → Clarify: purpose

**"Improve this writing"**

High-confidence: "Grammar" or "clarity" specified → Focused improvement
Ambiguous: No specific aspect → Ask what kind of improvement (style, clarity, engagement, etc.)

### Decision Requests

**"Should I [X] or [Y]?"**

High-confidence: Clear criteria or context provided → Analyze tradeoffs
Ambiguous: No context → Ask: What are you optimizing for? What constraints matter?

**"What's the best [X]?"**

Always ambiguous:
- "Best" for whom and for what purpose?
- What criteria define "best"?
- What constraints exist?

Clarify: Use case, priorities, constraints

## Expertise Level Indicators

### Signals of High Expertise
- Uses domain-specific terminology correctly
- Asks specific, narrow questions
- References specific tools/approaches/frameworks
- Provides detailed context

**Interpretation**: Can assume deeper knowledge, use technical language, focus on nuance

### Signals of Beginner Level
- Uses general or imprecise terminology
- Asks broad, open-ended questions
- Uncertain about options or approaches
- Minimal technical context

**Interpretation**: Need more background, simpler explanations, explicit step-by-step guidance

### Signals of Intermediate Level
- Mix of technical and general terms
- Knows concepts but uncertain about application
- Has tried things but stuck on specific aspect
- Some context provided but incomplete

**Interpretation**: Can build on existing knowledge, needs targeted help with gaps

## Temporal Signals

### Urgency Indicators
- "Quick," "fast," "briefly," "ASAP"
- Time constraints mentioned ("I have a meeting in an hour")
- Multiple exclamation points

**Interpretation**: Prioritize speed and directness over comprehensiveness

### Thoroughness Indicators
- "Comprehensive," "detailed," "in-depth," "thorough"
- "I want to really understand"
- Willing to engage in back-and-forth

**Interpretation**: Prioritize completeness and depth over brevity

### No Temporal Signal
- Neither urgency nor thoroughness specified

**Interpretation**: Match complexity to task—simple tasks get concise responses, complex tasks get thorough treatment

## Context Clues

### Purpose Indicators
- "For a presentation" → Polish, professional quality
- "For learning" → Educational, explanatory approach
- "For a project" → Functional, complete solution
- "Just curious" → Concise, interesting answer

### Audience Indicators
- "For my team" → Consider team's expertise level
- "For my boss" → Professional, clear, well-justified
- "For beginners" → Accessible, no jargon
- "For experts" → Can use technical language

### Constraint Indicators
- Budget mentions → Cost-consciousness
- Technology mentions → Compatibility requirements
- Timeframe mentions → Feasibility constraints
- Platform mentions → Environment constraints

## Response Strategy Matrix

| Confidence Level | Ambiguity Type | Strategy |
|-----------------|----------------|----------|
| High (>80%) | None | Proceed with interpretation |
| High (>80%) | Minor details | Proceed, note assumptions |
| Moderate (50-80%) | Significant | Proceed, explicitly state interpretation |
| Low (<50%) | Critical info missing | Clarify before proceeding |
| Low (<50%) | Multiple equally likely intents | Present options or ask directly |

## Red Flags Requiring Clarification

Always clarify when you notice:
- Contradictory requirements ("brief but comprehensive")
- Vague success criteria ("make it better")
- Missing critical context (no audience, purpose, or constraints specified)
- Technical request without expertise level indicators
- High-stakes decision without criteria
- Creative request without tone, style, or purpose
- "Quick" request for inherently complex task

## Quick Decision Framework

1. **Is the request clear and unambiguous?** → Proceed
2. **Is there one dominant interpretation (>80% confidence)?** → Proceed with brief assumption note
3. **Are there 2-3 equally likely interpretations?** → Present options or ask one targeted question
4. **Is critical information missing?** → Ask 1-3 strategic questions
5. **Is the request impossible as stated?** → Clarify constraints or suggest alternatives

## Common Mistakes to Avoid

**Over-clarifying obvious requests**: "What color is the sky?" doesn't need intent analysis

**Under-clarifying ambiguous ones**: "Help me with my project" needs more context

**Assuming technical level**: Don't guess expertise—look for signals or ask

**Ignoring context clues**: Pay attention to what's implied by phrasing and situation

**Asking too many questions**: 1-3 strategic questions max per turn

**Being mechanical**: Keep clarification natural and conversational

Remember: The goal is providing value efficiently. Clarify when necessary, but don't over-analyze straightforward requests.
