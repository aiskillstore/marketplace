# review.json Schema

The agent outputs a `review.json` file. The posting script reads it and creates a GitHub Review with inline comments.

**Never post comments directly.** Write `review.json` to the path given in `$REVIEW_OUTPUT_PATH` (default: `/tmp/review.json`).

## Schema

```json
{
  "verdict": "APPROVED" | "APPROVED_WITH_SUGGESTIONS" | "CHANGES_REQUESTED",
  "summary": "1-2 sentence plain-text summary for the PR-level review body",
  "counts": {
    "critical": 0,
    "high": 0,
    "observations": 0
  },
  "findings": [
    {
      "id": "security-no-rate-limiting",
      "domain": "security" | "performance" | "react-ts" | "testing" | "test-validity" | "devops" | "holistic" | "duplication" | "bug" | "scope" | "thermo" | "comments",
      "severity": "critical" | "high" | "observation",
      "path": "src/api/handler.ts",
      "line": 42,
      "title": "No rate limiting on public endpoint",
      "problem": "The /login route has no rate limiting, allowing brute-force attacks.",
      "fix": "Add express-rate-limit middleware before this handler.",
      "fix_prompt": "Add rate limiting to the /login route in src/api/handler.ts at line 42.\n\nUse express-rate-limit with max: 10 requests per 15 minutes per IP.\n\nExpected outcome: brute-force attempts are throttled with a 429 response."
    }
  ]
}
```

## Field rules

- **`id`**: `{domain}-{kebab-case-title}` — must be stable across re-runs for the same logical finding so suppression matching works. Do not include line numbers in the id.
- **`path`**: relative path from repo root, exactly as it appears in the diff header (`+++ b/src/...` → `src/...`).
- **`line`**: the **new-file** line number in the diff where the issue is located (the `+` side). Use the last relevant line if the issue spans multiple lines. If the finding is file-level with no specific line (e.g. a missing file), omit `line` — the posting script will post it as a file-level comment.
- **`fix_prompt`**: plain text, no markdown formatting inside the string. Concise enough to paste directly into a chat prompt.
- **`summary`**: written for the PR-level review body. Include verdict emoji: ✅ / ⚠️ / ❌. Mention counts.

## stdout fallback (no PR number)

When running locally with no PR number, print `review.json` content to stdout instead of writing to a file.
