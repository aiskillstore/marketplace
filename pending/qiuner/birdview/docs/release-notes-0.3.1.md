# Birdview 0.3.1

[中文](release-notes-0.3.1.zh.md)

This patch fixes CLI startup through symbolic links, strengthens installation diagnostics, and refines viewer motion without changing the layout.

- Worker CLIs now recognize their entry point through symbolic links, including Node's `--preserve-symlinks-main` mode (#25).
- `doctor` executes the installed validation CLI and checks its exit status and JSON report. Silent exits, malformed reports and failed processes can no longer pass the check (#26, #27).
- Flow markers retain their animation when still active. Shorter transitions and interruptible guide movement respect reduced-motion preferences and keep keyboard navigation immediate (#28, #29).
- Migration-only frozen implementations and schema copies have been removed. Current behavioral tests, runtime/exported-schema comparisons and reproducible build checks remain (#28, #29).

Follow the [installation guide](installation.md) to update the complete skill bundle. Run `npm ci` and `node scripts/birdview.mjs doctor` in the skill directory. Refresh configured projects with `setup --project <project-root>` and start a fresh agent task; preserve local customizations. Existing invocation modes are preserved. Generated JavaScript is included, so users do not need to compile TypeScript. Distribution remains through GitHub; the npm package is private.

Verification covers 87 unit tests, seven Chromium suites, strict type checks, reproducible artifacts, example validation, demo generation, paired documentation and clean committed-source installation. CI checks Windows and Linux with Node.js 18 and 24.

`doctor` probes one installed worker CLI and renders in memory; it does not exercise every command or prove skill activation in an agent session. Birdview displays agent-declared snapshots and instructions, not independently observed edits or filesystem enforcement. This patch does not claim a measured improvement in AI coding quality.
