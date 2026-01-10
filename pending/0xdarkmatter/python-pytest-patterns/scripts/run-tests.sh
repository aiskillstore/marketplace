#!/bin/bash
# Run pytest with recommended options
# Usage: ./run-tests.sh [options]
#
# Options:
#   --quick     Skip slow tests, minimal output
#   --coverage  Run with coverage report
#   --watch     Watch mode with pytest-watch
#   --failed    Re-run only failed tests
#   --debug     Enable debug output

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default options
PYTEST_ARGS="-v"
COVERAGE=""
WATCH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            PYTEST_ARGS="-q -x --tb=short"
            shift
            ;;
        --coverage)
            COVERAGE="--cov=src --cov-report=term-missing --cov-report=html"
            shift
            ;;
        --watch)
            WATCH=1
            shift
            ;;
        --failed)
            PYTEST_ARGS="$PYTEST_ARGS --lf"
            shift
            ;;
        --debug)
            PYTEST_ARGS="$PYTEST_ARGS -s --tb=long"
            shift
            ;;
        *)
            PYTEST_ARGS="$PYTEST_ARGS $1"
            shift
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest not found. Install with: pip install pytest${NC}"
    exit 1
fi

# Watch mode
if [[ -n "$WATCH" ]]; then
    if ! command -v ptw &> /dev/null; then
        echo -e "${YELLOW}pytest-watch not found. Installing...${NC}"
        pip install pytest-watch
    fi
    echo -e "${GREEN}Starting watch mode...${NC}"
    ptw -- $PYTEST_ARGS $COVERAGE
    exit 0
fi

# Run tests
echo -e "${GREEN}Running pytest...${NC}"
echo "pytest $PYTEST_ARGS $COVERAGE"
echo ""

pytest $PYTEST_ARGS $COVERAGE

# Open coverage report if generated
if [[ -n "$COVERAGE" ]] && [[ -f "htmlcov/index.html" ]]; then
    echo ""
    echo -e "${GREEN}Coverage report: htmlcov/index.html${NC}"
    if command -v open &> /dev/null; then
        read -p "Open coverage report? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open htmlcov/index.html
        fi
    fi
fi
