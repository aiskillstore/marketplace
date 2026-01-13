# Planning Principles

Implementation planning is a critical phase in the development lifecycle of an AI agent. It transforms ambiguous user requests into executable, verified actions.

## 1. The Principle of Least Surprise
Users should never be surprised by what the agent does. The plan acts as a contract. If you deviate from the plan during implementation, stop and explain why.

## 2. Iterative Planning vs. Big Design Up Front
Avoid spending hours on a perfect plan for a massive task. Instead:
1. Plan a manageable milestone.
2. Get approval.
3. Implement.
4. Plan the next milestone.

This keeps you and the user aligned and allows for early course correction.

## 3. Proactive Questioning
Don't wait for the user to find flaws. Search for them yourself.
- "What happens if this network call fails?"
- "Is this the correct naming convention for this project?"
- "Are there existing utilities that do this already?"

Presenting questions with proposed answers demonstrates competence and reduces user cognitive load.

## 4. Environment Awareness
Planning should always start with exploration. Use `ls`, `grep`, `find`, and `read_file` to understand the landscape before proposing a blueprint.

## 5. Risk Mitigation
Identify the most "dangerous" parts of your proposal (e.g., changing shared libraries, bulk file deletions) and highlight them. Propose safe verification steps for these risks.
