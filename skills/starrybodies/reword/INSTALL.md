# Install Reword

Reword is a folder-based agent skill. It needs a host that can read its files,
run Python 3.10+, and use a model for writing. Its Python helpers use the standard
library; no package installation, API key or separate Reword service is needed.
Your host's model access, permissions and normal data handling still apply.

Install it by cloning this repository into your host's skills folder, and update
it with `git pull` from inside that folder. Keep personal voice stores outside
the skill folder and outside public repositories.

The [skills CLI](https://skills.sh/) can place the folder for you:

```bash
npx skills add starrybodies/reword
```

## Claude Code

```bash
git clone https://github.com/starrybodies/reword ~/.claude/skills/reword
```

Clone into `.claude/skills/reword` inside a project to install it for that
project only. Invoke it with `/reword Build my voice from these three samples`.

Personal local folders do not automatically make a skill available in Cowork or
cloud sessions. Follow the official host guidance for those environments.
Source: [Claude Code skills](https://code.claude.com/docs/en/skills).

## Codex CLI and IDE extension

```bash
git clone https://github.com/starrybodies/reword ~/.agents/skills/reword
```

Clone into `.agents/skills/reword` inside a repository to install it for that
repository only. Use `/skills` to find it or invoke
`$reword Build my voice from these three samples`.
Source: [OpenAI skill setup and discovery](https://learn.chatgpt.com/docs/build-skills).

## ChatGPT

Use a ChatGPT surface that offers standalone skills and a supported skill
installation flow. Download the
[repository ZIP](https://github.com/starrybodies/reword/archive/refs/heads/main.zip)
from GitHub. In the desktop app, open Skills and follow the import or creation
options available to your account, supplying the ZIP or its extracted folder when
the interface accepts it. Then select Reword with `@` and ask it to build your
voice. Availability and permitted uploads depend on the surface and workspace.
A ZIP attached to an ordinary chat is not proof of a persistent installation.
If your interface has no supported skill installer, use the local Codex or Claude
Code setup above. Full Reword functionality also needs Python execution and
durable private file storage in the host.
Source: [OpenAI skill support and invocation](https://learn.chatgpt.com/docs/build-skills).

## Verify and try it

From the installed `reword` folder, run:

```bash
python3 scripts/reword.py --version
python3 scripts/reword.py voice onboard
python3 scripts/reword.py prompt draft.md --destination email
```

The first command prints the installed version. `draft.md` is a plain-text or
Markdown draft you supply. `prompt` returns a request for the host model; it does
not rewrite the file itself. On Windows, use your installed Python command if it
differs. Follow [the pilot guide](references/pilot.md) for a short real-use trial.

Installation references checked 2026-11-13. Host interfaces can change.
