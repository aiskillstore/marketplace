#!/bin/bash
# detect-context.sh - Intelligent context detection for validation strategy
# Part of code-validation-sandbox v3.0 (Reasoning-Activated)

set -euo pipefail

CHAPTER_PATH="${1:-.}"

# =============================================================================
# REASONING ACTIVATION: Context Analysis (not hardcoded rules)
# =============================================================================

# Layer Detection
# ---------------
# Question: What layer is this content?
# Reasoning: Analyze metadata, file structure, and content patterns

detect_layer() {
  local chapter_path=$1

  # Check for chapter metadata (explicit layer declaration)
  if [ -f "$chapter_path/chapter-meta.yaml" ]; then
    layer=$(grep "^layer:" "$chapter_path/chapter-meta.yaml" | cut -d: -f2 | tr -d ' ')
    if [ -n "$layer" ]; then
      echo "$layer"
      return
    fi
  fi

  # Reasoning-based detection from content patterns
  local content=$(find "$chapter_path" -name "*.md" -exec cat {} \;)

  # Layer 1 signals: "first time", "manual", "type this", "practice"
  if echo "$content" | grep -qi "first time\|manual\|type this\|practice without AI"; then
    echo "1"
    return
  fi

  # Layer 2 signals: "AI suggests", "optimize", "before/after", "convergence"
  if echo "$content" | grep -qi "AI suggests\|before.*after\|optimiz\|convergence\|collaborate"; then
    echo "2"
    return
  fi

  # Layer 3 signals: "reusable", "skill", "agent", "Persona.*Questions.*Principles"
  if echo "$content" | grep -qi "reusable\|create.*skill\|design.*agent\|Persona.*Questions.*Principles"; then
    echo "3"
    return
  fi

  # Layer 4 signals: "orchestrate", "integrate", "multi-agent", "system"
  if echo "$content" | grep -qi "orchestrat\|integrat\|multi-agent\|system.*component"; then
    echo "4"
    return
  fi

  # Default: Layer 1 (most conservative - full validation)
  echo "1"
}

# Language Detection
# ------------------
# Question: What language ecosystem?
# Reasoning: File extensions + keywords + manifest files

detect_language() {
  local chapter_path=$1
  local languages=()

  # Python detection
  if find "$chapter_path" -name "*.py" | grep -q .; then
    languages+=("python")
  elif grep -rq "import \|def \|class \|pip \|uv \|python" "$chapter_path"/*.md 2>/dev/null; then
    languages+=("python")
  fi

  # Node.js detection
  if [ -f "$chapter_path/package.json" ]; then
    languages+=("node")
  elif find "$chapter_path" -name "*.js" -o -name "*.ts" | grep -q .; then
    languages+=("node")
  elif grep -rq "npm \|pnpm \|require(\|import.*from\|node " "$chapter_path"/*.md 2>/dev/null; then
    languages+=("node")
  fi

  # Rust detection
  if [ -f "$chapter_path/Cargo.toml" ]; then
    languages+=("rust")
  elif find "$chapter_path" -name "*.rs" | grep -q .; then
    languages+=("rust")
  elif grep -rq "cargo \|rustc\|fn \|impl " "$chapter_path"/*.md 2>/dev/null; then
    languages+=("rust")
  fi

  # Go detection
  if [ -f "$chapter_path/go.mod" ]; then
    languages+=("go")
  elif find "$chapter_path" -name "*.go" | grep -q .; then
    languages+=("go")
  fi

  # Return comma-separated list
  if [ ${#languages[@]} -eq 0 ]; then
    echo "unknown"
  else
    IFS=,
    echo "${languages[*]}"
  fi
}

# Complexity Tier Detection (CEFR-aligned)
# -----------------------------------------
# Question: What's the target audience complexity?
# Reasoning: Check chapter-index.md or part number

detect_tier() {
  local chapter_path=$1

  # Extract part number from path (e.g., "04-Python-Fundamentals" → Part 4)
  if [[ $chapter_path =~ ([0-9]+)- ]]; then
    part_num=${BASH_REMATCH[1]}

    # Parts 1-3: A1-A2 (Aspiring/Beginner)
    if [ "$part_num" -le 3 ]; then
      echo "A2"
      return
    fi

    # Parts 4-5: B1-B2 (Intermediate)
    if [ "$part_num" -le 5 ]; then
      echo "B1"
      return
    fi

    # Parts 6-13: C1-C2 (Advanced/Professional)
    echo "C2"
    return
  fi

  # Default: B1 (intermediate)
  echo "B1"
}

# Validation Depth Decision
# --------------------------
# Question: How deep should validation go?
# Reasoning: Layer + Language + Tier → Validation strategy

determine_validation_depth() {
  local layer=$1
  local languages=$2
  local tier=$3

  case $layer in
    1)
      # Layer 1: CRITICAL depth (syntax + runtime + output matching)
      echo "CRITICAL"
      ;;
    2)
      # Layer 2: VERIFICATION depth (baseline + optimized + claims)
      echo "VERIFICATION"
      ;;
    3)
      # Layer 3: REUSABILITY depth (multi-scenario testing)
      echo "REUSABILITY"
      ;;
    4)
      # Layer 4: INTEGRATION depth (end-to-end testing)
      echo "INTEGRATION"
      ;;
    *)
      # Default: CRITICAL (most conservative)
      echo "CRITICAL"
      ;;
  esac
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
  local chapter_path="${1:-.}"

  echo "=== Context Detection (Reasoning-Based) ===" >&2
  echo >&2

  # Detect layer
  layer=$(detect_layer "$chapter_path")
  echo "Layer: $layer" >&2

  case $layer in
    1) echo "  → Manual Foundation (zero error tolerance)" >&2 ;;
    2) echo "  → AI Collaboration (verify claims)" >&2 ;;
    3) echo "  → Intelligence Design (test reusability)" >&2 ;;
    4) echo "  → Orchestration (integration testing)" >&2 ;;
  esac
  echo >&2

  # Detect language(s)
  languages=$(detect_language "$chapter_path")
  echo "Language(s): $languages" >&2

  IFS=',' read -ra LANGS <<< "$languages"
  for lang in "${LANGS[@]}"; do
    case $lang in
      python) echo "  → Python (AST + runtime validation)" >&2 ;;
      node) echo "  → Node.js (tsc + npm test)" >&2 ;;
      rust) echo "  → Rust (cargo check + test)" >&2 ;;
      go) echo "  → Go (go build + test)" >&2 ;;
      unknown) echo "  → Unknown (generic validation)" >&2 ;;
    esac
  done
  echo >&2

  # Detect tier
  tier=$(detect_tier "$chapter_path")
  echo "Tier: $tier" >&2

  case $tier in
    A2) echo "  → Aspiring/Beginner (heavy scaffolding)" >&2 ;;
    B1) echo "  → Intermediate (moderate guidance)" >&2 ;;
    C2) echo "  → Advanced/Professional (minimal scaffolding)" >&2 ;;
  esac
  echo >&2

  # Determine validation depth
  depth=$(determine_validation_depth "$layer" "$languages" "$tier")
  echo "Validation Depth: $depth" >&2

  case $depth in
    CRITICAL) echo "  → Syntax + Runtime + Output matching" >&2 ;;
    VERIFICATION) echo "  → Baseline + Optimized + Claims" >&2 ;;
    REUSABILITY) echo "  → Multi-scenario testing" >&2 ;;
    INTEGRATION) echo "  → End-to-end system validation" >&2 ;;
  esac
  echo >&2

  # Output machine-readable context (for validation scripts)
  cat <<EOF
LAYER=$layer
LANGUAGES=$languages
TIER=$tier
DEPTH=$depth
EOF
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  main "$@"
fi
