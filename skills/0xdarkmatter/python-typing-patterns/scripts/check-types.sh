#!/bin/bash
# Run type checkers with common options
# Usage: ./check-types.sh [--mypy|--pyright|--both] [--strict] [path]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
CHECKER="both"
STRICT=""
TARGET="src"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mypy)
            CHECKER="mypy"
            shift
            ;;
        --pyright)
            CHECKER="pyright"
            shift
            ;;
        --both)
            CHECKER="both"
            shift
            ;;
        --strict)
            STRICT="--strict"
            shift
            ;;
        *)
            TARGET="$1"
            shift
            ;;
    esac
done

# Check if target exists
if [[ ! -e "$TARGET" ]]; then
    echo -e "${RED}Target not found: $TARGET${NC}"
    exit 1
fi

run_mypy() {
    echo -e "${BLUE}=== Running mypy ===${NC}"

    if ! command -v mypy &> /dev/null; then
        echo -e "${YELLOW}mypy not found. Install with: pip install mypy${NC}"
        return 1
    fi

    MYPY_ARGS="--show-error-codes --show-error-context --pretty"
    if [[ -n "$STRICT" ]]; then
        MYPY_ARGS="$MYPY_ARGS --strict"
    fi

    echo "mypy $MYPY_ARGS $TARGET"
    echo ""

    if mypy $MYPY_ARGS "$TARGET"; then
        echo -e "${GREEN}✓ mypy passed${NC}"
        return 0
    else
        echo -e "${RED}✗ mypy found errors${NC}"
        return 1
    fi
}

run_pyright() {
    echo -e "${BLUE}=== Running pyright ===${NC}"

    if ! command -v pyright &> /dev/null; then
        echo -e "${YELLOW}pyright not found. Install with: pip install pyright${NC}"
        return 1
    fi

    PYRIGHT_ARGS=""
    if [[ -n "$STRICT" ]]; then
        # Create temporary config for strict mode
        TEMP_CONFIG=$(mktemp)
        cat > "$TEMP_CONFIG" << EOF
{
  "typeCheckingMode": "strict"
}
EOF
        PYRIGHT_ARGS="--project $TEMP_CONFIG"
    fi

    echo "pyright $PYRIGHT_ARGS $TARGET"
    echo ""

    if pyright $PYRIGHT_ARGS "$TARGET"; then
        echo -e "${GREEN}✓ pyright passed${NC}"
        [[ -n "$STRICT" ]] && rm -f "$TEMP_CONFIG"
        return 0
    else
        echo -e "${RED}✗ pyright found errors${NC}"
        [[ -n "$STRICT" ]] && rm -f "$TEMP_CONFIG"
        return 1
    fi
}

# Run checkers
MYPY_STATUS=0
PYRIGHT_STATUS=0

case $CHECKER in
    mypy)
        run_mypy || MYPY_STATUS=$?
        ;;
    pyright)
        run_pyright || PYRIGHT_STATUS=$?
        ;;
    both)
        run_mypy || MYPY_STATUS=$?
        echo ""
        run_pyright || PYRIGHT_STATUS=$?
        ;;
esac

# Summary
echo ""
echo -e "${BLUE}=== Summary ===${NC}"

if [[ "$CHECKER" == "both" ]] || [[ "$CHECKER" == "mypy" ]]; then
    if [[ $MYPY_STATUS -eq 0 ]]; then
        echo -e "mypy:    ${GREEN}✓ passed${NC}"
    else
        echo -e "mypy:    ${RED}✗ failed${NC}"
    fi
fi

if [[ "$CHECKER" == "both" ]] || [[ "$CHECKER" == "pyright" ]]; then
    if [[ $PYRIGHT_STATUS -eq 0 ]]; then
        echo -e "pyright: ${GREEN}✓ passed${NC}"
    else
        echo -e "pyright: ${RED}✗ failed${NC}"
    fi
fi

# Exit with error if any checker failed
if [[ $MYPY_STATUS -ne 0 ]] || [[ $PYRIGHT_STATUS -ne 0 ]]; then
    exit 1
fi
