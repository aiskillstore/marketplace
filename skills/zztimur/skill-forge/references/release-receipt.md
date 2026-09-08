# Reviewed publication receipt (schema 1)

Pushing an annotated release tag builds and validates a candidate artifact. It
**does not publish a GitHub Release**. Publication requires a separate
`Release Skill` workflow dispatch with an exact `release_tag`, a successful
`Capture Release Receipt` run ID (`receipt_run_id`), and the reviewer's SHA256
of the exact `receipt.json` bytes (`receipt_sha256`). The source-only verifier
uses Python 3.9+ and GitHub CLI; it does not belong in the installed runtime.

## Trust and evidence boundary

The **reviewer dispatch receipt pin is the reviewer assertion trust root**.
The pin must come from the completed independent review, not be blindly copied
from an unreviewed candidate workflow. The receipt and evaluator tree/inspector
pins are reviewer assertions. A valid shape, a matching digest, or artifact
upload success does not prove their underlying narrative is true.

The verifier separately obtains facts using the authenticated GitHub API:

- The receipt artifact comes from this repository's fixed
  `.github/workflows/capture-release-receipt.yml` workflow, from the requested
  successful run, and its uploading actor matches the declared reviewer.
- The bundle matches GitHub's artifact digest; its exact receipt bytes match
  the external dispatch pin, and its evaluator report bytes match the receipt.
- The selected `Self Tests` run belongs to this repository and workflow ID,
  uses the exact release commit, and completed successfully. Its latest run
  attempt must contain all seven distinct successful jobs: Linux containment
  and bounded tests, plus Ubuntu/macOS/Windows with Python 3.9/3.x. Fork/PR runs,
  skipped jobs, partial reruns lacking all seven jobs, wrong commits, and a
  rerun beginning during verification block publication. Run all jobs again
  when a partial rerun cannot provide a complete attempt.

These CI observations are labeled `github_api_observation`. Review gates are
labeled `reviewer_assertion`, and the evaluator report is labeled
`reviewer_pinned_report`. No host certification, reviewer competence, continuous
immutability, or new live independent evaluation is inferred by this verifier.
The publication job fetches these observations again immediately before creating
the release. It fails closed instead of publishing while checks are pending;
redispatch after the required run succeeds.

## Required receipt fields

All fields below are mandatory; additional fields are rejected.

| Field | Required value |
|---|---|
| `schema_version` | Integer `1` |
| `repository` | Exact `owner/repository` |
| `release_tag` | Exact annotated `vMAJOR.MINOR.PATCH` tag |
| `commit` | Full lowercase 40-character candidate commit |
| `archive_sha256` | Lowercase SHA256 of source-proven `skill-forge.zip` |
| `reviewer` | Object with `github_login` and `evidence_class: "reviewer_assertion"` |
| `independent_evaluator` | Object with `report_sha256`, `tree_sha256`, `inspector_sha256`; each is a reviewer-approved SHA256 |
| `self_tests_run_id` | Positive integer ID of the qualifying Self Tests run |
| `gates` | Exactly G01–G23 once each, using the gate object below |

Each gate has exactly `id`, `result`, `evidence_label`, `evidence_class`,
`rationale`, and `evidence_refs`. A publishing receipt permits only `Pass` or
`Not Applicable`, with `evidence_label: "Verified"` and
`evidence_class: "reviewer_assertion"`. Semantic review gates G05, G14, G17,
G18, G20, and G21 may instead retain `evidence_label: "Inferred"`; this never
relabels predictions as measured facts. Other gates require `Verified` because
they assert inspected facts, observed execution, integrity, or arithmetic.
Unverified evidence cannot support publication. The output preserves each gate's
declared evidence label.

This validator is specifically for the Skill Forge source-and-archive release
pipeline. G01–G07, G09, G11–G18, and G20–G23 must be Pass. The published Agent
Skills description limit makes G06 applicable; bundled OpenAI metadata makes
G07 applicable; the bundled and source suites make G11/G12 applicable; G23 is
specifically the canonical Skill Forge archive proof. A caller cannot bypass
these by declaring a different scope or marking them Not Applicable.

Only G08 (conditional platform-specific fields), G10 (optional official
validator), and G19 (documented product upload limit) may be Not Applicable.
Rationale and evidence references must be nonempty and substantiate the specific
exclusion under the audit contract. The verifier enforces which gates may be
excluded; the reviewer remains responsible for the truth of that rationale.

An unfinished gate record intentionally blocks publication:

```json
{
  "id": "G01",
  "result": "Not Assessed",
  "evidence_label": "Unverified",
  "evidence_class": "reviewer_assertion",
  "rationale": "Independent review is pending.",
  "evidence_refs": ["review:pending"]
}
```

The external file `independent-evaluator.json` must be a complete successful
schema-2 report from `python3 scripts/verify_independent_evaluator.py`, using exact
schema-6 portable and openai checks. Bootstrap-transition evidence is not
accepted. Candidate before/copy/after hashes must all equal the release archive;
evaluator before/copy/after hashes must match the reviewer's independent tree
and inspector pins. Both profiles must show complete manifest/inspection
coverage and strict success, and the report must show completed scratch
execution and verified candidate/evaluator integrity without mutations/errors.
Keep the evaluator pretrusted and independently installed according to that
tool's existing procedure; do not substitute the candidate's own inspector.

## Operator procedure

1. Finish the release commit and annotated tag through the normal authorized
   release process. Obtain the validated candidate's ZIP from the tag-triggered
   `Release Skill` run. Source-prove the exact archive. Ensure `Self Tests` has
   all seven successful jobs on that same commit (run it on that commit's branch
   if necessary).
2. Run the independently installed evaluator against those exact bytes with
   the independently approved tree, inspector, and candidate pins. Save its
   JSON as `independent-evaluator.json`. Complete the independent 23-gate review
   and author `receipt.json`. Compute the report digest and include it in the
   receipt; compute the final receipt digest after review. These files are
   external artifacts, never a follow-up commit that changes the candidate.
3. Review both files for private paths and sensitive source data before upload.
   Prefer generating the independent report in a neutral synthetic review
   workspace. GitHub workflow input/artifact access is not a secrets vault.
4. Capture the exact reviewed bytes through the dedicated workflow. It only
   base64-decodes bounded JSON and uploads files; it never executes input text.
   The combined dispatch inputs must fit GitHub's workflow input size limit;
   each field also has a 60,000-character bound. Oversized evidence is rejected,
   not truncated. Run this on the branch containing the capture workflow; that
   branch does not need to become a new release commit.

```sh
python3 -B -S - <<'PY' > receipt-inputs.json
import base64, json
from pathlib import Path
print(json.dumps({
    'receipt_base64': base64.b64encode(Path('receipt.json').read_bytes()).decode(),
    'evaluator_report_base64': base64.b64encode(Path('independent-evaluator.json').read_bytes()).decode()
}))
PY
gh workflow run capture-release-receipt.yml --ref main --json < receipt-inputs.json
gh run list --workflow capture-release-receipt.yml --limit 5
```

5. After capture succeeds, use its run ID and your independently retained
   receipt hash to dispatch `Release Skill`. Example placeholders below must
   be replaced with the reviewed tag, numeric capture run ID, and receipt hash.

```sh
gh workflow run release-skill.yml --ref main \
  -f release_tag=v3.0.0 \
  -f receipt_run_id=123456789 \
  -f receipt_sha256=REVIEWED_RECEIPT_SHA256
```

A local read-only verification uses the same CLI and makes authenticated API
reads. It performs no upload or publication:

```sh
python3 -B -S scripts/verify_release_receipt.py \
  --repository owner/repository --release-tag v3.0.0 \
  --commit FULL_RELEASE_COMMIT --archive skill-forge.zip \
  --receipt-run-id 123456789 --receipt-sha256 REVIEWED_RECEIPT_SHA256
```

Exit `0` means these publication prerequisites matched; exit `2` means missing,
untrusted, malformed, stale, or incomplete evidence. Keep the review and
independent report in their approved evidence storage after artifact expiry.

API provenance rules follow GitHub's official
[artifact API](https://docs.github.com/en/rest/actions/artifacts),
[workflow run API](https://docs.github.com/en/rest/actions/workflow-runs), and
[workflow jobs API](https://docs.github.com/en/rest/actions/workflow-jobs).
