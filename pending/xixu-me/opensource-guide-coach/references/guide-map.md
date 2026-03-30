# Open Source Guides Map

Use this file to route open source questions to the smallest useful set of official guide topics.

## Current English Guide Set

| Slug                                              | Official title                                  | Use when                                                                                                        | Common signals                                                                     | Official URL                                                                |
| ------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `starting-a-project`                              | Starting an Open Source Project                 | Someone is deciding whether to open source a project or wants to prepare for launch.                            | "should I open source this", "what do I need before launch", "how do I start"      | <https://opensource.guide/starting-a-project/>                              |
| `how-to-contribute`                               | How to Contribute to Open Source                | The user wants better contributor onboarding or wants to help with an open source project.                      | "how can people contribute", "first contribution", "new contributor path"          | <https://opensource.guide/how-to-contribute/>                               |
| `finding-users`                                   | Finding Users for Your Project                  | The project exists, but adoption, discoverability, or user feedback is weak.                                    | "how do we get users", "nobody knows about the project", "how do we grow adoption" | <https://opensource.guide/finding-users/>                                   |
| `building-community`                              | Building Welcoming Communities                  | The user wants a healthier community experience, better participation, or a more inclusive project culture.     | "community health", "welcoming contributors", "participation", "inclusive project" | <https://opensource.guide/building-community/>                              |
| `best-practices`                                  | Best Practices for Maintainers                  | Maintainers need clearer process, healthier boundaries, or better ways to handle incoming work.                 | "too many issues", "too many PRs", "how do I say no", "maintainer process"         | <https://opensource.guide/best-practices/>                                  |
| `leadership-and-governance`                       | Leadership and Governance                       | The project needs shared decision-making, clearer authority, or formal governance norms.                        | "who decides", "governance", "maintainers vs contributors", "decision process"     | <https://opensource.guide/leadership-and-governance/>                       |
| `getting-paid`                                    | Getting Paid for Open Source Work               | The user is exploring sustainability, sponsorship, grants, or business support for the project.                 | "funding", "sponsor", "how do we sustain this", "can maintainers get paid"         | <https://opensource.guide/getting-paid/>                                    |
| `code-of-conduct`                                 | Your Code of Conduct                            | The project needs behavior expectations, enforcement norms, or healthier interaction standards.                 | "code of conduct", "moderation", "harassment", "community rules"                   | <https://opensource.guide/code-of-conduct/>                                 |
| `metrics`                                         | Open Source Metrics                             | The user wants to measure project health, impact, contributor flow, or growth without guessing.                 | "what should we measure", "metrics", "health indicators", "success"                | <https://opensource.guide/metrics/>                                         |
| `legal`                                           | The Legal Side of Open Source                   | The user has licensing or legal-basics questions about operating an open source project.                        | "license", "legal", "can I use this", "what should we choose"                      | <https://opensource.guide/legal/>                                           |
| `maintaining-balance-for-open-source-maintainers` | Maintaining Balance for Open Source Maintainers | A maintainer is overwhelmed, burned out, or struggling to protect time and energy.                              | "burned out", "too much maintenance", "need a break", "exhausted"                  | <https://opensource.guide/maintaining-balance-for-open-source-maintainers/> |
| `security-best-practices-for-your-project`        | Security Best Practices for your Project        | The user wants to improve project trust through maintainership-level security hygiene and disclosure practices. | "security posture", "responsible disclosure", "dependency safety", "trust"         | <https://opensource.guide/security-best-practices-for-your-project/>        |

## Quick Pairings

- New project with unclear launch readiness: `starting-a-project`
- New project plus growth concerns: `starting-a-project` + `finding-users`
- Better contributor funnel: `how-to-contribute` + `building-community`
- Maintainer overload: `best-practices`
- Maintainer overload plus burnout: `best-practices` + `maintaining-balance-for-open-source-maintainers`
- Decision bottlenecks or unclear authority: `leadership-and-governance`
- Governance plus interaction norms: `leadership-and-governance` + `code-of-conduct`
- Sustainability planning: `getting-paid`
- Measuring impact after launch: `metrics`
- Trust and project hygiene: `security-best-practices-for-your-project`

## Routing Notes

- Prefer the user's pain point over the broadest article.
- Avoid pairing `legal` unless the user is clearly asking about licensing or legal concerns.
- Avoid sending a first-time maintainer into formal governance too early unless the problem is really about decision-making.
- `best-practices` is often the anchor article for maintainers; add a second guide only when the pain point is clearly broader.
