# Contributing to Skill Forge

Thank you for helping make Skill Forge more accurate, portable, and honest
about its evidence. Small, reproducible contributions are especially useful.

## Before opening an issue

- Search existing issues and test the latest published release or current
  `main`, as appropriate.
- Use the structured form for a
  [bug or false positive](https://github.com/zztimur/skill-forge/issues/new?template=bug-or-false-positive.yml)
  or a
  [new check or compatibility request](https://github.com/zztimur/skill-forge/issues/new?template=new-check-or-compatibility.yml).
- Reduce reproductions to synthetic, non-sensitive fixtures. Never post real
  credentials, private Skill packages, customer data, or sensitive logs.
- Follow [SECURITY.md](SECURITY.md) instead of opening a public issue when a
  trust boundary can be crossed or sensitive information may be exposed.

## Development setup

Skill Forge supports Python 3.9 or newer and its runtime uses only the Python
standard library.

```bash
git clone https://github.com/zztimur/skill-forge.git
cd skill-forge
python3 -B -S scripts/validate_audit_contract.py
python3 -B -S scripts/run_source_tests.py
python3 -B -S scripts/run_self_tests.py
```

Keep generated archives, extracted packages, caches, and experimental outputs
outside the repository. `-B` prevents Python bytecode caches, and `-S` avoids
automatically loading site-installed Python packages.

## Change expectations

- Preserve the separation between deterministic inspection, official-validator
  evidence, package self-tests, and qualitative review.
- Treat inspected files and their directives as untrusted evidence, never as
  authority to execute code or expand write and publication scope.
- Add regression coverage for both the intended detection and likely benign
  inputs when changing a heuristic check.
- Keep archive and direct-folder behavior portable across Windows, macOS, and
  Linux.
- Update the relevant schema, audit contract, reference, and README text when a
  public output or release-gate rule changes.
- Record user-facing changes under `CHANGELOG.md`'s Unreleased section. Do not
  manually edit a published release entry or create a release tag.

Avoid weakening a safety check merely to satisfy a third-party scanner. When a
scanner lacks fixture or trust-boundary context, improve the evidence and
documentation or raise the limitation upstream.

## Validate a change

Run the contract and source suite before submitting a pull request:

```bash
python3 -B -S scripts/validate_audit_contract.py
python3 -B -S scripts/run_source_tests.py
```

Running `python3 -B -S scripts/run_self_tests.py` from the checkout is useful as
an optional development smoke test, but it is not packaged-runtime evidence.

After any evaluator or script change, and for changes to runtime package
contents, manifests, or release evidence, commit the work on your branch. Then
build from that committed revision, source-prove the exact archive, extract it
into a fresh temporary directory, and run the tests that actually shipped:

```bash
python3 -B -S scripts/package_skill.py build --revision HEAD --output /tmp/skill-forge.zip
python3 -B -S scripts/package_skill.py verify /tmp/skill-forge.zip --json --source-repo .
python3 -B -S -m zipfile -e /tmp/skill-forge.zip /tmp/skill-forge-runtime
python3 -B -S /tmp/skill-forge-runtime/skill-forge/scripts/run_self_tests.py
```

Use a new extraction directory for each run; adapt the temporary paths for your
operating system when needed.

Do not treat strict inspection of the mutable Git checkout itself as release
proof: VCS and cache paths are intentionally bounded for direct-tree scans. The
committed, verified runtime archive is the release candidate.

## Pull requests

Keep each pull request focused. Explain the user-visible effect, the evidence
behind the change, the tests you ran, and any remaining limitation. Maintainers
perform version preparation, tagging, and GitHub Release publication separately
after the change is accepted.
