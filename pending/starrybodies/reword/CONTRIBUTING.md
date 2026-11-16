# Contributing to Reword

Issues and small, focused pull requests are welcome. Fork the repository, create a branch, make the change, and describe the behavior it fixes or adds. Include a synthetic before/after example when that makes the change easier to review.

## Run the core tests

Use Python 3.10+ from the repository root. There are no package dependencies:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/reword.py --version
```

Unset `REWORD_VOICE` while testing so an installed personal default cannot affect a test. The GitHub workflow runs the suite on Linux with Python 3.10 and 3.14.

For runtime changes, add a regression test for the changed behavior. Keep temporary files in `tempfile` directories. Documentation-only changes usually need a link and command check rather than a new test.

## Keep private writing private

Use invented prose and identities in issues, tests, and pull requests. Do not upload a real voice collection, personal correspondence, unpublished writing, credentials, or model traces. Keep real samples and stores outside this checkout; `.gitignore` is a backstop, not permission to publish them. If another person's writing is essential to a report, obtain their permission and remove identifying details before sharing.

## Keep the scope clear

The host model writes and distils voice. The Python helpers assemble bounded guidance, manage local collections, and flag possible content changes. Preserve explicit consent, authored/reference distinctions, and the ability to inspect, export, pause, forget, and roll back. Do not turn model acceptance into authored evidence or import sample facts into another draft.

Core tests establish implementation behavior. Claims about writing quality or voice fidelity need separate, appropriate evidence. Do not add detector-evasion claims or unsupported comparisons.

Contributions are provided under the repository's [MIT license](LICENSE). Retain the existing upstream notices.
