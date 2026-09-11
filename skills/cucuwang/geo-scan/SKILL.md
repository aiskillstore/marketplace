---
name: geo-scan
description: Use when auditing a website or build output for deterministic content-readiness regressions and evidence-bounded discovery checks
---

# GEO Scan — Content Readiness Audit

Run geoptimize against a URL or build directory. The deterministic report is suitable for regression checks; optional Gemini, Copilot, or Claude reviews are experimental and do not predict ranking, indexing, rich results, visibility, or citation.

## Workflow

1. Identify the URL, file, or build directory.
2. Run the deterministic scan with machine-readable output:

   ```bash
   npx geoptimize scan <target> --json
   npx geoptimize scan <directory> --dir --json
   ```

3. Report the deterministic score, methodology version, critical findings, and heuristic limitations.
4. Use `--multi-ai` only when the user explicitly asks for a subjective review. Label the result an experimental blend and keep the deterministic score separate.
5. Prioritize sourced quantitative claims, unintentional `noindex`, malformed or misleading structured data, and reproducible content regressions.
6. Suggest `/geo-generate` only for an optional artifact preview. State that `llms.txt` is an unscored proposal.

## Boundaries

- FAQ content and `llms.txt` have no score impact.
- A score increase is not evidence of a ranking or citation increase.
- Generated schema must match visible content and current feature documentation.
- If a URL scan fails, use an authorized local build instead of bypassing access controls.
- Always use `--json` when another tool will consume the result.
