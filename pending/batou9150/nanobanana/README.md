# nanobanana-skill

A [Claude Agent Skill](https://github.com/anthropics/skills) for image generation, editing, and restoration via Google's Nano Banana (Gemini image models).

When you ask Claude things like *"generate a watercolor of a fox"*, *"make a favicon for my app"*, *"edit this photo to add sunglasses"*, or *"draw an architecture diagram for a microservices system"*, this skill activates and runs the appropriate Gemini image model. Default: `gemini-3.1-flash-image-preview` (Nano Banana 2).

The repo is also a self-contained Claude Code **plugin marketplace** — install with two commands (no venv, no `pip install`).

## Install (recommended — as a plugin)

In Claude Code:

```text
/plugin marketplace add batou9150/nanobanana-skill
/plugin install nanobanana@batou9150-skills
```

Then set the API key (see [API key — where to put it](#api-key--where-to-put-it)) and you're done.

The CLI is self-contained: it uses a PEP 723 inline-metadata shebang to auto-install `google-genai` on first run via [`uv`](https://docs.astral.sh/uv/). No manual venv or `pip install` step.

### Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) on `PATH` (one-line install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A Gemini API key

## Install (alternative — bare skill, no plugin system)

```bash
git clone https://github.com/batou9150/nanobanana-skill ~/.claude/skills/nanobanana
```

That's it. The first time the script runs, `uv` resolves and caches `google-genai` automatically.

## API key — where to put it

Get a key from <https://aistudio.google.com/apikey>, then choose **one** of:

### Option A — `~/.zshenv` (recommended for zsh users)

```bash
echo 'export NANOBANANA_API_KEY="<your-key>"' >> ~/.zshenv
```

`~/.zshenv` loads for **every** zsh invocation, including the non-interactive shells Claude Code's Bash tool uses. Putting it in `~/.zshrc` only works for interactive terminals — Claude Code won't see it.

(Bash users: use `~/.bash_profile` or whichever rc your shell sources for non-interactive runs.)

### Option B — Claude Code settings only

Add to `~/.claude/settings.json`:

```json
{
  "env": { "NANOBANANA_API_KEY": "<your-key>" }
}
```

Stored in plain text on disk; only visible to Claude Code processes (not to standalone CLI use).

### Fallback env-var names

If you already have a Gemini key set under another name, the skill picks the first that's defined, in this order:

1. `NANOBANANA_API_KEY` (preferred)
2. `NANOBANANA_GEMINI_API_KEY`
3. `NANOBANANA_GOOGLE_API_KEY`
4. `GEMINI_API_KEY`
5. `GOOGLE_API_KEY`

## Subcommands

| Command | Purpose |
|---|---|
| `generate` | Text-to-image with optional batch styles / variations |
| `edit` | Modify an existing image |
| `restore` | Repair / enhance an image |
| `icon` | App icon, favicon, UI element |
| `pattern` | Seamless pattern / texture |
| `story` | Sequential frames (story / process / tutorial / timeline) |
| `diagram` | Flowchart, architecture, schema, wireframe |

## Direct CLI use (without Claude)

The script is fully standalone:

```bash
~/.claude/skills/nanobanana/scripts/nanobanana.py generate \
  "sunset over mountains" --count=3 --styles=watercolor,oil-painting
```

Output goes to `./nanobanana-output/` in your cwd.

Run any subcommand with `--help` to see flags:

```bash
~/.claude/skills/nanobanana/scripts/nanobanana.py generate --help
```

## Model override

```bash
export NANOBANANA_MODEL=gemini-3-pro-image-preview   # Nano Banana Pro
export NANOBANANA_MODEL=gemini-2.5-flash-image       # Nano Banana v1
```

## Credit

Adapted from the official [`gemini-cli-extensions/nanobanana`](https://github.com/gemini-cli-extensions/nanobanana) Gemini CLI extension. This is a Claude-Skill port — no MCP server, no Node runtime, just a self-contained Python script invoked from `SKILL.md`.

## License

MIT — see [LICENSE](LICENSE).
