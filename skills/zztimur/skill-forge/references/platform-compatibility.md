# Platform Compatibility Profiles

Use one or more explicit inspector profiles for the supported surfaces where a
Skill will run. Run one inspector invocation and preserve one compatibility
result per selected canonical profile. A passing profile is compatibility
evidence for that profile only; it does not prove that every other host,
runtime, permission model, or upload path accepts the same package.

## Source verification

The supported OpenAI surface is documented at [OpenAI: Skills in
ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt).
Skill Forge's `openai` metadata checks are a local tooling policy, separate
from external product compatibility claims. No product upload limit is encoded
for either supported profile; the configurable inspector limit is an internal
resource and safety boundary.

## Published field constraints

Verified 2026-09-06 against the [Agent Skills specification](https://agentskills.io/specification): both profiles enforce the 1024-character description maximum, the optional compatibility string (1–500 characters), and metadata as a string-to-string map. Existing packages with overlong descriptions or invalid field types now fail strict validation. Concise and non-English descriptions receive no automatic quality penalty. These checks do not certify native-host behavior; platform-specific local rules and optional extensions remain distinct.

## Contract source of truth

Standard audits select the two audit target profiles from inspector output and
this reference without loading the full Release contract. The source contract
validator keeps these mirrored profile rules synchronized. Release audits load
[`audit-contract.json`](audit-contract.json); each `target_contracts` record
carries its verification date, source URL, host-verified rule keys, Skill Forge
policy recommendations, frontmatter expectations, layout rule, and known
product upload limit. A `null` product limit is an explicit **Not Applicable**
host-limit result, not permission to treat an internal inspector safety limit
as a host requirement.

## Canonical targets

| Target | What is enforced | What it does not prove |
|---|---|---|
| `portable` | Skill Forge's conservative shared baseline: root `SKILL.md`, lowercase hyphen-case `name`, description, matching folder, a 64-character name ceiling, and conditional OpenAI metadata checks when present. | Every product-specific upload, runtime, invocation, or UI workflow. |
| `openai` | Skill Forge's shared manifest baseline plus the conditional OpenAI metadata contract in `agents/openai.yaml`; an optional `default_prompt` is compared with the declared frontmatter name, including for a flat ZIP extraction. | Any compatibility claim for an unsupported host or an unencoded product upload limit. |

## Commands

```bash
python3 -S scripts/inspect_skill_package.py /path/to/skill --target portable --json --strict
python3 -S scripts/inspect_skill_package.py /path/to/skill --target openai --json --strict
```

For a Skill Forge release artifact, use the package verifier. It verifies the
canonical embedded runtime manifest and runs both canonical profiles.
Archive-only verification does not prove the
declared Git source:

```bash
python3 -S scripts/package_skill.py verify /path/to/skill-forge.zip --json
```

Archive-only verification may pass the package command, but it cannot Pass the
Skill Forge G23 release gate. To satisfy G23, provide a caller-selected local
source repository and require the separate commit/tree/blob proof and
manifest-digest binding:

```bash
python3 -S scripts/package_skill.py verify /path/to/skill-forge.zip \
  --json --source-repo /path/to/skill-forge-source
```

If that local source evidence is unavailable, G23 is **Not Assessed** and the
Skill Forge release gate is blocked. The proof establishes consistency with the selected local Git object graph,
not remote provenance, tag authenticity, or official host compatibility. The
two profile inspections, local source proof, independently pinned Skill Forge
evidence, and official platform validation remain separate claims.

## Reporting rules

- State every requested surface and selected canonical profile in the report.
- Preserve the authoritative findings matrix and release verdict independently
  for every selected profile. An overall roll-up must not hide a failed or Not
  Assessed member.
- Treat `portable` as a conservative starting point, not an all-host
  certification.
- Keep platform findings separate from Skill Forge safety findings. For
  example, a configured inspector refusal is an inspection limitation, not a
  compatibility claim.
- Treat `agents/openai.yaml` as OpenAI-specific metadata; its presence is not
  a requirement for a generic portable review.
