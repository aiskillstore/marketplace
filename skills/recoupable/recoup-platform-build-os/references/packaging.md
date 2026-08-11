# Packaging the workspace `plugin/` for Claude, Cursor, and Codex

The workspace's `plugin/` directory is the source of truth for skills. Build it once, then expose it
through the install/discovery surfaces each agent expects.

## Naming
Default the plugin name to `{DOMAIN_SLUG}-os` (kebab-case). Use the user's explicit name only if they give
one. The workspace folder stays `plugin/` to keep the root taxonomy simple; the packaged artifact and
both manifest `"name"` fields use `{DOMAIN_SLUG}-os`.

- `DOMAIN_SLUG`: lowercase kebab-case domain label (`product`, `record-label`, `research`).
- `DOMAIN_TITLE`: human title case label for UI text (`Product`, `Record Label`, `Research`).

## Multi-agent layout
```
{workspace}/
├── AGENTS.md                 # symlink -> CLAUDE.md
├── .agents/
│   └── skills -> ../plugin/skills
│
└── plugin/
    ├── .claude-plugin/
    │   └── plugin.json       # Claude plugin manifest
    ├── .codex-plugin/
    │   └── plugin.json       # Codex plugin manifest
    ├── skills/
    │   └── {skill}/SKILL.md  # one folder per skill
    └── README.md
```

Use `.agents/skills` as the repo-discovery adapter because both Cursor and Codex discover project
skills there. Do **not** also create `.cursor/skills` by default; Cursor also reads `.agents/skills`,
and creating both surfaces can show duplicates. Only add `.cursor/skills` if the user explicitly wants
a Cursor-only mirror.

Prefer a symlink so `plugin/skills` remains the single source of truth:
```bash
mkdir -p {workspace}/.agents
ln -s ../plugin/skills {workspace}/.agents/skills
```
If directory symlinks are unavailable, copy `plugin/skills/` into `.agents/skills/` and record that it
is a compatibility mirror that must be refreshed after skill changes.

## Claude manifest
Write `plugin/.claude-plugin/plugin.json` from `assets/claude-plugin.json.tmpl`:
```json
{
  "name": "{DOMAIN_SLUG}-os",
  "version": "0.1.0",
  "description": "Operating system for {DOMAIN_TITLE} — skills for intake, maintenance, learning, and repeatable work.",
  "author": { "name": "{author}" },
  "keywords": ["{DOMAIN_SLUG}", "workspace-os", "skills"]
}
```

## Codex manifest
Write `plugin/.codex-plugin/plugin.json` from `assets/codex-plugin.json.tmpl`:
```json
{
  "name": "{DOMAIN_SLUG}-os",
  "version": "0.1.0",
  "description": "Operating system for {DOMAIN_TITLE} — skills for intake, maintenance, learning, and repeatable work.",
  "author": { "name": "{author}" },
  "keywords": ["{DOMAIN_SLUG}", "workspace-os", "skills"],
  "skills": "./skills/",
  "interface": {
    "displayName": "{DOMAIN_TITLE} OS",
    "shortDescription": "Workspace operating system for {DOMAIN_TITLE}.",
    "longDescription": "A workspace operating system with skills for intake, maintenance, compound learning, and promoting repeatable work into durable capabilities.",
    "developerName": "{author}",
    "category": "Productivity",
    "capabilities": ["Skills"],
    "defaultPrompt": "Use {DOMAIN_SLUG}-os to organize this workspace and run the right workflow."
  }
}
```

Paths in the Codex manifest are relative to `plugin/` and must begin with `./`.

## Validate BEFORE zipping
1. Both manifests exist:
   - `plugin/.claude-plugin/plugin.json`
   - `plugin/.codex-plugin/plugin.json`
2. Both manifests are valid JSON and share the same kebab-case `"name"` (`{DOMAIN_SLUG}-os` by default).
3. The Codex manifest includes `"skills": "./skills/"`.
4. Every `plugin/skills/*/` folder contains a `SKILL.md` with valid frontmatter (`name` + `description`).
5. No `<` or `>` in any skill `description` (some loaders reject XML-looking tags).
6. No stray non-skill folders inside `plugin/skills/`.
7. `.agents/skills` points to or mirrors `plugin/skills`.

A quick validator:
```bash
python3 - <<'PY'
import json, glob, os, re, sys
plg = "{workspace}/plugin"
claude = json.load(open(f"{plg}/.claude-plugin/plugin.json"))
codex = json.load(open(f"{plg}/.codex-plugin/plugin.json"))
assert claude["name"] == codex["name"], "manifest names differ"
assert re.fullmatch(r"[a-z0-9-]+", claude["name"]), "name not kebab-case"
assert codex.get("skills") == "./skills/", "Codex skills path must be ./skills/"
bad = []
for sk in glob.glob(f"{plg}/skills/*/SKILL.md"):
    text = open(sk).read()
    fm = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not fm:
        bad.append(f"{sk}: missing frontmatter")
        continue
    name = re.search(r"^name:\s*(.+)$", fm.group(1), re.M)
    desc = re.search(r"^description:\s*(.+)$", fm.group(1), re.M)
    if not name or not desc:
        bad.append(f"{sk}: missing name/description")
    elif "<" in desc.group(1) or ">" in desc.group(1):
        bad.append(f"{sk}: angle bracket in description")
adapter = "{workspace}/.agents/skills"
assert os.path.exists(adapter), ".agents/skills adapter missing"
print("FAIL" if bad else "OK", *bad)
sys.exit(1 if bad else 0)
PY
```

## Package + deliver
Zip the **contents** of `plugin/` (so `.claude-plugin/` and `.codex-plugin/` sit at the zip root) into
`/tmp` first, then copy to the outputs folder:
```bash
cd {workspace}/plugin && zip -rq /tmp/{DOMAIN_SLUG}-os.plugin . -x "*.DS_Store"
cp /tmp/{DOMAIN_SLUG}-os.plugin {OUTPUTS}/{DOMAIN_SLUG}-os.plugin
```

Claude and Codex install from the plugin manifests. Cursor and Codex can also use the checked-in
project skills directly through `.agents/skills`.

## Keep the package fresh (the artifact is transient, not taxonomy)
The packaged `{DOMAIN_SLUG}-os.plugin` is a **release artifact, not a workspace folder**. Never create
an `outputs/` (or similar) top-level directory for it inside the workspace — that would trip the
doctor's root-hygiene check. Zip to `/tmp` and deliver to the external outputs location.

Because `plugin/skills/` is the source of truth, the package goes **stale** the moment a skill or
manifest changes in place — e.g. when `{DOMAIN}-skillify` publishes a skill or the janitor reconciles
one. After any such change, re-zip and record the packaged version so the doctor can verify freshness:
```bash
cd {workspace}/plugin && zip -rq /tmp/{DOMAIN_SLUG}-os.plugin . -x "*.DS_Store"
cp /tmp/{DOMAIN_SLUG}-os.plugin {OUTPUTS}/{DOMAIN_SLUG}-os.plugin
python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])" > {workspace}/operations/.packaged-version
```
The `{DOMAIN}-janitor` and `{DOMAIN}-skillify` skills own this step; `{DOMAIN}-doctor` only reports when
the stamp and the manifest version disagree (its package-freshness check).

## AGENTS.md
In the target workspace, symlink so any agent runner finds the same brain:
```bash
cd {workspace} && ln -s CLAUDE.md AGENTS.md
```
If symlinks are not supported, write an `AGENTS.md` that says "See CLAUDE.md".
