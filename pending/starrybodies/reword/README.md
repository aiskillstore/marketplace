# Reword

Reword is an open-source agent skill for Claude Code and Codex that learns your writing voice. Give it writing you choose, and it builds a compact voice profile your agent uses to draft and edit in your writing style. It fits the destination, such as an email, a message, a LinkedIn post, or a cover letter, and it can learn from your revisions and stated preferences when you opt in.

[Installation](INSTALL.md) · [Commands](references/cli.md) · [Website](https://reword.symbai.studio/)

## Install

Clone the repository into your agent's skills folder. It works with a host agent that can read skill files, run **Python 3.10+**, and save private files. The helpers use only the Python standard library. Your agent's model performs the writing and voice distillation; Reword does not train a model or call a separate writing service.

| Host | Install | Invoke |
| --- | --- | --- |
| Claude Code | `git clone https://github.com/starrybodies/reword ~/.claude/skills/reword` | `/reword Build my voice` |
| Codex CLI or IDE | `git clone https://github.com/starrybodies/reword ~/.agents/skills/reword` | `$reword Build my voice` |
| ChatGPT with supported skills | Import the [repository ZIP](https://github.com/starrybodies/reword/archive/refs/heads/main.zip) through Skills | Select Reword with `@` |

Run `git pull` in that folder to update. The [skills CLI](https://skills.sh/) also works: `npx skills add starrybodies/reword`. See [INSTALL.md](INSTALL.md) for setup details and host limitations.

## Use it

Start with one to five pieces you wrote and deliberately choose to share:

> Build my voice from these three samples. Keep it in a private collection. Ask before enabling ongoing learning.

Then give it a draft or a factual brief and a destination:

> Rewrite this email using my saved voice. Put the request first and keep the dates and commitments unchanged.

> Draft a LinkedIn post from these notes using my saved voice. Use only the facts in the notes.

With your consent, later corrections can improve the guide. You can inspect, export, pause learning, forget evidence, or restore an earlier guide. [Voice collections](references/voice-collection.md) explains those controls.

Your samples and voice collection stay in the private location you choose, outside the skill and public repositories. Your host's usual model processing and data rules still apply. Keep reference inspiration separate from your authored work; sample facts are never facts for a new draft.

## Local tools

From this folder:

```bash
python3 scripts/reword.py --version
python3 scripts/reword.py prompt draft.md --destination email
python3 scripts/reword.py check original.md candidate.md --destination email
```

`prompt` assembles a request for your host model; it does not rewrite the file. `check` flags possible changes to protected content and claims. These checks are heuristics, so review the result against the source.

## Help build it

If Reword is useful, **star this repository**. **Fork it** to try a change, open an issue with a synthetic example, or send a pull request. [CONTRIBUTING.md](CONTRIBUTING.md) covers the small test suite and contribution workflow.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

The tests cover local runtime behavior, consent, persistence, bounded guidance, and content checks. They do not measure writing quality or voice fidelity.

Made by [Symbai Studios](https://symbai.studio/). Released under the [MIT license](LICENSE).
