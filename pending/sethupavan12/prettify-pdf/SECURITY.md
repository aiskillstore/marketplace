# Security Policy

## Supported Versions

Security fixes target the latest version on the default branch.

## Reporting A Vulnerability

Please do not open a public issue for vulnerabilities involving private PDFs, unsafe script behavior, or prompt-injection risks.

Report privately to the repository maintainer using GitHub private vulnerability reporting if enabled, or by email if the maintainer publishes one.

Include:

- A short description of the issue.
- A minimal reproduction using synthetic or redacted files.
- The affected file or workflow.
- Any suggested mitigation.

## Privacy Expectations

PDFs often contain sensitive personal, financial, medical, legal, or government information. Do not attach real documents to public issues. Use synthetic PDFs, redacted screenshots, or text-only reproductions.

## Scope

In scope:

- Helper script behavior that leaks data, writes outside the requested output directory, or mishandles private files.
- Skill instructions that encourage unsafe relabeling, data mutation, or hidden external calls.
- Supply-chain risks introduced by new dependencies.

Out of scope:

- Behavior of a third-party LLM provider.
- A user's local environment configuration.
- Malicious PDFs that exploit vulnerabilities in external PDF libraries. Report those to the affected upstream project as well.
