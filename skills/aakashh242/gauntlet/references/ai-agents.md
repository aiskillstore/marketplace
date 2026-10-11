# AI, tools, RAG, and agent-skill lens

Trigger: LLM-powered workflows, tool-using agents, prompts, retrieval, evals, or skill packages.

## Authority and data boundaries

Map user intent, system/developer policy, skill instructions, retrieved material, model outputs, and executable tools. Untrusted material must not confer authority. Test instructions embedded in documents, comments, web pages, logs, filenames, and tool results that ask the agent to ignore boundaries, expose secrets, or perform unrelated actions. Review the host's actual enforcement; prompt text alone is not a sandbox.

Check tool arguments against schemas, resource ownership, allowlists, confirmation requirements, idempotency, and output provenance. Agent-produced paths/URLs are not automatically safe. Ensure previews and approvals identify the exact action and revision that will execute. Prevent stale approval from silently covering modified content.

## Reliability and termination

Review token/cost budgets, recursive tool calls, sub-agent depth, retry behavior, context loss, checkpoint/resume, timeouts, and partial completion. Missing optional tools should trigger a stated fallback; missing mandatory evidence must remain a blocker. A plan is not execution, a generated citation is not a retrieved source, and agent consensus is not verification.

For multi-agent systems, examine correlated assumptions, authorship/verification separation, conflicting writes, evidence sharing, duplicate findings, and an orchestrator's stop criteria. Test the no-sub-agent path explicitly. Do not expose all secrets to every worker for convenience.

## Retrieval and generation quality

Check document/version provenance, retrieval relevance, grounding, citation correctness, stale indexes, unauthorized retrieval, context truncation, and handling of conflicting sources. Evaluate hallucinated claims separately from stylistic preference. Use source content rather than judging a response by a convincing tone.

## Evaluation integrity

Separate training/prompt tuning examples from held-out evaluation. Avoid answer leakage into retrieval or tools. Include failure cases, task refusal/permission boundaries, unavailable tools, ambiguous requirements, clean inputs, and corrupted evidence. Report model/version, run count, budgets, oracle, and uncertainty. A self-judged pass is not an independently established success.

## Skill-specific checks

Validate frontmatter and discoverability, exact relative paths, trigger boundaries, progressive loading, script help/errors, dependencies, and no unintended installation/network side effects. Confirm that runtime records stay outside the installed skill directory. Test that instructions distinguish review-only from repair permission and that no response falsely claims delegated work.

For Gauntlet itself, use the included behavioral evaluations and compare against the same agent without the skill under a similar budget. Until that experiment is run, describe this as a designed workflow with tested helper logic, not a benchmark-proven reviewer.
