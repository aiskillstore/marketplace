# ShareXtract Distribution

This document is the repository-level source of truth for Agent Skill distribution. The GitHub repository remains the canonical source; third-party registries are discovery/install surfaces, not independent source copies.

## Canonical identity

- Repository: `wuaishare/sharextract`
- Skill path: `/SKILL.md`
- Runtime package: `sharextract`
- Canonical repository license: Apache-2.0
- Version source of truth: `pyproject.toml` + GitHub Releases
- Agent Skills metadata: `SKILL.md` uses the portable `license`, `compatibility`, and `metadata.author/version` fields

## Distribution matrix

| Surface | Repository policy | Current integration mode |
| --- | --- | --- |
| skills.sh | GitHub-native | Install with `npx skills add wuaishare/sharextract`; repository is canonical |
| SkillsMP | GitHub-indexed | Eligible for automated discovery through Agent Skill metadata and GitHub topics |
| AgentSkill.sh | Registry import/sync | Imported from the canonical `SKILL.md`; security score 100/100. GitHub owner-level re-import/claim remains blocked by the registry's GitHub API rate limit |
| skills.re | GitHub import | Submitted from the canonical repository; processing/listing is asynchronous |
| Skillstore | GitHub URL + audit PR | Submission `c3bdf489-27cd-4c45-b40c-d1c94d494de9` produced PR #3323 with a high-risk review. Upstream has since hardened DNS-rebinding/SSRF, browser navigation, proxy trust, and indirect prompt-injection boundaries; CI is green. PR #3323 has been merged into Skillstore's review pipeline; the original audit remains high-risk until a fresh post-hardening rescan can run after the duplicate cooldown |
| Smithery Skills | Git-backed/API listing | **Published/listed:** Smithery skill `wuaishare/sharextract`, backed by the canonical GitHub repository |
| ClawHub | Registry publish | **Published/latest:** https://clawhub.ai/wuaishare/sharextract — `0.23.0`, MIT-0, 5-file thin bundle (`SKILL.md` + four references). The accidental full-repository `0.1.0` version has been withdrawn; the Python runtime remains Apache-2.0 on GitHub |
| AI智库 | First-party catalog | **Published:** https://ai.wuaishare.cn/hub/sharextract/ — richer GitHub/i18n/security enrichment is tracked as a catalog pipeline improvement |

## Rules

1. Do not fork the Skill text per marketplace unless a platform requires a thin packaging adapter.
2. Never change the canonical repository license merely to satisfy a registry without an explicit project decision.
3. Marketplace metadata must point back to the canonical repository and exact Skill path.
4. Version, license, install requirements, security boundaries, and last verification time should remain machine-readable where the platform supports them.
5. ClawHub publishes only the portable Skill layer; the Python runtime remains canonical on GitHub under Apache-2.0.
6. A marketplace listing is a distribution surface, not proof of security or quality; ShareXtract's tests, Adapter Health, provenance and release gates remain the primary evidence.
