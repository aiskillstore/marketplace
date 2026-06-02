# Release Checklist

Dittobot's detailed release runbook now lives in the wiki:

https://github.com/RegionallyFamous/dittobot/wiki/Release-Checklist

Short version:

1. Update `CHANGELOG.md`.
2. Run the deterministic validation suite.
3. Build and check the plugin package.
4. Generate the public scorecard.
5. Push and wait for GitHub Actions.
6. Tag the validated commit and create the GitHub release.

Use live eval only as a bounded smoke test. Keep it separate from deterministic release proof, and use a real threshold such as `--fail-under-score 0.95` when citing live transcript scorecards as passing.
