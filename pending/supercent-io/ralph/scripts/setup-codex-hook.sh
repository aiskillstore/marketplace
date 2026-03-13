#!/usr/bin/env bash
# ralph (Ouroboros) - Codex CLI setup helper
# Configures Codex for the full Ouroboros specification-first workflow:
#
#  1) developer_instructions  → ~/.codex/config.toml  (ooo command contract)
#  2) ~/.codex/prompts/ralph.md       (load via /prompts:ralph)
#  3) ~/.codex/prompts/ouroboros.md   (load via /prompts:ouroboros)
#
# Usage:
#   bash setup-codex-hook.sh [--dry-run]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m'

DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    -h|--help)
      echo "Usage: $0 [--dry-run]"
      echo ""
      echo "Configures Codex for Ouroboros / ralph loop workflows:"
      echo "  1. Adds ooo command contract to ~/.codex/config.toml developer_instructions"
      echo "  2. Creates ~/.codex/prompts/ralph.md for /prompts:ralph"
      echo "  3. Creates ~/.codex/prompts/ouroboros.md for /prompts:ouroboros"
      echo ""
      echo "Options:"
      echo "  --dry-run  Show what would change without writing"
      echo "  -h, --help Show this help"
      exit 0
      ;;
    *) ;;
  esac
done

CODEX_DIR="$HOME/.codex"
CODEX_CONFIG="$CODEX_DIR/config.toml"
CODEX_PROMPTS="$CODEX_DIR/prompts"
RALPH_PROMPT="$CODEX_PROMPTS/ralph.md"
OUROBOROS_PROMPT="$CODEX_PROMPTS/ouroboros.md"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Ouroboros × Codex setup                      ║${NC}"
echo -e "${BLUE}║  Stop prompting. Start specifying.             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

if ! command -v codex &>/dev/null; then
  echo -e "${YELLOW}⚠ codex CLI not found in PATH${NC}"
  echo -e "${GRAY}  Install via: npm install -g @openai/codex${NC}"
  echo -e "${GRAY}  Continuing setup anyway (config and prompts will be prepared).${NC}"
  echo ""
fi

mkdir -p "$CODEX_DIR" "$CODEX_PROMPTS"

# ── developer_instructions content ──────────────────────────────────────────
OOO_INSTRUCTION='Ouroboros specification-first workflow is active. ooo command contract:

COMMANDS:
  ooo interview [topic]   - Socratic questioning until Ambiguity<=0.2
  ooo seed                - Crystallize into immutable YAML spec
  ooo run [seed.yaml]     - Execute via Double Diamond
  ooo evaluate <id>       - 3-stage gate: Mechanical->Semantic->Consensus
  ooo evolve [topic]      - Evolutionary loop until Similarity>=0.95
  ooo unstuck [persona]   - Lateral thinking (simplifier|hacker|contrarian|researcher|architect)
  ooo status [id]         - Drift check (threshold<=0.3)
  ooo ralph "task"        - Persistent loop until verified

RALPH LOOP CONTRACT:
  When user runs /ralph or "ooo ralph":
  1) Treat `/ralph "<task>" [--completion-promise=TEXT] [--max-iterations=N]` as a contract.
  2) Keep original task unchanged across retries.
  3) Parse completion signal: <promise>VALUE</promise>
  4) If promise missing and iteration < max-iterations: continue immediately.
  5) If promise found or max-iterations reached: finish with status report.
  6) Save state to .omc/state/ralph-state.json each iteration.
  7) Report format: [Ralph Iteration i/max] Verification: PASSED/FAILED Score: 0.0-1.0
  Default promise: DONE. Default max: 10. The boulder never stops.'

# ── Step 1: Config.toml developer_instructions ──────────────────────────────
echo -e "${BLUE}Step 1: Config.toml developer_instructions${NC}"
if [ -f "$CODEX_CONFIG" ] && grep -q "ouroboros\|ooo interview\|ralph loop" "$CODEX_CONFIG" 2>/dev/null; then
  echo -e "${YELLOW}⚠ developer_instructions already contains Ouroboros reference${NC}"
  echo -e "${GRAY}  No changes made to config.toml.${NC}"
else
  if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN] Would add Ouroboros ooo contract to developer_instructions in ${CODEX_CONFIG}${NC}"
  else
    if [ -f "$CODEX_CONFIG" ] && grep -q "^developer_instructions" "$CODEX_CONFIG"; then
      if command -v python3 &>/dev/null; then
        python3 - "$CODEX_CONFIG" "$OOO_INSTRUCTION" <<'PYEOF'
import sys
import re

path, addition = sys.argv[1], sys.argv[2]

def escape_toml_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')

with open(path) as f:
    content = f.read()

pattern = re.compile(r'^(developer_instructions\s*=\s*")(.+?)(")', re.MULTILINE | re.DOTALL)
match = pattern.search(content)

if match:
    current = match.group(2)
    if "ouroboros" not in current and "ooo interview" not in current:
        new_val = current + " " + addition
        content = content[:match.start()] + f'developer_instructions = "{escape_toml_value(new_val)}"' + content[match.end():]
        with open(path, "w") as out:
            out.write(content)
        print("Updated existing developer_instructions.")
    else:
        print("developer_instructions already includes Ouroboros contract.")
else:
    with open(path, "a") as out:
        out.write('\ndeveloper_instructions = "{}"\n'.format(escape_toml_value(addition)))
    print("Added developer_instructions line.")
PYEOF
      else
        echo -e "${YELLOW}⚠ python3 not found. Appending developer_instructions.${NC}"
        printf '\ndeveloper_instructions = "%s"\n' "$OOO_INSTRUCTION" >> "$CODEX_CONFIG"
      fi
    else
      # New or empty config — write fresh
      if [ -f "$CODEX_CONFIG" ]; then
        python3 -c "
import sys, re
path = sys.argv[1]
addition = sys.argv[2]
def escape(v): return v.replace('\\\\', '\\\\\\\\').replace('\"', '\\\\\"')
with open(path, 'a') as f:
    f.write('\ndeveloper_instructions = \"{}\"\\n'.format(escape(addition)))
print('Appended developer_instructions.')
" "$CODEX_CONFIG" "$OOO_INSTRUCTION" 2>/dev/null || printf '\ndeveloper_instructions = "%s"\n' "$OOO_INSTRUCTION" >> "$CODEX_CONFIG"
      else
        printf 'developer_instructions = "%s"\n' "$OOO_INSTRUCTION" > "$CODEX_CONFIG"
      fi
    fi
    echo -e "${GREEN}✓ Updated ${CODEX_CONFIG}${NC}"
  fi
fi

# ── Step 2: ralph prompt file ────────────────────────────────────────────────
echo ""
echo -e "${BLUE}Step 2: ralph prompt file (${RALPH_PROMPT})${NC}"

RALPH_CONTENT='# ralph — Ouroboros Completion Loop

The boulder never stops. This prompt configures Codex for ralph loop execution.

## Loop Contract

1. Parse `/ralph "<task>" [--completion-promise=TEXT] [--max-iterations=N]`
2. Completion promise detected as: `<promise>VALUE</promise>` in output
3. If not found and iteration < max_iterations → continue immediately with same task
4. Default promise: `DONE` | Default max iterations: `10`

## State File

Create `.omc/state/ralph-state.json` at loop start:
```json
{
  "mode": "ralph",
  "session_id": "<uuid>",
  "request": "<user request>",
  "status": "running",
  "iteration": 0,
  "max_iterations": 10,
  "last_checkpoint": null,
  "verification_history": []
}
```

## Progress Report Format

```
[Ralph Iteration i/max]
Execution complete. Verifying...

Verification: FAILED/PASSED
Score: 0.0-1.0
Issues: <list>

The boulder never stops. Continuing...
```

When complete:
```
<promise>DONE</promise>

Ralph COMPLETE
==============
Request: <original request>
Duration: <time>
Iterations: <count>
```

## Quick Reference

| Action | Command |
|--------|---------|
| Start loop | `/ralph "task"` or `ooo ralph "task"` |
| Custom promise | `--completion-promise=TEXT` |
| Iteration cap | `--max-iterations=N` |
| Cancel | `/ralph:cancel` |
| Resume | `ralph continue` |

## Ouroboros ooo Commands

For full specification-first workflow, use:
```
ooo interview "topic"   → Socratic interview
ooo seed                → Generate spec (Ambiguity≤0.2)
ooo run [seed.yaml]     → Execute spec
ooo evaluate <id>       → 3-stage verification
ooo evolve "topic"      → Evolutionary loop
ooo unstuck             → Lateral thinking
ooo ralph "task"        → Persistent loop
```

See /prompts:ouroboros for the complete Ouroboros reference.
'

if [ -f "$RALPH_PROMPT" ]; then
  echo -e "${YELLOW}⚠ ${RALPH_PROMPT} already exists — overwriting with Ouroboros version${NC}"
fi
if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}[DRY RUN] Would create/update ${RALPH_PROMPT}${NC}"
else
  printf '%s\n' "$RALPH_CONTENT" > "$RALPH_PROMPT"
  echo -e "${GREEN}✓ Created ${RALPH_PROMPT}${NC}"
fi

# ── Step 3: ouroboros prompt file ────────────────────────────────────────────
echo ""
echo -e "${BLUE}Step 3: ouroboros prompt file (${OUROBOROS_PROMPT})${NC}"

OUROBOROS_CONTENT='# Ouroboros — Specification-First AI Development

> Stop prompting. Start specifying.
> The serpent does not repeat — it evolves.

Most AI coding fails at the INPUT, not the output.
Ouroboros fixes this by exposing hidden assumptions BEFORE any code is written.

## The Loop

```
Interview → Seed → Execute → Evaluate
    ↑                           ↓
    └──── Evolutionary Loop ────┘
```

## Commands

| Command | What It Does |
|---------|--------------|
| `ooo interview "topic"` | Socratic questioning → Ambiguity≤0.2 |
| `ooo seed` | Crystallize into immutable YAML spec |
| `ooo run [seed.yaml]` | Execute via Double Diamond |
| `ooo evaluate <id>` | 3-stage: Mechanical→Semantic→Consensus |
| `ooo evolve "topic"` | Evolutionary loop → Similarity≥0.95 |
| `ooo unstuck [persona]` | Lateral thinking when blocked |
| `ooo status [id]` | Drift check (Goal 50%+Constraint 30%+Ontology 20%) |
| `ooo ralph "task"` | Persistent loop until verified |

## Ambiguity Gate

```
Ambiguity = 1 − Σ(clarityᵢ × weightᵢ)
Greenfield: Goal(40%) + Constraint(30%) + Success(30%)
Brownfield: Goal(35%) + Constraint(25%) + Success(25%) + Context(15%)
Threshold: ≤ 0.2 → ready for Seed
```

## Convergence Gate

```
Similarity = 0.5×name_overlap + 0.3×type_match + 0.2×exact_match
Threshold: ≥ 0.95 → CONVERGED → Ralph stops
```

## Nine Minds (Loaded On-Demand)

| Agent | Core Question |
|-------|--------------|
| Socratic Interviewer | "What are you assuming?" |
| Ontologist | "What IS this, really?" |
| Seed Architect | "Is this complete and unambiguous?" |
| Evaluator | "Did we build the right thing?" |
| Contrarian | "What if the opposite were true?" |
| Hacker | "What constraints are actually real?" |
| Simplifier | "What is the simplest thing that could work?" |
| Researcher | "What evidence do we actually have?" |
| Architect | "If we started over, would we build it this way?" |

## Unstuck Personas

- `simplifier` — cut scope to MVP first
- `hacker` — make it work, elegance later
- `contrarian` — challenge all assumptions
- `researcher` — stop coding, find missing information
- `architect` — restructure the approach entirely

## Ralph Cancellation

- Save checkpoint: `/ouroboros:cancel` or `/ralph:cancel`
- Force clear: `/ouroboros:cancel --force`
- Resume: `ooo ralph continue`

Source: https://github.com/Q00/ouroboros — MIT License
'

if [ -f "$OUROBOROS_PROMPT" ]; then
  echo -e "${YELLOW}⚠ ${OUROBOROS_PROMPT} already exists — overwriting${NC}"
fi
if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}[DRY RUN] Would create/update ${OUROBOROS_PROMPT}${NC}"
else
  printf '%s\n' "$OUROBOROS_CONTENT" > "$OUROBOROS_PROMPT"
  echo -e "${GREEN}✓ Created ${OUROBOROS_PROMPT}${NC}"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}Ouroboros × Codex setup complete.${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Restart Codex session"
echo -e "  2. Load ralph context:     ${GREEN}/prompts:ralph${NC}"
echo -e "  3. Load full context:      ${GREEN}/prompts:ouroboros${NC}"
echo -e "  4. Start specification:    ${GREEN}ooo interview \"your idea\"${NC}"
echo -e "  5. Start persistent loop:  ${GREEN}ooo ralph \"your task\" --max-iterations=10${NC}"
echo ""
echo -e "${GRAY}Note: Codex CLI has no native AfterAgent hooks.${NC}"
echo -e "${GRAY}Ralph loop relies on conversation-level promise detection.${NC}"
echo -e "${GRAY}Use --max-iterations=N as a safety net.${NC}"
echo ""
