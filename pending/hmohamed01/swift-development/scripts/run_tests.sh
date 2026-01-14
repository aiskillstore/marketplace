#!/bin/bash
# Run Swift tests with common options
# Usage: run_tests.sh [options]
#   --coverage    Enable code coverage
#   --parallel    Run tests in parallel
#   --filter      Run specific test (e.g., MyTests.testFoo)
#   --verbose     Verbose output
#   --xcode       Use xcodebuild instead of swift test

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "${GREEN}==>${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

echo_error() {
    echo -e "${RED}Error:${NC} $1" >&2
}

# Check prerequisites
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo_error "$1 is not installed."
        echo "         Install with: $2" >&2
        return 1
    fi
}

COVERAGE=""
PARALLEL=""
FILTER=""
VERBOSE=""
USE_XCODE=false
WORKSPACE=""
SCHEME=""
DESTINATION="platform=iOS Simulator,name=iPhone 15"

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage) COVERAGE="--enable-code-coverage"; shift ;;
        --parallel) PARALLEL="--parallel"; shift ;;
        --filter) FILTER="--filter $2"; shift 2 ;;
        --verbose) VERBOSE="-v"; shift ;;
        --xcode) USE_XCODE=true; shift ;;
        --workspace) WORKSPACE="$2"; shift 2 ;;
        --scheme) SCHEME="$2"; shift 2 ;;
        --destination) DESTINATION="$2"; shift 2 ;;
        *) echo_error "Unknown option: $1"; echo "Usage: run_tests.sh [--coverage] [--parallel] [--filter <test>] [--verbose] [--xcode] [--workspace <path>] [--scheme <name>] [--destination <dest>]" >&2; exit 1 ;;
    esac
done

if $USE_XCODE; then
    # Check xcodebuild is available
    if ! check_command xcodebuild "xcode-select --install"; then
        exit 1
    fi

    # xcodebuild mode
    if [[ -z "$WORKSPACE" ]]; then
        # Try to find workspace
        WORKSPACE=$(find . -maxdepth 1 -name "*.xcworkspace" 2>/dev/null | head -1)
        if [[ -z "$WORKSPACE" ]]; then
            PROJECT=$(find . -maxdepth 1 -name "*.xcodeproj" 2>/dev/null | head -1)
            if [[ -n "$PROJECT" ]]; then
                echo_step "Using project: $PROJECT"
                OUTPUT=$(xcodebuild test \
                    -project "$PROJECT" \
                    -scheme "${SCHEME:-$(basename "$PROJECT" .xcodeproj)}" \
                    -destination "$DESTINATION" \
                    ${COVERAGE:+-enableCodeCoverage YES} 2>&1)
                
                # Use xcpretty if available, otherwise plain output
                if command -v xcpretty &> /dev/null; then
                    echo "$OUTPUT" | xcpretty || echo "$OUTPUT"
                else
                    echo "$OUTPUT"
                fi
                exit 0
            fi
        fi
    fi

    if [[ -n "$WORKSPACE" ]]; then
        echo_step "Using workspace: $WORKSPACE"
        OUTPUT=$(xcodebuild test \
            -workspace "$WORKSPACE" \
            -scheme "${SCHEME:-$(basename "$WORKSPACE" .xcworkspace)}" \
            -destination "$DESTINATION" \
            ${COVERAGE:+-enableCodeCoverage YES} 2>&1)
        
        # Use xcpretty if available, otherwise plain output
        if command -v xcpretty &> /dev/null; then
            echo "$OUTPUT" | xcpretty || echo "$OUTPUT"
        else
            echo "$OUTPUT"
        fi
    else
        echo_error "No workspace or project found."
        echo "         Use --workspace <path> or --scheme <name> to specify a project." >&2
        exit 1
    fi
else
    # Check swift is available
    if ! check_command swift "Install Xcode Command Line Tools: xcode-select --install"; then
        exit 1
    fi

    # swift test mode
    echo_step "Running: swift test $VERBOSE $PARALLEL $COVERAGE $FILTER"
    if ! swift test $VERBOSE $PARALLEL $COVERAGE $FILTER; then
        echo_error "Tests failed"
        exit 1
    fi

    # Show coverage report if enabled
    if [[ -n "$COVERAGE" ]]; then
        echo ""
        echo "Coverage report:"
        swift test --show-codecov-path 2>/dev/null || echo "Coverage data available in .build/coverage"
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Tests completed!${NC}"
echo -e "${GREEN}========================================${NC}"
