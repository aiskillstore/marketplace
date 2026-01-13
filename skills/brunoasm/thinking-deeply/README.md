# Deep Thinking Protocol - Claude Skill

A custom Claude skill that prevents automatic agreement or disagreement by enforcing deeper analysis and multi-perspective thinking.

## Overview

This skill makes Claude pause and think more deeply when responding to questions or statements that might trigger quick agreement or disagreement. Instead of reflexively validating user assumptions, Claude will:

- Reframe questions to expose underlying concerns
- Present multiple valid perspectives
- Identify context-dependent factors
- Provide nuanced, well-reasoned recommendations

## What Problem Does This Solve?

Without this skill, Claude may:
- Quickly agree with user statements without thorough analysis
- Accept embedded assumptions without questioning them
- Provide binary yes/no answers without exploring nuances
- Miss important context or alternative perspectives
- Validate the user's framing even when broader analysis would be more helpful

## How It Works

When Claude encounters questions or statements that could lead to automatic responses, this skill triggers a structured thinking process:

1. **Pause and Recognize**: Identify what's really being asked
2. **Reframe**: Transform the question into a broader investigation
3. **Map the Landscape**: Consider multiple perspectives, trade-offs, and context
4. **Structured Response**: Deliver analysis using a clear framework
5. **Avoid Anti-Patterns**: Resist reflexive agreement/disagreement

## Installation

### For Claude.ai (Web/Mobile Apps)

1. Download this repository as a ZIP file
2. Ensure the ZIP structure is:
   ```
   claude_rethink.zip
   └── claude_rethink/
       ├── Skill.md
       └── README.md
   ```
3. Go to Claude.ai Settings > Capabilities > Skills
4. Click "Upload Skill" and select the ZIP file
5. Enable the "Deep Thinking Protocol" skill

### For Claude API

Place the `Skill.md` file in your skills directory according to your API integration setup. Consult the Claude API documentation for skill configuration.

## Usage Examples

### Example 1: Technology Choice

**User asks:** "React is better than Vue for this project, right?"

**Without skill:** "Yes, React would be a great choice!"

**With skill:** Claude will:
- Reframe: Identify what makes a framework "better" for the specific context
- Analyze: Compare React and Vue across multiple dimensions
- Consider: Team experience, project complexity, timeline, hiring needs
- Recommend: Provide context-dependent guidance with clear reasoning

### Example 2: Architectural Decisions

**User states:** "Obviously using microservices is the modern way to build applications."

**Without skill:** "You're right, microservices are definitely the modern approach!"

**With skill:** Claude will:
- Challenge: Question whether "modern" equals "appropriate"
- Explore: Analyze microservices vs. monolith trade-offs
- Contextualize: Consider team size, operational maturity, actual scale needs
- Advise: Suggest architecture based on specific requirements, not trends

### Example 3: Binary Choices

**User asks:** "Should I use TypeScript or JavaScript?"

**Without skill:** "TypeScript is the better choice - use TypeScript!"

**With skill:** Claude will:
- Expand: Transform binary choice into a spectrum of considerations
- Compare: Analyze benefits and trade-offs of each option
- Identify: Determine which factors matter for this specific situation
- Guide: Provide decision framework rather than simple directive

## When the Skill Activates

The skill triggers when Claude detects:

- Confirmation-seeking questions ("Is X the best?", "Should I do Y?")
- Leading statements ("Obviously A is better than B")
- Binary choice questions ("Which is better, X or Y?")
- Assumption-laden questions
- Situations prompting quick validation
- Polarizing statements

## Benefits

- **Deeper Analysis**: Forces consideration of multiple perspectives
- **Better Decisions**: Users receive context-dependent guidance
- **Reduced Bias**: Prevents confirmation bias from reflexive agreement
- **Learning**: Users understand trade-offs and decision factors
- **Intellectual Honesty**: Promotes truth-seeking over validation

## Configuration

The skill works out-of-the-box with no configuration needed. Claude will automatically apply the Deep Thinking Protocol when appropriate.

To adjust when the skill triggers, you can modify the description field in `Skill.md`:

```yaml
description: Engage deeper analysis when responding to user statements or questions requiring confirmation, preventing automatic agreement or disagreement
```

Make this description more specific to narrow triggering, or more general to broaden it.

## Version History

- **1.0.0** (2025-01-17): Initial release
  - Core deep thinking protocol
  - Structured response framework
  - Multiple usage examples

## Contributing

To improve this skill:

1. Test with various question types and note where it helps/hinders
2. Identify patterns where the skill should (or shouldn't) trigger
3. Refine the structured response framework
4. Add more examples for specific domains

## License

This skill is provided as-is for use with Claude. Modify and distribute freely.

## Support

For issues or questions:
- Review the `Skill.md` file for the complete protocol
- Test with different question phrasings
- Check Claude skill documentation: https://support.claude.com/en/articles/12512198-how-to-create-custom-skills

## Related Resources

- [Claude Skills Documentation](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Professional Objectivity in AI Interactions](https://www.anthropic.com/research)
