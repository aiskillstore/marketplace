# Distribution research (Oct 14, 2026)

**Scope:** research only. Nothing in this file has been published or submitted. Each item says where its status comes from: URLs I fetched on 2026-10-14, star counts from the GitHub API on the same day, and npm registry lookups.

**What we're distributing:** `github.com/israelvicars/request-transit`, one Agent Skill with `SKILL.md` at the repo root plus Node scripts. On first run it installs npm deps and Playwright Chromium itself and needs ffmpeg (`scripts/setup.mjs`). Anything that only copies the folder works, because setup runs on first use.

## 1. Official channels

| Channel | Status (fetched) | How you get in | Fit |
| --- | --- | --- | --- |
| **Claude Code plugin marketplace (self-hosted)**: [docs](https://code.claude.com/docs/en/plugin-marketplaces), [plugins overview](https://code.claude.com/docs/en/plugins) | Live. Any git repo with `.claude-plugin/marketplace.json` (`name`, `owner`, `plugins[]` of `{name, source}`). Users run `claude plugin marketplace add israelvicars/request-transit` and then `claude plugin install request-transit@<marketplace>`. Sources can be a relative path, `github`, `git-subdir`, `url`, `archive`, `npm` or `command`. Check with `claude plugin validate .`. Official names like `claude-plugins-official` are reserved | Self-serve, no review | **High.** A one-command install for Claude Code users. The repo can be both the marketplace and the plugin |
| **Anthropic official directory** (`claude-plugins-official`, [repo](https://github.com/anthropics/claude-plugins-official), 37.9k★, pushed today) | Claude Code adds it to every interactive install automatically. Third-party plugins live in `/external_plugins` | [Submission form](https://clau.de/plugin-directory-submission). Plugins "must meet quality and security standards", with manual review | **High reach, uncertain acceptance.** Apply after the plugin is stable and has some users |
| **Claude Marketplace website**: [claude.com/plugins](https://claude.com/plugins) | Web catalog of what the official marketplace lists (docs: "A plugin marketplace isn't Claude Marketplace") | Comes with the official directory | Follows from the row above |
| **anthropics/skills** ([repo](https://github.com/anthropics/skills), 181k★) | Anthropic's own example skills | Not a third-party directory | No |
| **OpenAI Codex skills catalog**: [openai/skills](https://github.com/openai/skills) (28.1k★, last push 2026-09-08) | `.system` (bundled), `.curated` (installable by name with `$skill-installer`) and `.experimental` folders. The README doesn't describe a third-party process. Any GitHub URL already works: `$skill-installer install https://github.com/israelvicars/request-transit` | PR to `.experimental` is possible but not documented as open to outsiders | **Medium.** Document the `$skill-installer <url>` line in the README; a PR is optional |
| **Codex/ChatGPT plugins**: [docs](https://developers.openai.com/codex/plugins), [skills docs](https://developers.openai.com/codex/skills) | One "universal plugin directory" for ChatGPT and Codex; the Codex CLI has `/plugins` that installs "from a configured marketplace". The skills docs say to use plugins for distribution | I didn't find a public submission path or the third-party marketplace file format in the fetched pages (**to verify**) | **Later.** Revisit when the format is documented |
| **Cursor Marketplace**: [cursor.com/marketplace](https://cursor.com/marketplace), [plugins docs](https://cursor.com/docs/plugins), [skills docs](https://cursor.com/docs/skills) | Plugins: "Agent Plugins" (a spec `plugin.json` at the plugin root, with skills and MCP) or "Cursor Plugins" (`.cursor-plugin/plugin.json`). Skills docs: repo skills come in only as plugins via a `.cursor-plugin/marketplace.json` repo import or a team marketplace. Featured entries are mostly big vendors (Google, Slack, Granola) | There's a "Publish" link on the marketplace; review criteria weren't visible in the fetched text (**to verify**) | **Medium.** Cursor already reads `~/.claude/skills` and `~/.agents/skills`, so any installer below covers Cursor |
| **Agent Skills spec**: [agentskills.io](https://agentskills.io), [spec repo](https://github.com/agentskills/agentskills) (26.1k★) | Spec plus a client showcase (Claude Code, Codex, Cursor, Copilot/VS Code, Gemini CLI, OpenCode, Goose, Amp, Kiro and ~40 others). **There's no skill directory**, only clients | n/a | Make sure the frontmatter is spec-only (`name`, `description`, optionally `license`, `compatibility`, `metadata`) so every client loads it. Ours is already spec-only |
| **GitHub topics** | Free discovery and crawler food: skillsmp and VoltAgent both crawl GitHub | Repo settings | **Do now.** Suggested topics: `agent-skills`, `claude-skills`, `claude-code`, `claude-code-plugin`, `codex`, `cursor`, `opentelemetry`, `distributed-tracing`, `observability`, `visualization`, `datadog`, `posthog`, `grafana-tempo`, `aws-xray` |

## 2. Unofficial registries and directories

| Directory | Size / traffic signal | How listing happens | Notes |
| --- | --- | --- | --- |
| **skills.sh** (Vercel): [site](https://skills.sh), CLI [vercel-labs/skills](https://github.com/vercel-labs/skills) (34.8k★) | The `skills` npm package had **25.1M downloads** from 2026-09-13 to 10-12 ([npm API](https://api.npmjs.org/downloads/point/last-month/skills)). The leaderboard's top entries have 1–4M installs | **Automatic.** `npx skills add owner/repo` installs from any git URL. The leaderboard counts installs, and the CLI sends anonymous telemetry (README "Telemetry"; opt out with `DISABLE_TELEMETRY`), so listing appears to follow from installs (inferred; no submit form seen). The CLI supports `-g` global, `-a claude-code -a codex …`, symlink (default) or `--copy`, plus `list/update/remove` | **Biggest channel and zero work.** README line: `npx skills add israelvicars/request-transit -g`. There's also a badge (`https://skills.sh/b/<owner>/<repo>`) |
| **SkillsMP**: [skillsmp.com](https://skillsmp.com) | "3,497,602 collected SKILL.md files"; sorted by occupation and creator; featured collections | **Auto-crawl** of public GitHub (its about page: "3M+ skills scattered across GitHub repositories") | Probably indexed already or soon; topics help. No action |
| **agentskills.in** (`agent-skills-cli`): [site](https://agentskills.in) | Claims "175k+ skills" and its own `skills` binary (`npm i -g agent-skills-cli`). Its command name clashes with Vercel's `npx skills` | Appears to aggregate | Low priority |
| **Smithery** (now part of Arcade.dev): [smithery.ai/skills](https://smithery.ai/skills) | "25,154 skills found"; MCP-first, with a "Publish" flow and a "Verified" filter | Self-publish (login) | Optional. Its audience overlaps the MCP-adjacent positioning |
| **VoltAgent/awesome-agent-skills** ([repo](https://github.com/VoltAgent/awesome-agent-skills)) | 35.7k★, pushed 2026-10-13, "1000+ agent skills" | **PR.** Quality criteria in the README: third-person description, under 500 lines, no absolute paths, scoped tools | **Good first PR.** We meet the criteria |
| **ComposioHQ/awesome-claude-skills** ([repo](https://github.com/ComposioHQ/awesome-claude-skills)) | 77.1k★, pushed 2026-09-18 | PR per CONTRIBUTING.md | Good second PR |
| **travisvn/awesome-claude-skills** ([repo](https://github.com/travisvn/awesome-claude-skills)) | 15.4k★, last push 2026-04-28 (quiet) | PR | Low priority |
| **hesreallyhim/awesome-claude-code** ([repo](https://github.com/hesreallyhim/awesome-claude-code), [CONTRIBUTING](https://github.com/hesreallyhim/awesome-claude-code/blob/main/CONTRIBUTING.md)) | 55.7k★, pushed today | **Web UI issue form only.** PRs or the CLI risk a temporary ban. The maintainer says to get users first | Submit only after real usage |
| **skillhub.club** | Reachable (HTTP 200); not evaluated | ? | Skipped |

## 3. Packaging options

### npm + `npx request-transit` (name is free: `registry.npmjs.org/request-transit` returns 404)
- Add `bin: {"request-transit": "scripts/cli.mjs"}` with these commands:
  - `install [--claude] [--codex] [--cursor] [--all] [--copy]`: symlink the package folder (or copy it, with `--copy`) into `~/.claude/skills/request-transit`, `~/.agents/skills/request-transit` (Codex; Cursor reads this too) and optionally `~/.cursor/skills/request-transit`.
  - `uninstall`: remove those links.
  - `doctor`: run `setup.mjs --force`.
  - `render <trace>`: pass through, so the CLI is useful without an agent.
- **Caveat:** `npx` runs from a temporary npm cache, so a symlink to it would break. The installer must copy into a stable home such as `~/.request-transit/<version>` and link to that. With a global install (`npm i -g request-transit`), linking to the global package folder is fine.
- Trim the package with `files: [...]` (skip `out/`, `examples/`, `docs/*.gif`) and keep Playwright as a regular dependency. Chromium still downloads on first run, as it does today.
- **Pros:** versioned, updatable, works without git. **Cons:** a second install path to maintain. Vercel's `npx skills add` already does the multi-agent symlinking, so our own installer mostly helps people who don't know about `skills`.

### `npx skills add` (existing third-party installer)
- Works today with no changes: `npx skills add israelvicars/request-transit -g -a claude-code -a codex -a cursor`. **To verify:** whether it handles a repo-root `SKILL.md` alongside a large repo. It accepts tree URLs and `--skill`, so a single root skill should resolve. Test before you document it.

### Claude Code plugin
- Add `.claude-plugin/plugin.json` (`name: request-transit`, version, description, author, homepage, license) and `.claude-plugin/marketplace.json` with one entry, `{ "name": "request-transit", "source": "./" }`. Docs say a relative path from the marketplace root without `..` is valid, but **to verify:** whether `"./"` (the repo root itself) is accepted. The fallback is moving the skill to `skills/request-transit/`, or a `github` source pointing at the same repo.
- A `SKILL.md` at the plugin root loads with the frontmatter `name` ([skills docs](https://code.claude.com/docs/en/skills), "Plugin root SKILL.md"), so the command becomes `/request-transit:request-transit`.
- Installed plugins are copied into `~/.claude/plugins/` cache. First-run setup would then write `node_modules` into the cache, which updates replace. A later improvement is to put deps in `${CLAUDE_PLUGIN_DATA}` (persists across updates).

### Homebrew tap (`israelvicars/homebrew-tap`)
- **Pros:** one familiar command for macOS users, and it can declare `depends_on "node"` and `depends_on "ffmpeg"`.
- **Cons:**
  - Chromium can't reasonably be a formula dependency, so it would still be downloaded by Playwright post-install or on first run.
  - The formula can't write into `~/.claude/skills` (Homebrew discourages touching $HOME), so users still run a link step.
  - It's macOS/Linuxbrew only, adds a tap to maintain per release, and for an agent skill it duplicates npm.
- **Verdict:** skip unless there's demand.

## 4. Recommendation (ranked)

| # | Step | Effort | Files / changes |
| - | --- | --- | --- |
| 1 | **GitHub topics + description check** | 5 min | Topics listed in §1 (repo settings; `gh repo edit --add-topic …`) |
| 2 | **Document the `npx skills add` path and test it on a clean machine/user** (Claude Code, Codex, Cursor) | 30 min | README install section: `npx skills add israelvicars/request-transit -g`; optional skills.sh badge. This is how skills.sh listing happens |
| 3 | **Claude Code plugin + self-hosted marketplace in the same repo** | 1–2 h | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`; run `claude plugin validate .`; test `claude plugin marketplace add israelvicars/request-transit` + `claude plugin install request-transit@request-transit`; README lines |
| 4 | **Awesome-list PRs**: VoltAgent/awesome-agent-skills, then ComposioHQ/awesome-claude-skills | 30 min each | One-line entry each; needs your approval since it's posted under your name |
| 5 | **npm package with `npx request-transit install`** | half a day | `package.json`: `name`, `bin`, `files`, `engines.node >=18`, `repository`, `keywords`; `scripts/cli.mjs` (install/uninstall/doctor/render; copy to `~/.request-transit/<ver>` and then link); tests; `npm publish` (needs approval) |
| 6 | **Anthropic directory submission** (form) | 30 min + review wait | Needs step 3 done, a stable version, and a short security note (what the plugin runs: node, Playwright Chromium, ffmpeg; no network beyond installs) |
| 7 | Codex `$skill-installer` README line now; Codex/ChatGPT plugin and Cursor Marketplace once their third-party formats are verified | 15 min now; later TBD | README line; later `.cursor-plugin/` or Agent Plugin `plugin.json` |
| 8 | Smithery skills listing, awesome-claude-code issue form (after users) | 20 min each | none |
| – | Homebrew tap | skip | – |

## Sources (all fetched 2026-10-14)
- Claude Code: https://code.claude.com/docs/en/plugin-marketplaces · https://code.claude.com/docs/en/plugins · https://code.claude.com/docs/en/skills · https://github.com/anthropics/claude-plugins-official · https://claude.com/plugins
- Codex: https://developers.openai.com/codex/skills · https://developers.openai.com/codex/plugins · https://github.com/openai/skills
- Cursor: https://cursor.com/docs/skills · https://cursor.com/docs/plugins · https://cursor.com/marketplace
- Spec: https://agentskills.io · https://github.com/agentskills/agentskills
- Directories: https://skills.sh · https://github.com/vercel-labs/skills · https://skillsmp.com · https://skillsmp.com/about · https://agentskills.in · https://smithery.ai/skills · https://github.com/VoltAgent/awesome-agent-skills · https://github.com/ComposioHQ/awesome-claude-skills · https://github.com/travisvn/awesome-claude-skills · https://github.com/hesreallyhim/awesome-claude-code
- npm: https://registry.npmjs.org/request-transit (404 = free) · https://api.npmjs.org/downloads/point/last-month/skills
