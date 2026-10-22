---
name: ci-transit
description: A transit map for your CI runs. Use when the user wants to visualize a GitHub Actions run as a subway map. Draws jobs as lines, steps as stations, and failed, cancelled or slow steps as service alerts.
---
<!-- Generated from src/ci-transit/SKILL.md; do not edit -->


# Transit

A public transit map for a GitHub Actions run.

🔒 Runs entirely on the user's machine; run data never leaves it. No telemetry, tracking or analytics. The built page makes no network requests. The only network use is the optional fetch script against the user's own GitHub account through their local `gh` CLI.

## Where things are

`<skill>` below means the folder containing this SKILL.md. Run every script from it by absolute path, e.g. `node <skill>/core/build.mjs ./run.json --format gh-actions --out ./transit-out/ci/transit.html`. Trace paths are relative to the user's working directory. Pass `--out` (build) or `--out-dir` (render) so results land in the user's working directory, not inside the skill folder.

## Steps

1. **Get one run into a file.** Use `node <skill>/src/ci-transit/scripts/fetch.mjs <run-id> [--repo owner/name] [--out run.json]`, or `--last-failed [--workflow name] [--branch b]` instead of a run id for the newest failed run. It invokes the local `gh run list` / `gh run view` commands read-only. Runs with more than 150 steps show only failed or cancelled steps as stations; pass `--max-steps 0` to build/render to show all. Or provide a synthetic or previously saved run JSON file shaped like `gh run view --json ...`.
2. **Build the page to share:** `node <skill>/core/build.mjs <run.json> --format gh-actions --share --title "CI: one run" --subtitle "SYNTHETIC sample data"`.
   Without `--out` the file is named after the title and the failing job, in `./transit-out/`, e.g. `transit-out/ci-test-node-22-service-alert.html`.
   `--share` scrubs at the strict level, refuses `--no-scrub`, and opens the page paused on the first failed step with a one-line verdict above the map.
   Idle stretches with nothing running (e.g. queue waits between jobs) longer than 20 s are shortened to 20 s so the animation isn't dead air; the header says how many were shortened and the root span keeps the wall time as `transit.wall_ms`. Pass `--max-gap-ms N` to change the cap, or `--max-gap-ms 0` for true wall-clock timing.
3. **Share it: the HTML file is the thing to share.** Give the user the file path and the verdict line the build printed, ready to paste,
   and have them drag the file into Slack (desktop and iOS open it as the interactive page) or the PR. Use the printed verdict as is. For example:
   > test (node 22) / Run unit tests failed after 6 min · SERVICE ALERT · 12 dependencies
   > `ci-test-node-22-service-alert.html` opens on the failed step. Click any station for its timing.
4. **Optional teaser (GIF + MP4):** `node <skill>/core/render.mjs <run.json> --format gh-actions --name ci --out-dir ./transit-out/ci --title "CI: one run" --subtitle "SYNTHETIC sample data"`.
5. **Check it:** `node <skill>/core/verify.mjs <run.json> --format gh-actions --name ci`.
6. Report slow steps, failed or cancelled steps, skipped jobs, and the job dependency map shown by the run.

## Rules

- Only render with the bundled scripts. If they fail, stop and report the exact error and command to rerun with more permissions. Never hand-write a substitute renderer or a look-alike GIF.
- Never upload a run or render anywhere unless the user asks.
- GitHub Actions logs and metadata can contain private repository information. Keep the input and output local; use synthetic data for examples and tests.
- `gh` is optional. A saved JSON file can always be passed directly to the core build/render scripts.

## Sharing

By default the run title (it is the PR or commit title) and the branch name are left out of the page, and values in
job and step names and messages are scrubbed (emails, tokens, URL query strings...). Pass `--keep-ci-titles` to keep
the title and branch, `--strict` for the stricter level (`--share` uses it and refuses `--no-scrub`). See request-transit's SKILL.md for the full list.
