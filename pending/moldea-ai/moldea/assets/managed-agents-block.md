<!-- moldea:start -->

When installed in this repository, moldea provides project context. Explicit moldea operations, planning, creating, reviewing, or changing agents or skills, changes to what an in-app model decides or says (including inline calls), and project-context work use only the exact <repo-root>/{{skill-path}}/SKILL.md. If it is missing, continue without moldea and without searching for another copy, installing, or initializing; for an explicit moldea operation, report the unavailable installation. Otherwise, first read it unless its complete unchanged instructions are available, then follow its routing before repository checks. For other repository planning, implementation, or review, once you know the involved files, check only the exact files <repo-root>/{{skill-path}}/SKILL.md and <repo-root>/{{skill-path}}/scripts/relevance-gate.mjs. If either is missing, skip this section silently without searching for another copy, installing, or initializing moldea. Otherwise, before editing or giving conclusions, run:

node "<repo-root>/{{skill-path}}/scripts/relevance-gate.mjs" --repository "<repo-root>" --path "<file>" [--path "<file>" ...]

<repo-root> is the absolute repository root. Pass file paths relative to that root, even from a subdirectory. Use only already-known paths; do not scan or run Git for this. With no known paths, skip this precheck.

- Output 1: read <repo-root>/{{skill-path}}/SKILL.md unless its complete unchanged instructions are already available; retain the checked paths and result.
- Output 0 or an error: continue without moldea and do not mention it.

If the task involves new files later, check only that new batch once before acting. Reuse unchanged results.
<!-- moldea:end -->
