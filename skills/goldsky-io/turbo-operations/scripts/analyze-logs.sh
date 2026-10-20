#!/bin/bash
# Analyze Turbo pipeline logs for common issues
#
# Usage:
#   ./analyze-logs.sh <pipeline-name>
#   ./analyze-logs.sh <pipeline-name> --tail 100
#   goldsky turbo logs <pipeline> | ./analyze-logs.sh -
#
# Output: Summary of detected issues and recommendations

set -e

# Patterns below are kept in sync by hand with ../data/error-patterns.json,
# which is the machine-readable copy the skill reads.

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
PIPELINE_NAME=""
TAIL_LINES=50

while [[ $# -gt 0 ]]; do
    case $1 in
        --tail)
            TAIL_LINES="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 <pipeline-name> [--tail N]"
            echo ""
            echo "Analyze Turbo pipeline logs for common issues."
            echo ""
            echo "Arguments:"
            echo "  pipeline-name    Name of the pipeline to analyze"
            echo "  --tail N         Number of log lines to analyze (default: 50)"
            echo ""
            echo "Examples:"
            echo "  $0 my-pipeline"
            echo "  $0 my-pipeline --tail 100"
            echo "  goldsky turbo logs my-pipeline | $0 -"
            exit 0
            ;;
        -)
            PIPELINE_NAME="-"
            shift
            ;;
        *)
            PIPELINE_NAME="$1"
            shift
            ;;
    esac
done

if [ -z "$PIPELINE_NAME" ]; then
    echo "Error: Pipeline name required" >&2
    echo "Usage: $0 <pipeline-name> [--tail N]" >&2
    exit 1
fi

# Get logs
if [ "$PIPELINE_NAME" = "-" ]; then
    LOGS=$(cat)
else
    echo -e "${BLUE}Fetching logs for pipeline: $PIPELINE_NAME${NC}"
    LOGS=$(goldsky turbo logs "$PIPELINE_NAME" --tail "$TAIL_LINES" 2>&1)
fi

echo ""
echo "========================================"
echo "       PIPELINE LOG ANALYSIS"
echo "========================================"
echo ""

# Track findings
ERRORS_FOUND=0
WARNINGS_FOUND=0
HEALTHY_SIGNS=0

# Check for error patterns
check_pattern() {
    local pattern="$1"
    local description="$2"
    # $3 is the category, kept in the call signature for readability but unused here
    local severity="$4"
    
    if echo "$LOGS" | grep -qiE "$pattern"; then
        if [ "$severity" = "error" ]; then
            echo -e "${RED}[ERROR]${NC} $description"
            ERRORS_FOUND=$((ERRORS_FOUND + 1))
        elif [ "$severity" = "warning" ]; then
            echo -e "${YELLOW}[WARNING]${NC} $description"
            WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
        fi
        return 0
    fi
    return 1
}

# Error checks
echo "Checking for issues..."
echo ""

# Authentication errors
if check_pattern "password authentication failed" "Database authentication failed - check secret credentials" "auth" "error"; then
    echo "  → Fix: Update secret with correct password using 'goldsky secret update'"
fi

# Connection errors
if check_pattern "connection refused" "Cannot connect to database/service" "network" "error"; then
    echo "  → Fix: Check host/port in secret, verify database is running"
fi

# Secret errors
if check_pattern "Secret.*not found" "Referenced secret does not exist" "config" "error"; then
    echo "  → Fix: Create secret with 'goldsky secret create --name NAME --value ...'"
fi

# Storage errors
if check_pattern "size limit.*exceeded" "Storage quota exceeded (likely Neon free tier 512MB)" "storage" "error"; then
    echo "  → Fix: Upgrade database plan or clear existing data"
fi

# Dataset errors
if check_pattern "unknown dataset" "Invalid dataset name in pipeline config" "config" "error"; then
    echo "  → Fix: Check chain prefix (matic not polygon) and dataset type"
fi

# SQL errors
if check_pattern "SQL syntax|Parser error" "SQL transform syntax error" "config" "error"; then
    echo "  → Fix: Validate pipeline YAML with 'goldsky turbo validate'"
fi

# Performance warnings
if check_pattern "backpressure|lag|slow" "Processing may be falling behind" "perf" "warning"; then
    echo "  → Consider: Increase resource_size in pipeline config"
fi

# Memory issues
if check_pattern "out of memory|OOM" "Memory limit exceeded" "resource" "error"; then
    echo "  → Fix: Increase resource_size from 's' to 'm' or 'l'"
fi

echo ""

# Check for healthy signs
echo "Checking health indicators..."
echo ""

if echo "$LOGS" | grep -qiE "Processing block|processing slot"; then
    echo -e "${GREEN}[HEALTHY]${NC} Pipeline is actively processing data"
    HEALTHY_SIGNS=$((HEALTHY_SIGNS + 1))
fi

if echo "$LOGS" | grep -qiE "checkpoint|rows written"; then
    echo -e "${GREEN}[HEALTHY]${NC} Data is being written successfully"
    HEALTHY_SIGNS=$((HEALTHY_SIGNS + 1))
fi

echo ""
echo "========================================"
echo "             SUMMARY"
echo "========================================"
echo ""

if [ $ERRORS_FOUND -gt 0 ]; then
    echo -e "${RED}Errors found: $ERRORS_FOUND${NC}"
fi

if [ $WARNINGS_FOUND -gt 0 ]; then
    echo -e "${YELLOW}Warnings found: $WARNINGS_FOUND${NC}"
fi

if [ $HEALTHY_SIGNS -gt 0 ]; then
    echo -e "${GREEN}Healthy indicators: $HEALTHY_SIGNS${NC}"
fi

if [ $ERRORS_FOUND -eq 0 ] && [ $WARNINGS_FOUND -eq 0 ]; then
    if [ $HEALTHY_SIGNS -gt 0 ]; then
        echo -e "${GREEN}No issues detected - pipeline appears healthy!${NC}"
    else
        echo -e "${YELLOW}No obvious issues, but no healthy indicators either.${NC}"
        echo "  → Try: goldsky turbo inspect $PIPELINE_NAME"
    fi
fi

echo ""
echo "Related commands:"
echo "  - View live data: goldsky turbo inspect $PIPELINE_NAME"
echo "  - More logs: goldsky turbo logs $PIPELINE_NAME --tail 100"
echo "  - List secrets: goldsky secret list"
echo ""
