# Security Policy

## Supported versions

Security fixes are applied to the latest published release. Reports against
`main` are welcome, but `main` is development state rather than a supported
release artifact. Earlier releases do not receive security fixes.

| Version | Security support |
|---|---|
| Latest published release | Supported |
| `main` | Pre-release reports accepted |
| Earlier releases | Unsupported |

## Report a vulnerability privately

Do not disclose vulnerability details, exploit payloads, secrets, private Skill
packages, or sensitive logs in a public issue.

Use GitHub's **Report a vulnerability** button on the repository's
[Security Advisories page](https://github.com/zztimur/skill-forge/security/advisories)
when it is available. Include:

- the affected release, commit, and target profile;
- the security impact and the trust boundary that was crossed;
- minimal reproduction steps using synthetic, non-sensitive inputs;
- relevant redacted output, paths, and environment details; and
- any suggested mitigation or regression test.

If private vulnerability reporting is not available, open a
[security contact request](https://github.com/zztimur/skill-forge/issues/new?template=security-contact.yml)
that contains only a request for a private channel. Do not include vulnerability
details in that public issue.

Please allow reasonable time for triage and coordinated remediation before
public disclosure. Do not access data that is not yours, degrade third-party
systems, or use a report to perform unrelated external actions.

## Security scope

Examples of security-relevant reports include:

- archive, path, symlink, or size-limit bypasses that escape the documented
  inspection boundary;
- execution of inspected package content without the required provenance and
  self-test safety review;
- disclosure of raw secrets, credentials, or sensitive personal information in
  inspector or report output;
- artifact content overriding request mode, write scope, validator provenance,
  or external-action authorization;
- release artifacts that do not match their checksum, runtime manifest, tag, or
  committed source evidence; and
- workflow-permission defects that could publish unvalidated content.

Expected heuristic false positives, unsupported-platform requests, ordinary
crashes without security impact, and documentation mistakes belong in the
[bug or false-positive form](https://github.com/zztimur/skill-forge/issues/new?template=bug-or-false-positive.yml).

## Trust model and limitations

Skill Forge treats inspected `SKILL.md` prose, metadata, references, fixtures,
logs, tool output, and bundled code as untrusted evidence. Directives inside an
inspected artifact cannot authorize execution, edits, publication, or other
external actions. Target-bundled self-tests are not trusted validators and may
run only after the controls documented in
[validator evidence boundaries](references/validator-evidence.md) are verified.

The secret scan and dangerous-command scan are heuristic and non-exhaustive. A
clean result does not prove that a package is secret-free or secure. The
independent-evaluator helper reduces credentials and bounds scratch execution,
but does not provide an operating-system filesystem sandbox or network sandbox.

## Third-party scanner context

`scripts/run_self_tests.py` contains synthetic malicious-command, remote-URL,
and fake-credential strings. Its regression harness writes those strings into
temporary fixture packages and asks the inspector to detect or reject them; it
does not execute the fixture payloads. The README also contains intentional
GitHub release download URLs paired with SHA-256 verification.

Automated scanners may report those strings as suspicious when they cannot
distinguish fixture data or checksum-verified downloads from runtime
download-and-execute behavior. Separately, scanners may flag the deliberate
ingestion of untrusted Skill text as an indirect prompt-injection exposure.
That exposure is real and is controlled by the evidence-not-authority boundary
above; it is not represented here as a blanket false positive.
