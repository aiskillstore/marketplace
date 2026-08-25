# GovCon Growth Workflow current test evidence

Tested August 21, 2026 from a clean temporary installation of the complete skill folder.

## Current result

| Surface | Model / version | Result |
|---|---|---|
| Codex CLI | `codex-cli 0.149.0-alpha.4`, GPT-5.6 Sol, xhigh | Pass: explicit invocation returned only the complete nine-choice menu. A government-wide cybersecurity-market scenario listed all four provider modes, exact sanitized terms and URLs, Tavily privacy disclosure, residual disclosure risk, and waited for provider selection and plan approval. No research tool was invoked. |
| Claude Code CLI | `2.1.239`, `claude-opus-5`, max effort | Pass after correction: an initial run exposed that a generic plan-approval question could omit provider selection. The core gate was strengthened. A fresh run then produced all four modes, sanitized terms, exact proposed URLs, the Tavily disclosure, and a combined approval question with zero web-search and web-fetch requests before approval. |
| Claude Code CLI smoke | `2.1.239`, `claude-sonnet-5`, max effort | Pass after correction: the first packaged-plugin smoke returned all nine choices but omitted the final selection question. The exact question was moved into the front-loaded core and made a literal validity gate. A fresh run returned the complete menu and exact question with zero web-search and web-fetch requests. |

## Deterministic and artifact evidence

- Both `quick_validate.py` and the repository eight-skill validator passed.
- The shared evidence contract, web-provider policy, and research-record validator copies were byte-identical.
- Four provider modes validated. Unapproved providers, unapproved plans, missing disclosure acknowledgment, unknown evidence IDs, sensitive query keys, credential-like content, local/private/internal URLs, and signed or credential-bearing URLs failed as expected.
- An approved native-to-Tavily fallback record passed with provider, timestamp, reason, and sanitized query preserved. Reversed Tavily-to-native fallback and the retired Tavily-first combined mode failed new artifact validation; the retired mode remains readable for refresh migration.
- The offline evidence-brief fixture passed record validation, required-section validation, evidence-ID coverage, bid-decision boundary checks, and independent recomputation of `6,000,000.00` from three source values.
- The incomplete company-context fixture correctly produced `Evidence Brief - No Bid Decision` and listed missing vehicle, clearance, teaming, risk, and margin inputs.
- LibreOffice opened the DOCX and converted it to a three-page PDF.
- Text and evidence citations were extracted, and every rendered page was visually inspected after fixing compact-list collisions.

All federal results in the fixture are synthetic. No live federal API call was made for this evidence. Host-managed MCP initialization and tool discovery are distinguished from research-tool invocation.

## Open evidence

- A clean Codex Desktop invocation has not been independently rerun after this skill was added.
- Live Tavily tool discovery and one sanitized provider query are recorded at the agent-package release layer because the standalone skill does not install MCP configuration.
- Each menu branch has a scenario specification, but the complete live-source branch matrix remains release-candidate coverage.
- Implicit activation remains advisory and is not counted as a deterministic invocation path.
- Full upload-only-client and real-opportunity artifact scenarios remain open.

## August 23 calculation-citation correction

- Stable qualification found that a numeric-check paragraph could use the generic marker `[calculation]` even when the research record contained a stable calculation evidence ID.
- The builder now requires exactly one linked calculation evidence item and cites that stable ID. The DOCX validator verifies the ID appears on the same paragraph as the calculated total.
- Regression coverage removes the citation from the numeric paragraph while leaving the evidence register intact and requires validation to fail.

## August 22 stabilization regression

- Source calls now carry stable `Q###` identifiers. Public or federal evidence must cite the source call whose recorded retrieval timestamp it uses.
- The deterministic validator rejects evidence stamped with report-build time when that timestamp does not match a linked source call.
- Clean-client artifact replay remains required at the agent-package release layer.

## August 23 native-first provider regression

- The public-web menu now orders Native web only (Recommended), Native web with Tavily fallback, Tavily only, and No public web.
- Deterministic validation requires the combined mode to start with `native_web`, permits fallback only from `native_web` to `tavily`, and preserves the retired Tavily-first mode only for read-and-migrate intake.
- Native-only failure must stop for a new selection. Account creation, payment, and unapproved provider switching are prohibited. Installed-client behavioral replay remains required at the agent-package release layer.
- Only ten enumerated native failure classes can produce a combined-mode fallback event. Deterministic negatives reject zero or thin results, user-declined permission, content refusal, reversed provider order, and unknown modes.
- Installed-client replay exposed two instruction-salience gaps: the ambiguous reply `native` could be treated as Native web only, and No public web could be misread as disabling approved federal MCP calls. The permanent gate now requires an exact selection, preserves approved federal MCP research, and prohibits account or payment setup as the corrective path. Cross-client replay remains open at the agent-package layer.
- A specific-opportunity Sonnet replay skipped the required first-turn menu and moved directly to intake. The menu-first gate now states explicitly that supplied opportunity, bid-screen, and company context never bypasses the complete nine-choice menu. Cross-client installed-package replay remains required after vendoring.
- A subsequent installed Sonnet replay correctly rejected ambiguous selection but paraphrased combined fallback as available for “insufficient” results. Because zero, thin, or inconclusive results are never fallback triggers, re-presented menus must now reproduce the complete policy choice block without paraphrasing. Agent-package replay remains open.
