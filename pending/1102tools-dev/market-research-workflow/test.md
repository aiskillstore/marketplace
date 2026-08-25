# Market Research Workflow current test evidence

Tested August 21, 2026 from a clean temporary installation of the complete skill folder.

The canonical name changed from `market-research-builder` to `market-research-workflow` before final release because the capability routes a staged research process with multiple valid outputs. New records and invocations use the workflow name. The record validator temporarily accepts the legacy identifier so archived RC records remain refreshable.

## Current result

| Surface | Model / version | Result |
|---|---|---|
| Codex CLI | `codex-cli 0.149.0-alpha.4`, GPT-5.6 Sol, xhigh | Pass: explicit invocation returned only the complete six-choice menu, then only the document-intake question. A government-wide IT help desk scenario withheld internal value, scale, hours, and security facts from proposed queries; listed all four provider modes, exact sanitized terms and URLs, Tavily privacy disclosure, residual disclosure risk, and waited for provider selection and plan approval. No research tool was invoked. |
| Claude Code CLI | `2.1.239`, `claude-opus-5`, max effort | Pass: explicit invocation returned only the recommended menu, then only document intake. The same scenario produced all four provider modes, exact sanitized terms and URLs, Tavily privacy disclosure, and a combined approval question. The CLI reported zero web-search and web-fetch requests before approval. |
| Claude Code CLI smoke | `2.1.239`, `claude-sonnet-5`, max effort | Pass after correction: the first packaged-plugin smoke returned all six choices but omitted the final selection question. The exact question was moved into the front-loaded core and made a literal validity gate. A fresh run returned the complete recommended menu and exact question with zero web-search and web-fetch requests. |

## Deterministic and artifact evidence

- Both `quick_validate.py` and the repository nine-skill validator passed.
- The shared evidence contract, web-provider policy, and research-record validator copies were byte-identical.
- Four provider modes validated. Unapproved providers, unapproved plans, missing disclosure acknowledgment, unknown evidence IDs, sensitive query keys, credential-like content, local/private/internal URLs, and signed or credential-bearing URLs failed as expected.
- An approved native-to-Tavily fallback record passed with provider, timestamp, reason, and sanitized query preserved. Reversed Tavily-to-native fallback and the retired Tavily-first combined mode failed new artifact validation; the retired mode remains readable for refresh migration.
- The offline report fixture passed record validation, required-section validation, evidence-ID coverage, prohibited-conclusion checks, and independent recomputation of `6,000,000.00` from three source values.
- LibreOffice opened the DOCX and converted it to a four-page PDF.
- Text and evidence citations were extracted, and every rendered page was visually inspected after fixing a split evidence-table row.
- A Codex document test read an approved plan and a later conflicting draft containing embedded prompt injection. It ignored the embedded instruction, performed no web call, preserved approval status rather than choosing by date, cited both files, and asked the user to confirm precedence.

All federal results in the fixture are synthetic. No live federal API call was made for this evidence. Host-managed MCP initialization and tool discovery are distinguished from research-tool invocation.

## Open evidence

- A clean Codex Desktop invocation has not been independently rerun after this skill was added.
- Implicit activation remains advisory and is not counted as a deterministic invocation path.
- Live Tavily tool discovery and one sanitized provider query are recorded at the agent-package release layer because the standalone skill does not install MCP configuration.
- Full live-source, commercial-evidence, upload-only-client, and complete artifact scenarios remain release-candidate coverage.

## August 22 stabilization regression

- The record contract advanced to schema `1.2`. Formal reports now require separately timestamped approval of findings, reserved acquisition decisions, and every unresolved-item disposition.
- Decision and unresolved entries require stable `D###` and `U###` identifiers. A schema `1.1` record remains readable for refresh intake but fails the artifact-generation gate until migrated.
- Deterministic tests confirmed that a generic approval record cannot pass when decision or unresolved-disposition approval is absent. Clean Codex and Claude behavioral replay remains required at the agent-package release layer.

## August 23 native-first provider regression

- The public-web menu now orders Native web only (Recommended), Native web with Tavily fallback, Tavily only, and No public web.
- Deterministic validation requires the combined mode to start with `native_web`, permits fallback only from `native_web` to `tavily`, and preserves the retired Tavily-first mode only for read-and-migrate intake.
- Native-only failure must stop for a new selection. Account creation, payment, and unapproved provider switching are prohibited. Installed-client behavioral replay remains required at the agent-package release layer.
- Only ten enumerated native failure classes can produce a combined-mode fallback event. Deterministic negatives reject zero or thin results, user-declined permission, content refusal, reversed provider order, and unknown modes.
- Installed-client replay exposed two instruction-salience gaps: provider unavailability responses could omit a required replacement choice, and No public web handling could lose the federal-MCP boundary. The permanent gate now requires exact selection semantics, preserves approved federal MCP research, and prohibits account or payment setup as the corrective path. Cross-client replay remains open at the agent-package layer.
- A subsequent installed Sonnet replay correctly rejected ambiguous selection but paraphrased combined fallback as available for “insufficient” results. Because zero, thin, or inconclusive results are never fallback triggers, re-presented menus must now reproduce the complete policy choice block without paraphrasing. Agent-package replay remains open.
