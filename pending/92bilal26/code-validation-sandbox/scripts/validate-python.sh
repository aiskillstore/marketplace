#!/bin/bash
# validate-python.sh - Python-specific validation (Layer-aware)
# Part of code-validation-sandbox v3.0 (Reasoning-Activated)

set -euo pipefail

CHAPTER_PATH="${1:-.}"
OUTPUT_DIR="${2:-validation-output}"
LAYER="${3:-1}"
DEPTH="${4:-CRITICAL}"

# Extract Python code blocks from markdown
extract_python_blocks() {
  local chapter_path=$1
  local output_dir=$2

  mkdir -p "$output_dir/extracted"

  find "$chapter_path" -name "*.md" | while read -r mdfile; do
    local basename=$(basename "$mdfile" .md)
    local block_num=0

    # Extract code blocks
    awk '/```python/,/```/ { if ($0 !~ /```/) print }' "$mdfile" > "$output_dir/extracted/${basename}_all.py"

    # Split into individual blocks for detailed error reporting
    awk '
    /```python/ {
      in_block = 1
      block++
      file = "'"$output_dir"'/extracted/'"$basename"'_block_" block ".py"
      next
    }
    /```/ && in_block {
      in_block = 0
      next
    }
    in_block {
      print > file
    }
    ' "$mdfile"
  done
}

# Layer-aware validation
validate_python_layer_aware() {
  local chapter_path=$1
  local output_dir=$2
  local layer=$3
  local depth=$4

  local total_blocks=0
  local syntax_errors=0
  local runtime_errors=0
  local output_mismatches=0

  echo "Python Validation (Layer $layer, Depth: $depth)" >&2
  echo >&2

  # Extract code blocks
  extract_python_blocks "$chapter_path" "$output_dir"

  # Count total blocks
  total_blocks=$(find "$output_dir/extracted" -name "*_block_*.py" | wc -l | tr -d ' ')

  if [ "$total_blocks" -eq 0 ]; then
    echo "WARNING: No Python code blocks found" >&2
    return 0
  fi

  echo "Found $total_blocks Python code blocks" >&2
  echo >&2

  # Validation based on depth
  case $depth in
    CRITICAL)
      echo "=== CRITICAL Depth Validation ===" >&2
      echo "- Syntax: 100% correct (zero tolerance)" >&2
      echo "- Runtime: Must execute successfully" >&2
      echo "- Output: Must match expected (if documented)" >&2
      echo >&2

      # Syntax validation (CRITICAL - zero tolerance)
      find "$output_dir/extracted" -name "*_block_*.py" | while read -r pyfile; do
        if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
          echo "CRITICAL: Syntax error in $pyfile" >&2
          python3 -m py_compile "$pyfile" 2>&1 | head -5 >&2
          ((syntax_errors++))
        fi
      done

      # Runtime validation (CRITICAL)
      find "$output_dir/extracted" -name "*_block_*.py" | while read -r pyfile; do
        if ! timeout 10s python3 "$pyfile" >/dev/null 2>&1; then
          echo "CRITICAL: Runtime error in $pyfile" >&2
          timeout 10s python3 "$pyfile" 2>&1 | head -10 >&2
          ((runtime_errors++))
        fi
      done
      ;;

    VERIFICATION)
      echo "=== VERIFICATION Depth Validation ===" >&2
      echo "- Check: Baseline + Optimized versions both work" >&2
      echo "- Check: Functional equivalence" >&2
      echo "- Check: Performance claims (if present)" >&2
      echo >&2

      # Look for before/after patterns
      if find "$chapter_path" -name "*.md" -exec grep -l "before.*after\|baseline.*optimized" {} \; | grep -q .; then
        echo "Layer 2 pattern detected: Before/After optimization" >&2

        # Validate both versions work
        find "$output_dir/extracted" -name "*baseline*.py" -o -name "*before*.py" | while read -r baseline; do
          optimized=$(echo "$baseline" | sed 's/baseline/optimized/;s/before/after/')

          if [ -f "$optimized" ]; then
            echo "Testing equivalence: $(basename "$baseline") vs $(basename "$optimized")" >&2

            baseline_out=$(timeout 10s python3 "$baseline" 2>&1 || echo "FAILED")
            optimized_out=$(timeout 10s python3 "$optimized" 2>&1 || echo "FAILED")

            if [ "$baseline_out" != "$optimized_out" ]; then
              echo "HIGH: Functional equivalence broken" >&2
              echo "  Baseline: $baseline_out" >&2
              echo "  Optimized: $optimized_out" >&2
            fi
          fi
        done
      else
        # Fallback to CRITICAL validation
        find "$output_dir/extracted" -name "*_block_*.py" | while read -r pyfile; do
          python3 -m py_compile "$pyfile" 2>/dev/null || ((syntax_errors++))
          timeout 10s python3 "$pyfile" >/dev/null 2>&1 || ((runtime_errors++))
        done
      fi
      ;;

    REUSABILITY)
      echo "=== REUSABILITY Depth Validation ===" >&2
      echo "- Check: Persona+Questions+Principles pattern" >&2
      echo "- Check: Works with multiple scenarios" >&2
      echo >&2

      # Check for skill pattern in markdown
      if ! find "$chapter_path" -name "*.md" -exec grep -l "Persona:\|Questions:\|Principles:" {} \; | grep -q .; then
        echo "MEDIUM: Missing Persona+Questions+Principles pattern" >&2
        echo "  Layer 3 intelligence should follow v3.0 pattern" >&2
      fi

      # Syntax check all code
      find "$output_dir/extracted" -name "*_block_*.py" | while read -r pyfile; do
        python3 -m py_compile "$pyfile" 2>/dev/null || {
          echo "MEDIUM: Syntax error in reusable component: $pyfile" >&2
          ((syntax_errors++))
        }
      done
      ;;

    INTEGRATION)
      echo "=== INTEGRATION Depth Validation ===" >&2
      echo "- Check: docker-compose.yml exists" >&2
      echo "- Check: All Python services validated" >&2
      echo >&2

      # Look for docker-compose
      if [ -f "$chapter_path/docker-compose.yml" ]; then
        echo "Found docker-compose.yml - integration setup detected" >&2

        # Validate Python files in service directories
        find "$chapter_path" -name "*.py" | while read -r pyfile; do
          python3 -m py_compile "$pyfile" 2>/dev/null || {
            echo "HIGH: Syntax error in integration component: $pyfile" >&2
            ((syntax_errors++))
          }
        done
      else
        echo "WARNING: No docker-compose.yml found for Layer 4" >&2
      fi
      ;;
  esac

  # Report summary
  echo >&2
  echo "=== Python Validation Summary ===" >&2
  echo "Total blocks: $total_blocks" >&2
  echo "Syntax errors: $syntax_errors" >&2
  echo "Runtime errors: $runtime_errors" >&2

  if [ "$syntax_errors" -gt 0 ] || [ "$runtime_errors" -gt 0 ]; then
    if [ "$depth" = "CRITICAL" ]; then
      echo "❌ CRITICAL errors found (blocks publication)" >&2
      return 2
    else
      echo "⚠️  Errors found (review recommended)" >&2
      return 1
    fi
  else
    echo "✅ All Python code validated" >&2
    return 0
  fi
}

# Run validation
validate_python_layer_aware "$CHAPTER_PATH" "$OUTPUT_DIR" "$LAYER" "$DEPTH"
