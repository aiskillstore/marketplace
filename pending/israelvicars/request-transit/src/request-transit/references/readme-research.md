# README research (Oct 2026)

These are the patterns from 12 READMEs of comparable projects that we applied to `README.md`. Each one was read from the raw README on its default branch.

## Examples

| # | Project | URL | What it does well |
| --- | --- | --- | --- |
| 1 | charmbracelet/vhs | https://github.com/charmbracelet/vhs#readme | Logo, then 3 badges, then a **one-line pitch** ("Write terminal GIFs as code for integration testing and demoing your CLI tools."), then the **hero GIF**, then a caption saying the GIF was made with the tool itself ("view source"). The tutorial comes before installation. |
| 2 | asciinema/asciinema | https://github.com/asciinema/asciinema#readme | Two badges, a bold name plus a one-sentence definition, a paragraph saying *how it differs* (text recordings vs. heavy video files), then a demo embed and a "Notable features" bullet list. |
| 3 | excalidraw/excalidraw | https://github.com/excalidraw/excalidraw#readme | A full-width cover image with light/dark variants (`<picture>`), a centered link row, a two-line pitch as `<h2>`, then a badge row and a GIF. The features list puts the important ones first. |
| 4 | mermaid-js/mermaid | https://github.com/mermaid-js/mermaid#readme | Centered logo and tagline ("Generate diagrams from Markdown-like text."), then a link row (docs, getting started, live editor). Examples are shown as **source next to the rendered output**. |
| 5 | jaegertracing/jaeger | https://github.com/jaegertracing/jaeger#readme | Many badges. The **Quick Start is one `docker run` block** with comments for ports and the UI URL, then an architecture diagram. The heavy governance sections are pushed to the bottom. |
| 6 | CtrlSpice/otel-desktop-viewer | https://github.com/CtrlSpice/otel-desktop-viewer#readme | It has personality (a mascot and a dark-mode joke) and a one-sentence definition ("a local OpenTelemetry viewer"). It has a ToC, screenshots per signal, install per channel, and an **"Agent Usage Skill"** section. Its local/in-memory storage notes act as an implicit privacy note. |
| 7 | anthropics/skills | https://github.com/anthropics/skills#readme | It defines a skill in one sentence and has a "Try in Claude Code / Claude.ai / API" section **per client**. It shows a minimal `SKILL.md` and has a disclaimer block. |
| 8 | microsoft/playwright-mcp | https://github.com/microsoft/playwright-mcp#readme | A one-line pitch, then **"MCP vs CLI+skills" positioning**, 3 key features, requirements, a "standard config" JSON, **one-click install badges and a manual block per client** (VS Code, Cursor, Claude, ...), and a Security section. |
| 9 | modelcontextprotocol/servers | https://github.com/modelcontextprotocol/servers#readme | `> [!IMPORTANT]` and `> [!WARNING]` callouts state up front what the repo is *not* (reference code, not production). It is a curated bullet list with one line per item. |
| 10 | datadog-labs/mcp-server | https://github.com/datadog-labs/mcp-server#readme | Short: a pitch, then a **`claude mcp add` one-liner**, then a `.mcp.json` block, then a callout for region-specific endpoints. Everything else is a link. |
| 11 | getsentry/sentry-mcp | https://github.com/getsentry/sentry-mcp#readme | It says who it is for ("designed for human-in-the-loop coding agents") and gives **Claude Code plugin install commands**. It is honest about maturity ("still a work in progress") and separates stdio from remote. |
| 12 | PostHog/mcp | https://github.com/PostHog/mcp#readme | A one-command installer across clients (`npx @posthog/wizard@latest mcp add` for Cursor, Claude, Claude Code, VS Code, Zed). It also shows the "moved, see monorepo" pattern done gracefully. |

Also looked at: Warp's issues-only README, https://github.com/warpdotdev/Warp#readme (a 1024 px product image as the first element, then a centered link row with ` · ` separators), and Zed's, https://github.com/zed-industries/zed#readme (very short, with links out to the website and docs).

Install locations used in our README come from the vendors' docs:
- Claude Code: https://code.claude.com/docs/en/skills (`~/.claude/skills/<name>/SKILL.md`, or `.claude/skills/` in a project)
- Cursor: https://cursor.com/docs/skills (`~/.cursor/skills/`, `.cursor/skills/`, `.agents/skills/`; it also loads `~/.claude/skills` and `~/.codex/skills`)
- Codex: https://developers.openai.com/codex/skills (`.agents/skills` in the repo, `$HOME/.agents/skills` for the user)

## Patterns

- **Hero first.** The visual tools (vhs, excalidraw, Warp) put the image or GIF in the first screen, before any prose longer than one line. vhs captions it with "made with this tool", which is the strongest possible proof. Hero widths run 500–1024 px, and GIFs stay well under a few MB.
- **One-line pitch.** It is a verb phrase or a definition of under ~12 words, either directly under the title or as a centered `<h2>`. A second sentence says how it differs (asciinema), or who it is for (sentry-mcp).
- **Quickstart length.** The best are 1–3 commands (jaeger: one `docker run`; datadog: one `claude mcp add`). Long option references live below or in other docs.
- **Install per agent client.** Agent-adjacent tools give a separate block per client (Claude Code / Cursor / Codex / VS Code), usually as a list with a code block or one-click badges. Ours is a skill, not a server, so the honest equivalent is a folder link per client.
- **Badges.** Mature projects show 2–3 meaningful ones (release, build, license). Badge walls (jaeger) push the pitch down. Pre-release projects shouldn't show badges for things that don't exist yet.
- **Features.** A short bullet list or table with the important features first. Mermaid's source-next-to-output beats prose.
- **How it works.** A small diagram (jaeger) or a 3–4 step pipeline. A mermaid flowchart renders natively on GitHub.
- **Honesty callouts.** `[!NOTE]`/`[!WARNING]` blocks say what is reference-only, experimental or untested (MCP servers, sentry-mcp). Status labels per integration build trust.
- **Privacy/security.** Data-touching tools state where data goes (playwright-mcp's Security section, otel-desktop-viewer's local storage notes). For trace tools the key promise is "local, no network at view time, PII redacted".
- **MCP positioning.** playwright-mcp explicitly says when CLI+skills beats MCP and when it doesn't. Transit sits *next to* MCP servers: it consumes what the observability MCP servers return and turns it into a picture.

## Branding

- 🚇 (metro) is the primary mark: it reads as "transit/subway" at a glance and matches the tagline.
- Alternatives considered: 🚥 / 🚦 (traffic lights). They suggest status (ok/slow/error) but read as roads, not transit. They could be useful as status glyphs later.
- No landing page, Vercel or Pages for now. The README is the front door.

## Applied to README.md

The hero GIF comes first. The README also has:
- the tagline and a one-sentence "how it differs"
- a callout for pre-release status
- a 3-command quickstart
- install per client (Claude Code, Cursor, Codex)
- an MCP-adjacent positioning section
- a supported-sources table with honest status labels
- a how-it-works mermaid diagram
- a privacy section
- a links table for the deeper docs

No badges yet: there is nothing published to badge.
