# Release Evaluator Provenance

Load for independent release evidence and the historical bootstrap only.

### Pinned independent-evaluator helper

The source checkout includes `python3 scripts/verify_independent_evaluator.py` for a
bounded run against a separately installed Skill Forge tree. The evaluator must
already be trusted from evidence outside the candidate and the current run. A
required whole-tree SHA-256 pins every accepted evaluator path, byte, and mode;
the required candidate SHA-256 pins the exact ZIP. The optional inspector
SHA-256 is an additional check and never substitutes for the whole-tree pin.
Do not derive the trusted evaluator pin from the candidate checkout and then
describe that circular value as independent provenance.

```bash
python3 -S scripts/verify_independent_evaluator.py \
  --evaluator-root /path/to/pretrusted/skill-forge \
  --archive /path/to/candidate.zip \
  --expected-evaluator-tree-sha256 "$EVALUATOR_TREE_SHA256" \
  --expected-candidate-sha256 "$CANDIDATE_SHA256" \
  --json
```

Add `--expected-inspector-sha256 "$INSPECTOR_SHA256"` when a separately
recorded inspector pin is also available.

The helper copies the pinned evaluator and candidate into scratch space, uses
isolated Python (`-I -S -B`) with a credential-reduced environment, and applies
bounded tree, file, output, and wall-time limits while checking both canonical
profiles. It rejects an evaluator that overlaps this source checkout
and verifies the original evaluator and candidate identities again afterward.
It does **not** provide an operating-system filesystem sandbox or network
sandbox, and it does not claim continuous immutability. Use it only with an
evaluator whose complete tree is pretrusted; it is not a safe way to execute an
arbitrary evaluator.

By default, the inspected JSON must use exactly inspector schema version `6`
and satisfy the expected input, target, coverage, manifest-verification,
summary, and count invariants. An older or newer schema is incompatible and
yields **Not Assessed**, never Pass.

There is one bounded bootstrap exception for the first schema-6 release. A
pretrusted schema-5 evaluator may inspect only the exact `v2.0.0` candidate when
the helper receives both explicit arguments:

```bash
--bootstrap-schema-transition 5:6 --bootstrap-release-tag v2.0.0
```

The complete evaluator tree, inspector, and candidate still require pins from
outside the candidate and current run. The helper retains only stable summary
fields and forbids raw schema-5 frontmatter in its report. A passing run is
labeled **bootstrap transition evidence**; it is eligible for G09 only when
every requirement in `independent_evaluator_policy.bootstrap_transition`
passes, including separate schema-6 privacy/output-contract checks and proof
that the candidate release identity is exactly `v2.0.0`. It does not count as
an independent schema-6 pass and is not reusable after that release. Schema 4,
schema 5 without both exact options, and any other release tag remain Not
Assessed.

The overall helper states and process exits are `pass` (`0`), `fail` (`2`), and
`not_assessed` (`3`). A normal-schema Pass establishes independent strict
inspection for this candidate only; a bootstrap Pass establishes only the
bounded transition evidence described above. Review every profile and error
before attributing a Fail to the artifact, and complete the remaining
qualitative, official-validator, and release-gate evidence separately.
