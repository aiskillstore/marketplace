// Public copy fixture pinned to PR #3699. Revision counters are synthetic, not provider evidence.
export const fixture = {
  "source": {
    "pr": 3699,
    "head": "268edece37b97b1ba6daa5e310845ea8b3390b70",
    "base": "4ac52da14aa9a0249c404cfd9e66486e701ce8fa",
    "reportPath": "skills/cagdasyurekli/agy-worker/skill-report.json",
    "baseReportHash": "4e7244bd6addc54fecfbe0392ec35f41d04d5b40388eb4d001795a33a7424629",
    "headReportHash": "cfb56800e82c4a54e88a5f876e19e08ffcc4671b96e1c3825706dd70f9f527e5"
  },
  "simulation": {
    "artifactRevision": 7,
    "copyRevision": 2
  },
  "packageVersion": "0.22.0",
  "before": {
    "user_title": "Delegate Repository Work Through Antigravity",
    "value_statement": "Complex repository tasks require controlled delegation and independent verification. This skill stages approved content, runs Antigravity, and binds review evidence to each candidate.",
    "seo_keywords": [
      "Claude",
      "Codex",
      "Claude Code",
      "Google Antigravity",
      "repository automation",
      "agent delegation",
      "code verification",
      "Git worktree",
      "AI coding workflow",
      "provider isolation"
    ],
    "actual_capabilities": [
      "Previews provider-readable repository content before dispatch.",
      "Stages approved files in a private Gitless workspace for scoped jobs.",
      "Delegates exploration, implementation, and project work to the agy CLI.",
      "Tracks job state, time limits, continuation, cancellation, and preserved results.",
      "Creates isolated verification copies and runs driver-selected checks.",
      "Binds approvals, candidate bytes, verification evidence, and final disposition with digests."
    ],
    "limitations": [
      "The host integration supports Codex only, not Claude or Claude Code.",
      "Live delegation requires Bash, Python, Git, agy, provider authentication, and network access.",
      "The default session mode does not provide host containment for the provider.",
      "Worker output remains untrusted until Codex reviews the diff and runs relevant checks."
    ],
    "use_cases": [
      {
        "title": "Delegate a bounded feature",
        "description": "Stage selected files, request a focused implementation, inspect the diff, and verify the candidate before acceptance.",
        "target_user": "Repository maintainer"
      },
      {
        "title": "Expand test coverage",
        "description": "Delegate test creation within an approved scope, then run project tests against an isolated candidate copy.",
        "target_user": "Test engineer"
      },
      {
        "title": "Coordinate a broad project change",
        "description": "Use several controlled cycles for a larger change while retaining explicit approval and final review authority.",
        "target_user": "Technical lead"
      }
    ],
    "prompt_templates": [
      {
        "title": "Explore a repository area",
        "prompt": "Use agy-worker to explore [area]. Read only [paths]. Report findings and uncertainties without making changes.",
        "scenario": "Beginner read-only exploration"
      },
      {
        "title": "Implement a focused change",
        "prompt": "Use agy-worker to implement [change]. Allow edits only under [paths]. Verify with [test command] and review the final diff.",
        "scenario": "Bounded implementation"
      },
      {
        "title": "Repair a verified failure",
        "prompt": "Continue the approved agy-worker job. Provide the sanitized failure from [check]. Keep the existing scope, model, and budget.",
        "scenario": "Same-scope repair"
      },
      {
        "title": "Run a governed project workflow",
        "prompt": "Use the project workflow for [goal]. Approve only [content scope], use [isolation mode], and cap work at [cycles]. Run [checks] before finalization.",
        "scenario": "Advanced multi-cycle delivery"
      }
    ],
    "output_examples": [
      {
        "input": "Explore the parser and identify missing error-path tests.",
        "output": "A scoped findings report lists inspected files, missing cases, supporting evidence, and areas that were not reviewed."
      },
      {
        "input": "Add parser error-path tests under the test directory.",
        "output": "A preserved candidate contains the test changes, a reviewed diff, test results, and a clearly stated verification status."
      },
      {
        "input": "Repair the candidate after one focused test fails.",
        "output": "The same approved conversation receives sanitized failure details and returns a revised candidate for another independent check."
      }
    ],
    "best_practices": [
      "Prefer selected-content staging and review every provider-readable path before approval.",
      "Use exact argv verification and provide only the environment variables required by each check.",
      "Inspect candidate bytes and rerun affected checks before assigning a final disposition."
    ],
    "anti_patterns": [
      "Do not approve a whole worktree that contains secrets or unrelated private files.",
      "Do not treat provider output or worker-reported tests as independent verification.",
      "Do not use session isolation when the provider must lack normal user filesystem authority."
    ],
    "faq": [
      {
        "question": "Which host tools are supported?",
        "answer": "The skill supports Codex. Claude and Claude Code are included as search terms but are not supported hosts."
      },
      {
        "question": "Does installation authorize repository transmission?",
        "answer": "No. Each launch requires an explicit approval that binds the readable content, isolation mode, task, model, and budget."
      },
      {
        "question": "Can the provider read the entire worktree?",
        "answer": "Yes, when whole-worktree mode is approved. Selected-content mode limits the staged repository content but does not contain the host in session mode."
      },
      {
        "question": "Does the skill verify worker claims automatically?",
        "answer": "No. Codex must review the actual candidate and run suitable driver-owned checks before acceptance."
      },
      {
        "question": "Can verification commands access credentials?",
        "answer": "Only explicitly selected variables are passed. Credential-like variables and shell verification require separate acknowledgments."
      },
      {
        "question": "What happens when a check fails?",
        "answer": "The candidate is preserved. An approved same-scope repair can receive sanitized failure details, or the job can finish with a limited disposition."
      }
    ]
  },
  "proposed": {
    "user_title": "Antigravity delegation with independent verification",
    "value_statement": "Delegate repository work to Antigravity CLI from Codex, with clear scope and independent verification.",
    "actual_capabilities": [
      "Explore, implement, and audit repositories.",
      "Preview approved provider-readable content.",
      "Review diffs and bind independent verification evidence.",
      "Repair within the approved scope and budget."
    ],
    "use_cases": [
      {
        "title": "Explore a repository",
        "description": "Find relevant files and report findings without edits.",
        "target_user": "Repository maintainer"
      },
      {
        "title": "Implement a change",
        "description": "Delegate a feature or tests, then review the diff and run checks.",
        "target_user": "Developer"
      },
      {
        "title": "Repair a failure",
        "description": "Continue the approved conversation with sanitized test feedback.",
        "target_user": "Developer"
      }
    ],
    "prompt_templates": [
      {
        "title": "Implement a focused change",
        "prompt": "Use agy-worker to implement [change]. Limit edits to [paths], set the provider scope and budget, and obtain approval before dispatch. Review the diff and verify with [test command].",
        "scenario": "Bounded implementation"
      }
    ],
    "output_examples": [
      {
        "input": "Implement a focused change within approved paths.",
        "output": "A preserved candidate, reviewed diff, independent check results, and stated verification status."
      }
    ],
    "best_practices": [
      "Review provider-readable paths and exclude secrets.",
      "Run independent checks before accepting changes."
    ],
    "anti_patterns": [
      "Treating worker reports as verified results.",
      "Treating session mode as host isolation."
    ],
    "faq": [
      {
        "question": "Which tools do I need?",
        "answer": "For this published 0.22.0 package: Codex, Antigravity CLI (agy), Bash, Python 3, Git, and provider authentication."
      },
      {
        "question": "How do I install it?",
        "answer": "Use the installation options on this page. Installation alone does not authorize provider execution or repository transmission."
      },
      {
        "question": "What happens to my repository content?",
        "answer": "Approved prompts and files may reach Google/Gemini through agy. Prefer reviewed provider scope and exclude secrets. Whole-worktree mode can expose every file in that worktree. Session mode is not host isolation."
      },
      {
        "question": "How is the work verified?",
        "answer": "Codex reviews the actual diff and runs independent checks. Worker reports alone do not prove correctness. Repairs stay within the approved scope and budget; verification does not automatically commit, merge, or publish work."
      }
    ]
  },
  "excludedFields": [
    "seo_keywords"
  ],
  "excludedChanges": {
    "seo_keywords": [
      "Codex",
      "Antigravity CLI",
      "repository exploration",
      "agent delegation",
      "code verification"
    ]
  },
  "protectedNonContentHash": "754324a5cb87772953e910bd30d02f37d371e94b0152cfd82feb1d2cb12695bd",
  "nonContentEqual": true,
  "limitationsEqual": true
};
