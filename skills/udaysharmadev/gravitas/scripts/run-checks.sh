#!/usr/bin/env bash
# run-checks.sh — Quick verification script for GRAVITAS
# Run this as your "evidence" step after implementing changes.
#
# Usage: ./scripts/run-checks.sh [project-root]
#
# This script auto-detects the project type and runs appropriate checks.
# Exit code 0 = all checks passed. Non-zero = failures detected.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
cd "$PROJECT_ROOT"

echo "=== GRAVITAS Verification Checks ==="
echo "Project root: $(pwd)"
echo ""

FAILED=0

# --- Detect project type and run checks ---

# Node.js / TypeScript
if [ -f "package.json" ]; then
    echo "--- Node.js project detected ---"

    if [ -f "tsconfig.json" ] && command -v npx &>/dev/null; then
        echo "Running type check..."
        if npx tsc --noEmit 2>&1; then
            echo "✓ Type check passed"
        else
            echo "✗ Type check failed"
            FAILED=1
        fi
    fi

    if command -v npm &>/dev/null && grep -q '"lint"' package.json; then
        echo "Running linter..."
        if npm run lint 2>&1; then
            echo "✓ Lint passed"
        else
            echo "✗ Lint failed"
            FAILED=1
        fi
    fi

    if command -v npm &>/dev/null && grep -q '"test"' package.json; then
        echo "Running tests..."
        if npm test 2>&1; then
            echo "✓ Tests passed"
        else
            echo "✗ Tests failed"
            FAILED=1
        fi
    fi

    if command -v npm &>/dev/null && grep -q '"build"' package.json; then
        echo "Running build..."
        if npm run build 2>&1; then
            echo "✓ Build passed"
        else
            echo "✗ Build failed"
            FAILED=1
        fi
    fi
fi

# Python
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
    echo "--- Python project detected ---"

    PYTHON_CMD="python3"
    if [ -f ".venv/bin/python3" ]; then
        PYTHON_CMD=".venv/bin/python3"
    elif [ -f "venv/bin/python3" ]; then
        PYTHON_CMD="venv/bin/python3"
    elif ! command -v $PYTHON_CMD &>/dev/null; then
        PYTHON_CMD="python"
    fi

    if command -v $PYTHON_CMD &>/dev/null; then
        echo "Running syntax check..."
        if $PYTHON_CMD -m py_compile $(find . -name "*.py" -not -path "./.venv/*" -not -path "./venv/*" | head -20) 2>&1; then
            echo "✓ Syntax check passed"
        else
            echo "✗ Syntax check failed"
            FAILED=1
        fi
    fi

    if command -v pytest &>/dev/null; then
        echo "Running tests with pytest..."
        if pytest 2>&1; then
            echo "✓ Tests passed"
        else
            echo "✗ Tests failed"
            FAILED=1
        fi
    elif command -v $PYTHON_CMD &>/dev/null && [ -d "tests" ]; then
        echo "Running tests with unittest..."
        if $PYTHON_CMD -m unittest discover -s tests -v 2>&1; then
            echo "✓ Tests passed"
        else
            echo "✗ Tests failed"
            FAILED=1
        fi
    fi

    if command -v ruff &>/dev/null; then
        echo "Running linter..."
        if ruff check . 2>&1; then
            echo "✓ Lint passed"
        else
            echo "✗ Lint failed"
            FAILED=1
        fi
    fi
fi

# Rust
if [ -f "Cargo.toml" ]; then
    echo "--- Rust project detected ---"

    if command -v cargo &>/dev/null; then
        echo "Running cargo check..."
        if cargo check 2>&1; then
            echo "✓ Check passed"
        else
            echo "✗ Check failed"
            FAILED=1
        fi

        echo "Running tests..."
        if cargo test 2>&1; then
            echo "✓ Tests passed"
        else
            echo "✗ Tests failed"
            FAILED=1
        fi

        echo "Running clippy..."
        if cargo clippy -- -D warnings 2>&1; then
            echo "✓ Clippy passed"
        else
            echo "✗ Clippy failed"
            FAILED=1
        fi
    fi
fi

# Go
if [ -f "go.mod" ]; then
    echo "--- Go project detected ---"

    if command -v go &>/dev/null; then
        echo "Running go vet..."
        if go vet ./... 2>&1; then
            echo "✓ Vet passed"
        else
            echo "✗ Vet failed"
            FAILED=1
        fi

        echo "Running tests..."
        if go test ./... 2>&1; then
            echo "✓ Tests passed"
        else
            echo "✗ Tests failed"
            FAILED=1
        fi
    fi
fi

# --- Summary ---
echo ""
if [ $FAILED -eq 0 ]; then
    echo "=== All checks passed ==="
else
    echo "=== Some checks failed — see above ==="
    exit 1
fi
