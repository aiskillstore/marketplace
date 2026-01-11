---
name: persona-testing
description: Test LogiDocs Certify features from customer persona perspectives. Use when the user wants to test features as a customer, get simulated feedback, review UI from user perspective, or mentions "test as Aftrac", "test as Sirius", "customer feedback", "user testing", or "persona review".
---

# Persona Testing Skill

Test LogiDocs Certify from customer perspectives to identify UX issues, missing features, and friction points before actual customer feedback.

## When to Use

Use this skill when:
- Testing features from a customer perspective
- Generating simulated customer feedback
- Reviewing UI/UX from user viewpoint
- Preparing for customer demos
- Identifying friction points before release

## Available Personas

### Aftrac (End User)
**Agent:** `aftrac-tester`
**User:** Thabo Molefe - Quality & Compliance Manager
**Context:** First-time compliance, CE/UKCA marking, ~50 components

**Invoke:** "Test this feature as Aftrac" or "What would Thabo think of this?"

### Sirius (Consultant)
**Agent:** `sirius-tester`
**User:** Kate & Steve - Senior ISO Consultants
**Context:** 1,200+ clients, ISO 9001/14001/45001

**Invoke:** "Review this as Sirius" or "Would Kate recommend this to clients?"

## Usage Patterns

### Feature Review
```
Review the documents page from Aftrac's perspective.
```

### Browser Testing
```
As Sirius, test the signup flow and evaluate credibility.
```

### Feedback Simulation
```
Generate feedback Aftrac would give after uploading 20 documents.
```

## Testing Scenarios

### Aftrac Scenarios
1. **First Login** - First impression, can they understand what to do?
2. **Document Upload** - Upload and organize supplier certificates
3. **CE Marking Checklist** - Find and understand requirements
4. **Progress Report** - Answer CEO's "How close are we?"
5. **Expiring Certificate** - Handle upcoming expiry

### Sirius Scenarios
1. **Demo Evaluation** - Does it look credible for clients?
2. **Client Onboarding** - Set up new ISO 9001 client
3. **Evidence Search** - Find "management review process" evidence
4. **Multi-Client View** - Manage 15 active clients
5. **Audit Prep** - Prepare for ISO surveillance audit

## Comparison Matrix

| Aspect | Aftrac | Sirius |
|--------|--------|--------|
| Role | End User | Consultant |
| Expertise | Limited | Expert |
| Need | Guidance | Efficiency |
| Risk | Getting lost | Reputation damage |
| UX Priority | Clarity | Speed |

## Post-Testing Report

After testing, generate:

```markdown
## Persona Testing Report: [Feature]

### Tested As: [Persona]

### First Impressions
- [What they notice immediately]

### Positive Observations
- [What works well]

### Friction Points
- [Where they struggle]

### Missing Features
- [What they expected]

### Recommendations
- [Priority fixes]

### Quote (In Character)
> "[What they would actually say]"
```

## Integration

This skill works with the persona agents:
- `.claude/agents/aftrac-tester.md`
- `.claude/agents/sirius-tester.md`

The agents contain detailed persona context, while this skill provides testing methodology.
