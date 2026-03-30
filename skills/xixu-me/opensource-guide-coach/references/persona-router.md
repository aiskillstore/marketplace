# Persona Router

Use this table to infer the closest audience persona from the official Open Source Guides personas.

## Quick Decision Table

| Persona                                  | Best fit when                                                                                 | Likely goals                                                                         | Common pain points                                                                                         | Good first guides                                                                                                       |
| ---------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Individual developer (first-timer)       | One person is thinking about open sourcing a project for the first time.                      | Launch well, get noticed, get early feedback.                                        | Unsure whether to open source yet, unclear on readiness, no audience yet.                                  | `starting-a-project`, `finding-users`, `how-to-contribute`                                                              |
| Individual developer (multiple projects) | An experienced solo maintainer runs one or more projects, usually on personal time.           | Protect time, reduce overload, find help, keep the project sustainable.              | Burnout, issue queue pressure, contributor management, unclear boundaries.                                 | `best-practices`, `maintaining-balance-for-open-source-maintainers`, `getting-paid`                                     |
| Community developer                      | The project is intentionally shared with the community and decisions are not purely personal. | Encourage participation, keep the community healthy, share ownership well.           | Community friction, unclear norms, contribution quality, decision disputes.                                | `building-community`, `how-to-contribute`, `leadership-and-governance`, `code-of-conduct`                               |
| Corporate entity                         | A company or formal team is opening a project or maintaining it as part of paid work.         | Grow usage, support brand and recruiting goals, balance company and community needs. | Balancing company constraints with community expectations, adoption, governance, security, legal concerns. | `starting-a-project`, `finding-users`, `leadership-and-governance`, `security-best-practices-for-your-project`, `legal` |

## Inference Rules

- If the user says "my side project", "my library", or "I built this on weekends", start with `Individual developer (first-timer)` unless they clearly describe prior maintainer experience.
- If the user sounds overloaded, mentions issue triage fatigue, or has multiple maintained projects, route toward `Individual developer (multiple projects)`.
- If the user emphasizes shared ownership, community voting, working groups, or consensus, route toward `Community developer`.
- If the user says "we" from a company context, mentions brand, compliance, security policy, or recruiting, route toward `Corporate entity`.

## Fallback Rule

If the persona is ambiguous, choose the smallest-scope persona that still matches the pain point and say the assumption in the `Situation` section.

Example:

`I am assuming this is an early-stage solo-maintainer question because you described a side project and did not mention an existing maintainer team.`
