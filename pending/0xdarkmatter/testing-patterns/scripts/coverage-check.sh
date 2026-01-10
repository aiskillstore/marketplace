#!/bin/bash
# Run tests with coverage and fail if below threshold
# Usage: ./coverage-check.sh [--threshold 80] [pytest-args...]

set -e

THRESHOLD=80
PYTEST_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        *)
            PYTEST_ARGS="$PYTEST_ARGS $1"
            shift
            ;;
    esac
done

echo "=== Running tests with coverage ==="
echo "Minimum coverage threshold: ${THRESHOLD}%"
echo ""

# Run pytest with coverage
pytest \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=${THRESHOLD} \
    ${PYTEST_ARGS}

echo ""
echo "=== Coverage report generated ==="
echo "HTML report: htmlcov/index.html"
