# Anthropic Prompt Engineering Best Practices for Agent Instructions

*Research compiled: December 16, 2025*

This document synthesizes Anthropic's official guidance on prompt engineering, with specific focus on creating effective agent system prompts and instructions.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Prompt Structure and Organization](#prompt-structure-and-organization)
3. [Role Definition and Persona Setting](#role-definition-and-persona-setting)
4. [Using Examples (Multishot Prompting)](#using-examples-multishot-prompting)
5. [Chain of Thought and Reasoning](#chain-of-thought-and-reasoning)
6. [Output Format Control](#output-format-control)
7. [XML Tags for Structure](#xml-tags-for-structure)
8. [Context Engineering for Agents](#context-engineering-for-agents)
9. [Tool Design for Agents](#tool-design-for-agents)
10. [Common Pitfalls to Avoid](#common-pitfalls-to-avoid)
11. [Prompt Development Process](#prompt-development-process)
12. [Quick Reference](#quick-reference)

---

## Core Principles

### The "Right Altitude" Principle

System prompts should be extremely clear and use simple, direct language that presents ideas at the **right altitude** for the agent. The right altitude is the Goldilocks zone between two common failure modes:

- **Too Low (Over-Constrained)**: Engineers hardcode complex, brittle logic in their prompts (e.g., "if the user asks about pricing, say X"). This creates fragility and increases maintenance complexity over time.
- **Too High (Too Vague)**: Overly general prompts that provide vague, high-level guidance (e.g., "be helpful") fail to give the LLM concrete signals for desired outputs.

**The Sweet Spot**: Clear guidance that still lets the AI think. Provide specific enough direction to guide behavior effectively, yet flexible enough to provide strong heuristics.

### Minimalism with Completeness

You should be striving for the **minimal set of information that fully outlines your expected behavior**. Note that minimal does not necessarily mean short; you still need to give the agent sufficient information up front.

**Signal-to-Noise Ratio**: Good context engineering means "finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."

### Clarity Over Complexity

**Be Clear, Direct, and Detailed**:
- Don't assume the AI reads minds: Be specific about what you want
- Leaving things ambiguous gives the AI room to misinterpret
- Small details matter! Scrub your prompts for typos and grammatical errors
- Claude is sensitive to patterns—it's more likely to make mistakes when you make mistakes

**Language Matters**:
- Prompts written in your native or strongest language tend to work best
- Avoid using languages you aren't very confident in, as errors or unnatural phrasing can throw off the model

---

## Prompt Structure and Organization

### Recommended Component Order

In complex prompts, use this order:

1. **Task Context**: Assign the LLM a role or persona and broadly define the task
2. **Tone Context**: Set a tone for the conversation
3. **Background Data/Documents**: Provide all necessary information for the task
4. **Detailed Task Description and Rules**: Provide detailed rules about the LLM's interaction

### Use Clear Delineation

Organize prompts into distinct sections using:
- XML tags (e.g., `<instructions>`, `<context>`, `<examples>`)
- Markdown headers (e.g., `## Tool Guidance`, `## Output Description`)

### Instructions Placement for Long Documents

When working with long documents, **place instructions at the end of the prompt**, after the long document. This increases the likelihood that the model remembers what it's supposed to do.

### System vs User Messages

Claude follows instructions in the **user messages** (the actual user prompts) better than those in the system message.

**Best Practice**:
- Use the system message mainly for high-level scene setting
- Put most of your instructions in the human prompts

---

## Role Definition and Persona Setting

### Purpose of Roles

**Role prompting** is a technique where you assign a specific persona or role to Claude using the system parameter in the Messages API. By casting Claude in the role of a subject matter expert (e.g., "General Counsel for legal analysis" or "Chief Financial Officer for financial planning"), developers can tap into the model's latent knowledge and skills in those domains.

### Benefits

- **Tone and Vocabulary**: Setting a persona helps Claude set the proper tone and vocabulary for responses
- **Focus**: Role-based framing helps Claude focus on relevant expertise and minimizes off-topic digressions
- **Consistency**: Improved role-playing and character consistency across interactions

### Best Practices

**Do**:
- Assign Claude a precise persona to guide tone and depth
- Use roles that align with the specific expertise needed
- Example: "You are an experienced software architect specializing in distributed systems"

**Don't**:
- Over-constrain the role: "You are a helpful assistant" is often better than "You are a world-renowned expert who only speaks in technical jargon and never makes mistakes"
- Overly specific roles can limit the AI's helpfulness

---

## Using Examples (Multishot Prompting)

### Power of Examples

**"Examples are your secret weapon"** for getting Claude to generate exactly what you need. This technique, known as few-shot or multishot prompting, is particularly effective for tasks that require structured outputs or adherence to specific formats.

### Why Examples Work

- **Reduce Misinterpretation**: Examples make instructions concrete
- **Enforce Uniformity**: Ensure consistent structure and style
- **Demonstrate Patterns**: Show exactly what you want, not just describe it
- **For an LLM, a few good examples are worth a thousand words of instruction**

### How Many Examples?

- **Include 3-5 diverse, relevant examples** to show Claude exactly what you want
- More examples generally equals better performance, especially for complex tasks
- For agents: Quality over quantity—curate a small, diverse set of canonical examples

### Example Structure

Use XML tags to delineate examples:

```xml
<examples>
  <example>
    <input>User question or request</input>
    <output>Desired response format</output>
  </example>
  <example>
    <input>Another user question</input>
    <output>Another desired response</output>
  </example>
</examples>
```

### Modern Considerations for Agents

**Important**: For frontier models and agents, prescriptive few-shot examples are becoming **less effective**. Modern models have CoT reasoning trained into them and know how to think through problems systematically.

**For Agents**: Instead of showing exact reasoning chains, tell the agent **how to use its thinking process**:
- "Use your thinking process to plan out your approach before taking action"
- "After getting tool results, reflect on whether the information is sufficient"

---

## Chain of Thought and Reasoning

### What is Chain of Thought (CoT)?

Chain of thought prompting encourages Claude to break down problems step-by-step, leading to more accurate and nuanced outputs.

### Benefits

- **Accuracy**: Stepping through problems reduces errors, especially in math, logic, analysis, or complex tasks
- **Coherence**: Structured thinking leads to more cohesive, well-organized responses
- **Debugging**: Seeing Claude's thought process helps you pinpoint where prompts may be unclear

### Implementation Techniques

#### Simple Approach
Add the phrase **"Think step by step"** to your prompt.

#### Structured Approach
Use XML tags to separate reasoning from the final answer:

```xml
<thinking>
[Claude's step-by-step reasoning goes here]
</thinking>

<answer>
[Final answer goes here]
</answer>
```

### For Agent Prompts

In evaluation agents' system prompts, Anthropic recommends instructing agents to output:
- **Reasoning blocks**: Before tool calls
- **Feedback blocks**: After receiving tool results
- **Response blocks**: Final structured output

**Why This Order Matters**: Instructing agents to output reasoning and feedback blocks before tool call and response blocks may increase LLMs' effective intelligence by triggering chain-of-thought (CoT) behaviors.

### Important Caveat

Recent Anthropic research shows that CoT traces may not always be "faithful"—they can sometimes omit or obscure critical influences, especially when the model is incentivized to behave strategically. While CoTs can surface useful reasoning steps, they should not be relied upon as the sole mechanism for AI interpretability or safety.

---

## Output Format Control

### Prefilling for Format Control

**Prefilling** allows you to specify the exact format you want Claude to use for its output by starting the Assistant's response yourself.

### Common Use Cases

1. **Skip Preambles**: Prefill with `{` to force Claude to directly output JSON without explanatory text
2. **Enforce Structure**: Start the response with the desired format structure
3. **Maintain Character**: Help Claude stay in character by beginning its response

### Example: JSON Output

Without prefill:
```
User: Return user data as JSON
Claude: Here's the user data in JSON format: {"name": "John", "age": 30}
```

With prefill (Assistant starts with `{`):
```
User: Return user data as JSON
Assistant: {
Claude: "name": "John", "age": 30}
```

This is cleaner, more concise, and easier for programs to parse.

### Structured Outputs (Beta Feature)

For guaranteed JSON schema compliance, use **Structured Outputs**:
- Available for Claude Sonnet 4.5, Opus 4.1, Opus 4.5, and Haiku 4.5
- Add header: `anthropic-beta: structured-outputs-2025-11-13`
- Provides guaranteed schema validation
- Two features: JSON outputs (`output_format`) and strict tool use (`strict: true`)

**Important**: Message prefilling is incompatible with JSON outputs when using structured outputs.

### When to Use Each

- **Structured Outputs**: When you need guaranteed schema compliance for downstream processing
- **Prompt Engineering/Prefilling**: When you need flexibility beyond strict JSON schemas or general output consistency

---

## XML Tags for Structure

### Why XML Tags?

Claude was trained with XML tags in the training data and has been fine-tuned to pay special attention to them. When your prompts involve multiple components like context, instructions, and examples, XML tags can be a game-changer.

### Benefits

- **Clarity**: Clearly separate different parts of your prompt and ensure well-structured prompts
- **Accuracy**: Reduce errors caused by Claude misinterpreting parts of your prompt
- **Flexibility**: Easily find, add, remove, or modify parts of your prompt without rewriting everything
- **Parseability**: Having Claude use XML tags in its output makes it easier to extract specific parts of its response

### Recommended Tags

While there are no canonical "best" XML tags, these are commonly used:

- `<instructions>`: Task instructions to Claude
- `<context>`: Background information
- `<example>` or `<examples>`: Sample inputs and outputs
- `<input>`: Input data within examples
- `<output>`: Expected output within examples
- `<thinking>`: Claude's reasoning process
- `<answer>`: Final answer
- `<human>` and `<assistant>`: For simulating conversations

### Best Practices

1. **Use Meaningful Names**: Tag names should make sense with the information they surround
2. **Be Consistent**: Use the same tag names throughout your prompts
3. **Reference Tags**: Refer to tag names when talking about content (e.g., "Using the contract in `<contract>` tags...")
4. **Nest Tags**: Use proper nesting for hierarchical content: `<outer><inner></inner></outer>`

### Power User Tip

Combine XML tags with other techniques:
- XML + Multishot prompting: `<examples>` containing multiple `<example>` blocks
- XML + Chain of thought: `<thinking>` and `<answer>` tags
- This creates super-structured, high-performance prompts

### Example Structure

```xml
<context>
You are analyzing customer support tickets for a SaaS product.
</context>

<instructions>
1. Classify the ticket sentiment (positive, neutral, negative)
2. Identify the primary issue category
3. Suggest an appropriate response tone
</instructions>

<examples>
  <example>
    <ticket>The app keeps crashing when I try to export data!</ticket>
    <analysis>
      <sentiment>negative</sentiment>
      <category>technical_issue</category>
      <tone>apologetic and solution-focused</tone>
    </analysis>
  </example>
</examples>
```

---

## Context Engineering for Agents

### Beyond Prompt Engineering

**Context engineering** is the natural progression of prompt engineering. As we move towards engineering more capable agents that operate over multiple turns of inference and longer time horizons, we need strategies for managing the entire context state:
- System instructions
- Tools
- Model Context Protocol (MCP)
- External data
- Message history

### The Curation Challenge

Context engineering is the art and science of curating what will go into the limited context window from the constantly evolving universe of possible information. In contrast to the discrete task of writing a prompt, **context engineering is iterative** and the curation phase happens each time we decide what to pass to the model.

### Key Principles for Agent Context

1. **High-Signal Tokens**: Focus on information that maximizes likelihood of desired outcomes
2. **Iterative Curation**: Context needs evolve with each agent turn
3. **Simplicity**: Maintain simplicity in your agent's design
4. **Transparency**: Explicitly show the agent's planning steps
5. **Efficient Tools**: Design tools that return token-efficient information

---

## Tool Design for Agents

### Tools as Context Gateways

Tools allow agents to operate with their environment and pull in new, additional context as they work. Because tools define the contract between agents and their information/action space, it's extremely important that tools promote efficiency.

### Principles for Effective Tools

1. **Token Efficiency**: Tools should return information that is token-efficient
2. **Encourage Efficient Behavior**: Tool design should guide agents toward efficient workflows
3. **Intentional and Clear**: Tools must be intentionally and clearly defined
4. **Judicious Context Use**: Use agent context judiciously
5. **Composable**: Tools can be combined together in diverse workflows
6. **Intuitive**: Enable agents to intuitively solve real-world tasks

### Agent-Computer Interface (ACI)

Carefully craft your agent-computer interface through:
- Thorough tool documentation
- Comprehensive testing
- Clear contracts between agent and environment

### Re-orienting Development Practices

To build effective tools for agents, we need to re-orient software development practices from **predictable, deterministic patterns** to **non-deterministic ones**. This represents a fundamental shift in how we design interfaces for AI systems.

---

## Common Pitfalls to Avoid

### 1. Over-Engineering Prompts

**Don't**: Make prompts longer and more complex thinking it's always better
**Do**: Find the minimal set of high-signal tokens that maximize desired outcomes

### 2. Ignoring the Basics

**Don't**: Jump to advanced techniques when your core prompt is unclear or vague
**Do**: Start with clear, direct instructions before adding complexity

### 3. Being Vague or Ambiguous

**Don't**: Assume the AI reads minds or has shared context
**Do**: Be explicit and specific about what you want

### 4. Using Every Technique at Once

**Don't**: Throw all techniques into one prompt
**Do**: Select techniques that address your specific challenge

### 5. Not Iterating

**Don't**: Expect the first prompt to work perfectly
**Do**: Test, refine, and iterate based on failures. Prompt engineering is about continuous iteration, not one-and-done

### 6. Making Typos and Grammatical Errors

**Don't**: Let typos slip through
**Do**: Scrub prompts carefully. Claude is sensitive to patterns—it's more likely to make mistakes when you make mistakes

### 7. Over-Constraining Roles

**Don't**: Create overly specific roles that limit helpfulness
**Do**: "You are a helpful assistant" is often better than "You are a world-renowned expert who only speaks in technical jargon"

### 8. Using LLMs for Tasks Better Done in Code

**Don't**: Rely on the LLM for formatting, validation, or evaluation logic that can be handled in code
**Do**: Handle deterministic steps outside the LLM. "If I don't have to make this long pilgrimage to the Oracle [Claude] to ask them, I shouldn't"

### 9. Not Testing Edge Cases

**Don't**: Focus only on the "happy path"
**Do**: Test with incomplete data, typographical errors, non-sequiturs. Real-world applications are messy

### 10. Poor Prompt Structure with Long Documents

**Don't**: Put instructions at the beginning before long documents
**Do**: Place instructions at the end, after the long document, so the model remembers what to do

### 11. Creating Brittle If-Else Logic

**Don't**: Hardcode complex, brittle logic in prompts (e.g., "if user asks X, respond Y")
**Do**: Provide clear heuristics that allow the model to reason

### 12. Not Thinking About Misinterpretation

**Don't**: Assume your instructions are unambiguous
**Do**: Think through how a model might misinterpret instructions. This self-awareness can save valuable time

---

## Prompt Development Process

### 1. Start Minimal

Begin by testing a **minimal prompt with the best model available** to see how it performs on your task. This establishes a baseline.

### 2. Identify Failure Modes

Run the prompt through various scenarios and identify where it fails:
- What does it misinterpret?
- Where does output quality degrade?
- What edge cases cause problems?

### 3. Add Targeted Improvements

Based on failure modes, add:
- **Clear instructions** to address misinterpretations
- **Examples** to demonstrate desired patterns
- **Constraints** to prevent unwanted behaviors
- **Structure** (XML tags) for complex prompts

### 4. Iterate and Test

- Test with diverse inputs
- Measure performance improvements
- Refine based on results
- Remove unnecessary complexity

### 5. Use Anthropic's Tools

- **Prompt Generator**: Automatically creates comprehensive prompts from concise task descriptions
- **Evaluate Tab**: Sandbox environment for testing and refining prompts
- **Prompt Improver**: Automated analysis and enhancement (excels at complex tasks requiring high accuracy)

### 6. Continuous Refinement

Prompt engineering isn't about writing a single perfect prompt and being done. It's about **continuous iteration and tweaking** through a "trial and error" approach.

---

## Quick Reference

### Prompt Engineering Techniques Hierarchy

**Basic**:
- Be clear, direct, and detailed
- Use examples (multishot prompting)
- Assign roles and personas

**Intermediate**:
- Let Claude think (chain of thought)
- Use XML tags for structure
- Prefill Claude's response

**Advanced**:
- Chain complex prompts together
- Long context optimization
- Context engineering for agents

### Essential Do's

1. Start minimal, then iterate
2. Be clear and specific
3. Use 3-5 diverse examples
4. Structure with XML tags
5. Enable chain of thought reasoning
6. Test edge cases thoroughly
7. Iterate based on failures
8. Proofread for errors
9. Place instructions after long documents
10. Design token-efficient tools for agents

### Essential Don'ts

1. Don't over-engineer from the start
2. Don't be vague or ambiguous
3. Don't over-constrain roles
4. Don't use LLMs for deterministic tasks
5. Don't skip testing edge cases
6. Don't use unfamiliar languages
7. Don't expect perfection on first try
8. Don't hardcode brittle if-else logic
9. Don't ignore the basics
10. Don't use every technique at once

### Agent-Specific Considerations

**For Agentic Systems**:
- Find the "right altitude"—not too prescriptive, not too vague
- Use reasoning and feedback blocks before tool calls
- Design efficient, well-documented tools
- Curate context iteratively
- Guide how to think, not what to think
- Maintain simplicity and transparency
- Start simple, add complexity only when needed

### Pattern: Workflow vs Agent

**Workflow**: System where LLMs and tools interact through predefined flows

**Agent**: System where the LLM dynamically decides its process and tool usage, autonomously managing how to complete tasks

**Guidance**: Start with simple prompts, optimize them with comprehensive evaluation, and add multi-step agentic systems only when simpler solutions fall short.

---

## Key Agentic Design Patterns

### 1. Augmented LLM

Augments the LLM with:
- Retrieval capabilities
- Memory for knowledge-grounding
- Tool capabilities
- Current AI models can generate their own search queries, select appropriate tools, and determine what information to retain

### 2. Prompt Chaining Workflow

Decomposes a task into a sequence of steps where each LLM call processes the output of the previous one.

**When to Use**: Tasks that can be easily divided into fixed subtasks, trading off latency for higher accuracy

**Structure**: Chain = sequence of operations that can be composed to form complex workflows

---

## Resources

### Official Anthropic Documentation

- [Prompt Engineering Overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Be Clear and Direct](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)
- [Use Examples (Multishot Prompting)](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multishot-prompting)
- [Let Claude Think (Chain of Thought)](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
- [Use XML Tags](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)
- [Prefill Claude's Response](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response)
- [System Prompts](https://docs.anthropic.com/claude/docs/system-prompts)
- [Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Control Output Format (JSON Mode)](https://docs.anthropic.com/claude/docs/control-output-format)

### Anthropic Engineering Blog

- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Claude Code: Best Practices for Agentic Coding](https://www.anthropic.com/engineering/claude-code-best-practices)

### Interactive Resources

- [Anthropic's Interactive Prompt Engineering Tutorial (GitHub)](https://github.com/anthropics/prompt-eng-interactive-tutorial)
- [Anthropic Courses Repository](https://github.com/anthropics/courses)
- [Anthropic Cookbook - Agent Prompts](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents/prompts)

### Third-Party Resources

- [AWS: Prompt Engineering with Claude 3 (GitHub)](https://github.com/aws-samples/prompt-engineering-with-anthropic-claude-v-3)
- [Simon Willison: Claude 4 System Prompt Analysis](https://simonwillison.net/2025/May/25/claude-4-system-prompt/)

---

## Conclusion

Effective prompt engineering for agents requires balancing specificity with flexibility, providing clear guidance while allowing the model to reason, and continuously iterating based on real-world failures. The key is finding the "right altitude"—specific enough to guide behavior effectively, yet flexible enough to handle the complexity and variability of real-world tasks.

As you design agent instructions, remember:
- Start minimal and iterate
- Be clear, not clever
- Use examples to demonstrate, not just describe
- Structure with XML for clarity
- Enable reasoning with chain of thought
- Design efficient tools and context
- Test thoroughly, especially edge cases
- Continuously refine based on failures

The future of prompt engineering is **context engineering**—managing the entire lifecycle of information that flows through agent systems. Master these fundamentals, and you'll be well-equipped to build effective, reliable AI agents.

---

*This research document is current as of December 2025 and reflects Anthropic's latest guidance for Claude 4.x models including Sonnet 4.5, Opus 4.5, and Haiku 4.5.*