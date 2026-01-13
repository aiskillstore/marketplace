#!/bin/bash
# validate.sh - Main validation orchestrator
# Part of code-validation-sandbox v3.0 (Reasoning-Activated)

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Usage
usage() {
  cat <<EOF
Usage: $0 <chapter-path> [options]

Intelligent code validation with automatic context detection.

Arguments:
  chapter-path    Path to chapter directory to validate

Options:
  --output DIR    Output directory for reports (default: validation-output)
  --layer N       Force layer (1-4), skip auto-detection
  --language L    Force language (python|node|rust), skip auto-detection
  --verbose       Show detailed validation process
  --help          Show this help message

Examples:
  # Auto-detect everything
  $0 apps/learn-app/docs/04-Python-Fundamentals/14-data-types

  # Force Layer 1 validation
  $0 apps/learn-app/docs/04-Python-Fundamentals/14-data-types --layer 1

  # Verbose output
  $0 apps/learn-app/docs/04-Python-Fundamentals/14-data-types --verbose

Exit codes:
  0 - All validations passed
  1 - Validation errors found (see report)
  2 - Critical errors (blocks publication)
  3 - Invalid arguments
EOF
}

# Parse arguments
CHAPTER_PATH=""
OUTPUT_DIR="validation-output"
FORCE_LAYER=""
FORCE_LANGUAGE=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --layer)
      FORCE_LAYER="$2"
      shift 2
      ;;
    --language)
      FORCE_LANGUAGE="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      if [ -z "$CHAPTER_PATH" ]; then
        CHAPTER_PATH="$1"
      else
        echo "Error: Unknown argument: $1" >&2
        usage >&2
        exit 3
      fi
      shift
      ;;
  esac
done

# Validate arguments
if [ -z "$CHAPTER_PATH" ]; then
  echo "Error: chapter-path required" >&2
  usage >&2
  exit 3
fi

if [ ! -d "$CHAPTER_PATH" ]; then
  echo "Error: Chapter path not found: $CHAPTER_PATH" >&2
  exit 3
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# =============================================================================
# REASONING ACTIVATION: Context Detection
# =============================================================================

echo "=== Code Validation Sandbox v3.0 (Reasoning-Activated) ===" >&2
echo >&2

if $VERBOSE; then
  echo "Chapter: $CHAPTER_PATH" >&2
  echo "Output: $OUTPUT_DIR" >&2
  echo >&2
fi

# Detect context (layer, language, tier, depth)
if $VERBOSE; then
  context_output=$("$SCRIPT_DIR/detect-context.sh" "$CHAPTER_PATH" 2>&1)
  echo "$context_output" >&2
  context_vars=$(echo "$context_output" | tail -4)
else
  context_vars=$("$SCRIPT_DIR/detect-context.sh" "$CHAPTER_PATH" 2>/dev/null)
fi

# Parse context variables
eval "$context_vars"

# Override with forced values
if [ -n "$FORCE_LAYER" ]; then
  LAYER="$FORCE_LAYER"
  echo "Layer forced to: $LAYER" >&2
fi

if [ -n "$FORCE_LANGUAGE" ]; then
  LANGUAGES="$FORCE_LANGUAGE"
  echo "Language forced to: $LANGUAGES" >&2
fi

# =============================================================================
# REASONING ACTIVATION: Validation Strategy Selection
# =============================================================================

select_validation_strategy() {
  local layer=$1
  local languages=$2
  local depth=$3

  echo "=== Validation Strategy Selection ===" >&2
  echo >&2

  case $depth in
    CRITICAL)
      echo "Strategy: CRITICAL DEPTH" >&2
      echo "  - Syntax: 100% correct (zero tolerance)" >&2
      echo "  - Runtime: Must execute without errors" >&2
      echo "  - Output: Must match expected (if documented)" >&2
      echo "  - Why: Layer 1 foundation - students type manually" >&2
      ;;
    VERIFICATION)
      echo "Strategy: VERIFICATION DEPTH" >&2
      echo "  - Baseline: Manual implementation must work" >&2
      echo "  - Optimized: AI-suggested version must work" >&2
      echo "  - Equivalence: Both produce same results" >&2
      echo "  - Claims: Performance improvements verified" >&2
      echo "  - Why: Layer 2 collaboration - accuracy critical" >&2
      ;;
    REUSABILITY)
      echo "Strategy: REUSABILITY DEPTH" >&2
      echo "  - Multi-scenario: Test with 3+ use cases" >&2
      echo "  - Parameterization: Test with different inputs" >&2
      echo "  - Pattern: Persona+Questions+Principles present" >&2
      echo "  - Why: Layer 3 intelligence - must generalize" >&2
      ;;
    INTEGRATION)
      echo "Strategy: INTEGRATION DEPTH" >&2
      echo "  - Component startup: All services healthy" >&2
      echo "  - Communication: APIs/messages working" >&2
      echo "  - End-to-end: User scenarios complete" >&2
      echo "  - Recovery: Graceful degradation on failures" >&2
      echo "  - Why: Layer 4 orchestration - production-ready" >&2
      ;;
  esac
  echo >&2
}

select_validation_strategy "$LAYER" "$LANGUAGES" "$DEPTH"

# =============================================================================
# REASONING ACTIVATION: Language-Specific Validation
# =============================================================================

validate_language() {
  local lang=$1
  local chapter_path=$2
  local output_dir=$3

  case $lang in
    python)
      if [ -f "$SCRIPT_DIR/validate-python.sh" ]; then
        "$SCRIPT_DIR/validate-python.sh" "$chapter_path" "$output_dir" "$LAYER" "$DEPTH"
      else
        echo "WARNING: validate-python.sh not found, skipping Python validation" >&2
        return 1
      fi
      ;;
    node)
      if [ -f "$SCRIPT_DIR/validate-node.sh" ]; then
        "$SCRIPT_DIR/validate-node.sh" "$chapter_path" "$output_dir" "$LAYER" "$DEPTH"
      else
        echo "WARNING: validate-node.sh not found, skipping Node validation" >&2
        return 1
      fi
      ;;
    rust)
      if [ -f "$SCRIPT_DIR/validate-rust.sh" ]; then
        "$SCRIPT_DIR/validate-rust.sh" "$chapter_path" "$output_dir" "$LAYER" "$DEPTH"
      else
        echo "WARNING: validate-rust.sh not found, skipping Rust validation" >&2
        return 1
      fi
      ;;
    unknown)
      echo "WARNING: Unknown language, using generic validation" >&2
      # Generic validation - check markdown code blocks exist
      if ! find "$chapter_path" -name "*.md" -exec grep -l '```' {} \; | grep -q .; then
        echo "ERROR: No code blocks found in markdown files" >&2
        return 2
      fi
      echo "INFO: Markdown code blocks found, manual review recommended" >&2
      return 0
      ;;
    *)
      echo "ERROR: Unsupported language: $lang" >&2
      return 1
      ;;
  esac
}

# Validate each detected language
IFS=',' read -ra LANGS <<< "$LANGUAGES"
validation_failed=false
critical_errors=false

for lang in "${LANGS[@]}"; do
  echo "=== Validating $lang ===" >&2
  echo >&2

  if ! validate_language "$lang" "$CHAPTER_PATH" "$OUTPUT_DIR"; then
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
      critical_errors=true
    fi
    validation_failed=true
  fi

  echo >&2
done

# =============================================================================
# Exit with appropriate code
# =============================================================================

if $critical_errors; then
  echo "❌ CRITICAL ERRORS FOUND - Publication blocked" >&2
  echo "See reports in: $OUTPUT_DIR" >&2
  exit 2
elif $validation_failed; then
  echo "⚠️  Validation errors found" >&2
  echo "See reports in: $OUTPUT_DIR" >&2
  exit 1
else
  echo "✅ All validations passed" >&2
  exit 0
fi
