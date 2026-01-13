# AllayMC Plugin Dev Skill ⚙️

Build, update, and troubleshoot AllayMC plugins with a ready-to-use skill bundle. 🚀

## Install 🧩

Clone this repository into your agent's skills directory and initialize submodules:

```bash
cd <skills-dir>
git clone --recurse-submodules git@github.com:AllayMC/AllaySkill.git allaymc-plugin-dev
```

- For Claude Code, `<skills-dir>` is `C:/Users/<your-username>/skills`.
- For OpenAI Codex, `<skills-dir>` is `C:/Users/<your-username>/.codex/skills/.system`.

If you already cloned it without submodules:

```bash
git submodule update --init --recursive
```

## Update 🔄

Pull the latest changes and refresh submodules:

```bash
git pull --recurse-submodules
```

If submodules are out of date:

```bash
git submodule update --init --recursive
```

## Use ✅

Invoke the skill by name or ask for AllayMC plugin development tasks:

Examples:
- "Use allaymc-plugin-dev to create a new AllayMC plugin skeleton."
- "Help me add commands and events to my AllayMC plugin."

## What's Inside 📦

- `SKILL.md`: The skill definition and workflow guidance.
- `references/Allay`: AllayMC source and docs (submodule).
- `references/AllayGradle`: Official AllayGradle plugin source (submodule).
- `references/JavaPluginTemplate`: Official Java template (submodule).

The skill reads AllayMC sources and the official Java plugin template via submodules under `references/`.
