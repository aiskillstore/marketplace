#!/usr/bin/env node
// post-review.js
// Reads /tmp/review.json (or $REVIEW_OUTPUT_PATH) and posts a GitHub Review
// with inline comments. Requires: GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER.
//
// GitHub Reviews API:
//   POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
//   Body: { commit_id, body, event, comments: [{ path, line, body }] }
//
// Inline comment body format:
//   <!-- id: {finding.id} -->   ← used by suppression logic on re-run
//   🔴/🟡/💡 **{title}**
//   ...

import { readFileSync } from "fs";
import { execSync } from "child_process";

const REVIEW_PATH = process.env.REVIEW_OUTPUT_PATH ?? "/tmp/review.json";
const TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.GITHUB_REPOSITORY; // "owner/repo"
const PR_NUMBER = process.env.PR_NUMBER;

if (!TOKEN || !REPO || !PR_NUMBER) {
  console.error(
    "Missing required env: GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER"
  );
  process.exit(1);
}

const [owner, repo] = REPO.split("/");

// ── Load review.json ──────────────────────────────────────────────────────────

let review;
try {
  review = JSON.parse(readFileSync(REVIEW_PATH, "utf8"));
} catch (e) {
  console.error(`Failed to read ${REVIEW_PATH}:`, e.message);
  process.exit(1);
}

const { verdict, summary, counts, findings = [] } = review;

// ── Get the head commit SHA ───────────────────────────────────────────────────

const prData = JSON.parse(
  execSync(
    `gh api repos/${owner}/${repo}/pulls/${PR_NUMBER} --jq '{sha: .head.sha}'`,
    { encoding: "utf8" }
  )
);
const commitId = prData.sha;

// ── Build inline comments ─────────────────────────────────────────────────────

const SEVERITY_EMOJI = {
  critical: "🔴",
  high: "🟡",
  observation: "💡",
};

const SEVERITY_LABEL = {
  critical: "Critical",
  high: "High Priority",
  observation: "Observation",
};

function buildInlineBody(f) {
  const emoji = SEVERITY_EMOJI[f.severity] ?? "💡";
  const label = SEVERITY_LABEL[f.severity] ?? f.severity;

  const lines = [
    `<!-- id: ${f.id} -->`,
    `${emoji} **${label}: ${f.title}**`,
    ``,
    f.problem,
  ];

  if (f.fix) {
    lines.push(``, `**Fix:** ${f.fix}`);
  }

  if (f.fix_prompt) {
    lines.push(
      ``,
      `<details>`,
      `<summary>🤖 AI Fix Prompt</summary>`,
      ``,
      "```",
      f.fix_prompt,
      "```",
      `</details>`
    );
  }

  return lines.join("\n");
}

// Findings without a line number → post as file-level comments (line omitted)
const inlineComments = findings.map((f) => {
  const comment = {
    path: f.path,
    body: buildInlineBody(f),
  };
  if (f.line != null) {
    comment.line = f.line;
    comment.side = "RIGHT";
  } else {
    // File-level: GitHub requires subject_type=file when no position is given
    comment.subject_type = "file";
  }
  return comment;
});

// ── Build review body (PR-level summary) ─────────────────────────────────────

const VERDICT_MAP = {
  APPROVED: "APPROVE",
  APPROVED_WITH_SUGGESTIONS: "COMMENT",
  CHANGES_REQUESTED: "REQUEST_CHANGES",
};

const reviewEvent = VERDICT_MAP[verdict] ?? "COMMENT";

const reviewBody = [
  `<!-- cc-pr-review -->`,
  summary ?? "",
  ``,
  `| Severity | Count |`,
  `|---|---|`,
  `| 🔴 Critical | ${counts?.critical ?? 0} |`,
  `| 🟡 High | ${counts?.high ?? 0} |`,
  `| 💡 Observations | ${counts?.observations ?? 0} |`,
].join("\n");

// ── Dismiss any existing bot review (so we don't stack reviews on re-run) ────

try {
  const existingReviews = JSON.parse(
    execSync(
      `gh api repos/${owner}/${repo}/pulls/${PR_NUMBER}/reviews ` +
        `--jq '[.[] | select(.body | test("<!-- cc-pr-review -->"; "i")) | .id]'`,
      { encoding: "utf8" }
    )
  );

  for (const reviewId of existingReviews) {
    // Dismiss only REQUEST_CHANGES reviews — APPROVE/COMMENT don't need dismissal
    try {
      execSync(
        `gh api repos/${owner}/${repo}/pulls/${PR_NUMBER}/reviews/${reviewId} --jq '.state'`,
        { encoding: "utf8" }
      );
      execSync(
        `gh api repos/${owner}/${repo}/pulls/${PR_NUMBER}/reviews/${reviewId}/dismissals ` +
          `-X PUT -f message="Superseded by updated review"`,
        { encoding: "utf8", stdio: "pipe" }
      );
    } catch {
      // Dismissal may fail if review is not in REQUEST_CHANGES state — ignore
    }
  }
} catch (e) {
  console.warn("Could not check existing reviews:", e.message);
}

// ── Post the new review ───────────────────────────────────────────────────────

const payload = JSON.stringify({
  commit_id: commitId,
  body: reviewBody,
  event: reviewEvent,
  comments: inlineComments,
});

try {
  const result = execSync(
    `gh api repos/${owner}/${repo}/pulls/${PR_NUMBER}/reviews ` +
      `-X POST --input -`,
    { input: payload, encoding: "utf8" }
  );
  const posted = JSON.parse(result);
  console.log(
    `Posted review #${posted.id} (${reviewEvent}) with ${inlineComments.length} inline comment(s).`
  );
} catch (e) {
  console.error("Failed to post review:", e.message);
  // Surface the review.json so humans can see what was found even if posting failed
  console.error("review.json contents:");
  console.error(JSON.stringify(review, null, 2));
  process.exit(1);
}
