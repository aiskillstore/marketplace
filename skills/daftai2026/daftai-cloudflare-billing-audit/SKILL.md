---
name: daftai-cloudflare-billing-audit
description: >
  Audits a Cloudflare application repository offline for code paths and configuration that may create
  usage-based billing exposure. Use when asked to inspect Cloudflare Worker, D1, Durable Objects,
  storage, queue, or compute usage for unexpected bills, billing risks, or cost drivers. Reports
  evidence and uncertainty; it does not access an account or guarantee a spending cap.
---

# Cloudflare Billing Risk Audit

Inspect a user-designated local project for plausible Cloudflare usage-based billing risks and deliver an evidence-linked report. The default mode is read-only, offline, and uses no Cloudflare token or account access.

## Boundaries

- Require an explicit target path. By default, keep generated reports and scanner inventory in this skill's `audit-results/` workspace. If the user chooses another output directory, use it only when it is outside the target tree and tell them where it will be written. This version does not modify the target tree; if the requested output is inside it, explain the conflict and ask for a separate output location.
- Do not run target code, build steps, package scripts, tests, hooks, migrations, `.env` files, or other project commands. Do not read credential or secret-value files, use Cloudflare credentials, sign in, call account APIs, or change account/project configuration.
- Inspect only the config, manifests, and source needed to establish workspace/configuration boundaries, configured entry points, binding declarations, triggers, and relevant call paths. Configuration does not prove what is currently deployed. Do not follow symlinks. Read listed source or auxiliary content only through the scanner's bounded, platform-selected `--read-file` mode with its matching `reviewEvidenceFiles` fingerprint; the path lists alone do not authorize reopening files with `cat`, an editor, or another unanchored reader. Use parsed config metadata from the inventory rather than re-opening config files. Auxiliary evidence is limited to SQL migration files under each valid D1 binding's configured migrations directory (or workspace default) and GitHub Actions YAML workflows when a valid Workers config is present; the scanner does not parse or execute these files. A path absent from the lists stays out of scope. These lists exclude security-sensitive, symlink, unreadable, oversize, and limit-skipped files. If a file identity/content check fails or safe re-read is unavailable, do not use that file and report the uncertainty. Avoid `.git`, dependency/vendor trees, generated output, secret files, and unrelated source. Treat config values and source as private; never paste them into a public request.
- The bounded scanner is required to establish the allowed source/config review scope. It is a candidate-finding aid, not a complete static analyzer or proof of safety. Follow its contract in [references/scanner.md](references/scanner.md); if it cannot run safely, stop the project-source audit and report the blocker rather than bypassing its bounds with manual reads.
- A configured Cloudflare binding or ordinary billable operation by itself is not a billing-risk finding. Trace a plausible trigger to a source-confirmed amplification, duration, retention, or abuse mechanism; inspect its guards before reporting exposure.
- Report confirmed, conditional, and unknown conclusions separately. “No findings” means no supported issue was found in the reviewed scope, not that the application is safe or the account cannot incur a large bill. Do not promise a bill cap or prevention of overages.

## Audit flow

Use [references/workflow.md](references/workflow.md) for the detailed, bounded review method and [references/report-schema.md](references/report-schema.md) for the required report structure.

1. Confirm the explicit target and default or requested output directory, then inventory the bounded repository boundary. Find workspace roots and Cloudflare configuration such as `wrangler.json`, `wrangler.jsonc`, and `wrangler.toml`; inspect only relevant settings and identify configured entry points, named environments, binding declarations, and configured triggers. Do not claim these settings reflect current deployment.
2. Run the bounded scanner under its documented contract. If it cannot run safely, stop the project-source audit and report the blocker. Treat its findings as leads. Independently trace candidate paths and configured entry points from event handlers, scheduled triggers, queue consumers, or Durable Object lifecycle to a plausible chargeable operation; record where the trace stops. Use its controlled read mode with the recorded content fingerprint for listed files; if a file-identity or content check fails, do not draw conclusions from that file. The target tree, its ancestors, and the audit output location must remain stable during scan and review. Record the actual filesystem mode; the macOS/Windows stable-tree adapter is not a hostile-concurrency sandbox.
3. Load only product references relevant to observed usage. Read the matching product guide(s), which contain the relevant evidence links; use [references/sources.json](references/sources.json) for maintenance or when tracing a source ID. Do not load every product guide or the full source index by default. If a relevant guide is missing or evidence is stale/unclear, classify the point as unknown and say what must be verified.
4. Explain exposure through the mechanism: billable operation and unit × invocation volume or fan-out × duration, retention, or other applicable multiplier. Identify the triggering condition, relevant path and line numbers, expected consequence, and a practical mitigation. A binding or configuration declaration alone is not proof that it is exercised.
5. Separate confirmed exposure from conditional scenarios and unknowns. State audited paths, exclusions, unresolved paths, and limitations. Keep script candidates distinct from agent-verified findings. For every completed audit, produce the paired human-readable `agent-report.md` and machine-readable `agent-report.json` described in the schema.
6. Do not estimate dollars by default. If the user requests an estimate, retrieve current official Cloudflare pricing for only the relevant product and clearly state the retrieval date, currency, plan, billing period, usage assumptions, and uncertainties. Pricing and quotas change; local cached knowledge is not current pricing evidence.
7. Present budget alerts as notifications unless current official evidence explicitly documents a stronger behavior. Recommend hard limits only when the current product supports them and the specific limit applies; do not imply a budget or alert is a global spend stop.

## Script Directory

The helper is in this skill's `scripts/` directory. Resolve the absolute path of this `SKILL.md` as `SKILL_DIR` and set the command working directory to `${SKILL_DIR}`. Before running it, detect Bun once per session with `command -v bun` in a POSIX shell or `Get-Command bun` in PowerShell. If Bun is unavailable or the platform cannot meet the scanner's documented filesystem contract, stop the project-source audit and report the blocker; do not fall back to opening the raw project path.

Linux uses descriptor-anchored access; macOS/Windows use a weaker portable stable-tree adapter with identity checks. Neither is an atomic snapshot. Read the platform boundary in [references/scanner.md](references/scanner.md) before scanning; stop if a stable tree cannot be established. No raw-path manual-read fallback is allowed.

Run the inventory helper with the user's explicit target path:

```bash
bun ${SKILL_DIR}/scripts/audit.ts --project "/absolute/path/to/project"
```

By default, scanner inventory goes under `${SKILL_DIR}/audit-results/` in a unique run directory. If the user requests a separate audit directory, add `--output-dir "/absolute/path/to/audit-workdir"`, verify that it is outside the target tree, and tell the user where the report will be written. Save the paired agent reports in the same run directory as `inventory.json` and `inventory.md`. Follow [references/scanner.md](references/scanner.md) for exact output placement, runtime behavior, and safe interpretation. Do not run the command from the target project directory.

Retrieve only a listed source or auxiliary file through the fingerprint-checked reader, after inventory generation:

```bash
bun scripts/audit.ts --project "/absolute/path/to/project" --inventory "/absolute/path/to/audit-workdir/inventory.json" --read-file "src/worker.ts"
```

Use the exact relative path from `reviewEvidenceFiles` and the inventory created for this same run; legacy schema 1.0 inventory files are rejected. The command emits only the explicitly selected file text to local audit context; do not redirect or save that output, and never place source, SQL, or YAML text in either report. If the reader rejects stale identity/fingerprint data, discard that inventory for the affected path, regenerate inventory once against a stable tree, and only then consider a fresh controlled read. If the check still fails, leave the path unknown. The reader exits `2` for argument/safety/platform rejection and `3` for stale or changed inventory evidence; stdout is empty on refusal. Follow [references/scanner.md](references/scanner.md) for exact guarantees; do not substitute `cat` or another raw-path reader.

## Product references

Use only guides that match the code path under review:

- [Workers and request triggers](references/workers.md)
- [D1](references/d1.md)
- [Durable Objects](references/durable-objects.md)
- [Storage services](references/storage.md)
- [Queues and fan-out](references/queues.md)
- [Compute and AI](references/compute-ai.md)
- [Operations, limits, and guardrails](references/operations.md)

These references are maintained evidence notes, not account-specific conclusions. An audit of a project and maintenance of the product evidence are separate tasks; see [references/maintenance.md](references/maintenance.md).
