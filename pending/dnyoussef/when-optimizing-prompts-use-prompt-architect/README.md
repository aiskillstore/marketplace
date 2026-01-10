# Prompt Architect - Quick Start Guide

## Purpose
Evidence-based prompt engineering framework for creating and optimizing AI system prompts using proven techniques.

## When to Use
- Poor AI response quality
- Inconsistent outputs
- Creating new prompts
- Applying prompt engineering best practices

## Quick Start

```bash
# Optimize existing prompt
npx claude-flow@alpha skill-run prompt-architect \
  --input "original-prompt.md" \
  --output "optimized-prompt.md"
```

## 5-Phase Process

1. **Analyze Current** (5 min) - Identify weaknesses
2. **Structure Optimization** (10 min) - Reorganize logically
3. **Apply Techniques** (10 min) - Add evidence-based patterns
4. **Validate Effectiveness** (10 min) - A/B testing
5. **Refine Iteratively** (5 min) - Continuous improvement

## Evidence-Based Techniques Applied

- Chain-of-Thought reasoning
- Self-Consistency pattern
- ReAct (Reasoning + Acting)
- Few-Shot learning
- Constraint framing
- Progressive disclosure

## Expected Improvement

```
Average Score: +35%
Success Rate: +28%
Consistency: +42%
```

## Output Format

```json
{
  "original": "...",
  "optimized": "...",
  "improvements": {
    "scoreImprovement": "+35%",
    "successRate": "92%",
    "testsPassed": "5/5"
  }
}
```

## Common Use Cases
- **Agent Prompts**: Optimize system prompts for specialized agents
- **Task Instructions**: Improve task clarity and consistency
- **API Integration**: Create effective prompts for AI APIs
- **Skill Development**: Optimize skill instructions

For detailed documentation, see SKILL.md
