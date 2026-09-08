# Boyue Distribution

This document is the repository-level source of truth for Agent Skill distribution. The GitHub repository remains canonical.

## Canonical identity

- Repository: `wuaishare/boyue`
- Skill path: `/SKILL.md`
- Canonical repository license: MIT
- Version source of truth: `SKILL.md` + GitHub Releases

## Distribution matrix

| Surface | Repository policy | Current integration mode |
| --- | --- | --- |
| skills.sh | GitHub-native | Install with `npx skills add wuaishare/boyue`; repository is canonical |
| SkillsMP | GitHub-indexed | Eligible for automated discovery through Agent Skill metadata and GitHub topics |
| AgentSkill.sh | Registry import/sync | Imported from the canonical `SKILL.md`; security score 100/100. GitHub owner-level re-import/claim remains to be normalized after registry API rate limiting |
| Smithery Skills | Git-backed/API listing | Ready for listing; Smithery account/namespace authorization is still required |
| ClawHub | Registry publish | **Published:** https://clawhub.ai/wuaishare/boyue — the ClawHub distribution is MIT-0; the canonical GitHub repository remains MIT |
| AI智库 | First-party catalog | **Published:** https://ai.wuaishare.cn/hub/boyue/ — richer GitHub/i18n/security enrichment is tracked as a catalog pipeline improvement |

## Rules

1. GitHub is the canonical source; registries should not become divergent copies.
2. Keep `SKILL.md`, release version, license and marketplace metadata consistent.
3. Do not silently change the canonical repository license because a marketplace uses a different distribution license.
4. Marketplace listings must preserve links back to Wuaishare and the canonical repository where the platform supports them.
