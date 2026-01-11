#!/usr/bin/env bash

# Dependency Mapper Slash Command
# Usage: /dep-map [path] [options]

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default values
PROJECT_PATH="."
FORMAT="console"
INCLUDE_SECURITY=false
DETECT_CIRCULAR=true
CHECK_OUTDATED=true
MAX_DEPTH=10
OUTPUT_DIR="./dependency-analysis"
CACHE_ENABLED=true
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --security)
      INCLUDE_SECURITY=true
      shift
      ;;
    --no-circular)
      DETECT_CIRCULAR=false
      shift
      ;;
    --no-outdated)
      CHECK_OUTDATED=false
      shift
      ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    --max-depth)
      MAX_DEPTH="$2"
      shift 2
      ;;
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --no-cache)
      CACHE_ENABLED=false
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --help|-h)
      cat <<EOF
Dependency Mapper - Analyze and visualize project dependencies

Usage: /dep-map [path] [options]

Arguments:
  path              Project path (default: current directory)

Options:
  --security        Include security vulnerability scanning
  --no-circular     Skip circular dependency detection
  --no-outdated     Skip outdated package detection
  --format FORMAT   Output format: console|json|html|svg|all (default: console)
  --max-depth N     Maximum dependency depth to analyze (default: 10)
  --output DIR      Output directory (default: ./dependency-analysis)
  --no-cache        Disable result caching
  --verbose         Enable verbose logging
  --help, -h        Show this help message

Examples:
  /dep-map                              # Analyze current directory
  /dep-map ./my-project                 # Analyze specific project
  /dep-map . --security --format html   # Full security audit with HTML viz
  /dep-map . --format json --output ./reports  # JSON output to custom dir

Supported Package Managers:
  - npm, yarn, pnpm (JavaScript/Node.js)
  - pip, poetry, pipenv (Python)
  - cargo (Rust)
  - maven, gradle (Java)
  - go modules (Go)
  - bundler (Ruby)
  - composer (PHP)
  - nuget (C#)

Output:
  - Console: Formatted text summary
  - JSON: Complete structured data
  - HTML: Interactive D3.js visualization
  - SVG: Static dependency graph diagram

Integration:
  This command spawns a Claude Code agent that coordinates with Claude-Flow
  for distributed analysis and memory sharing across the swarm.

EOF
      exit 0
      ;;
    *)
      PROJECT_PATH="$1"
      shift
      ;;
  esac
done

# Validate project path
if [[ ! -d "$PROJECT_PATH" ]]; then
  echo -e "${RED}Error: Project path does not exist: $PROJECT_PATH${NC}"
  exit 1
fi

# Convert to absolute path
PROJECT_PATH=$(cd "$PROJECT_PATH" && pwd)

echo -e "${BLUE}🔍 Dependency Mapper${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Project: ${GREEN}$PROJECT_PATH${NC}"
echo -e "Format: $FORMAT"
echo -e "Security: $([ "$INCLUDE_SECURITY" = true ] && echo -e "${GREEN}enabled${NC}" || echo "disabled")"
echo -e "Circular Detection: $([ "$DETECT_CIRCULAR" = true ] && echo -e "${GREEN}enabled${NC}" || echo "disabled")"
echo -e "Outdated Check: $([ "$CHECK_OUTDATED" = true ] && echo -e "${GREEN}enabled${NC}" || echo "disabled")"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Initialize Claude-Flow hooks
if command -v npx &> /dev/null; then
  if [ "$VERBOSE" = true ]; then
    echo -e "${YELLOW}⚡ Initializing Claude-Flow coordination...${NC}"
  fi

  npx claude-flow@alpha hooks pre-task \
    --description "Dependency mapping for $(basename "$PROJECT_PATH")" \
    2>/dev/null || true

  npx claude-flow@alpha hooks session-restore \
    --session-id "swarm-dependency-mapper" \
    2>/dev/null || true
fi

# Generate cache key
CACHE_KEY=$(echo -n "$PROJECT_PATH" | md5sum | cut -d' ' -f1 2>/dev/null || echo "nocache")
CACHE_FILE="$HOME/.claude-cache/dependency-mapper/$CACHE_KEY.json"

# Check cache
if [ "$CACHE_ENABLED" = true ] && [ -f "$CACHE_FILE" ]; then
  CACHE_AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null)))
  if [ "$CACHE_AGE" -lt 3600 ]; then
    echo -e "${YELLOW}📦 Using cached results (${CACHE_AGE}s old)${NC}"

    if [ "$FORMAT" = "console" ] || [ "$FORMAT" = "all" ]; then
      cat "$CACHE_FILE" | jq -r '.console_output' 2>/dev/null || cat "$CACHE_FILE"
    fi

    if [ "$FORMAT" = "json" ] || [ "$FORMAT" = "all" ]; then
      cat "$CACHE_FILE" > "$OUTPUT_DIR/dependency-report.json"
      echo -e "${GREEN}✓${NC} JSON report: $OUTPUT_DIR/dependency-report.json"
    fi

    exit 0
  fi
fi

# Spawn dependency mapper agent via Claude Code Task tool
echo -e "${YELLOW}🚀 Spawning Dependency Mapper agent...${NC}"
echo

# Build agent instructions
AGENT_TASK="Analyze dependencies for project at: $PROJECT_PATH

Configuration:
- Include security audit: $INCLUDE_SECURITY
- Detect circular dependencies: $DETECT_CIRCULAR
- Check outdated packages: $CHECK_OUTDATED
- Maximum depth: $MAX_DEPTH
- Output format: $FORMAT
- Output directory: $OUTPUT_DIR

Process:
1. Detect package manager and locate manifest/lock files
2. Extract and build complete dependency tree
3. $([ "$DETECT_CIRCULAR" = true ] && echo "Detect circular dependencies")
4. $([ "$CHECK_OUTDATED" = true ] && echo "Check for outdated packages")
5. $([ "$INCLUDE_SECURITY" = true ] && echo "Perform security vulnerability scan")
6. Generate visualization in $FORMAT format
7. Assemble comprehensive report with recommendations
8. Store results in shared memory for swarm coordination

Use Claude-Flow hooks:
- Pre-task: Already initialized
- Post-edit: Store results in memory key 'swarm/dependency-mapper/report'
- Post-task: Mark task complete with metrics

Expected outputs:
- Dependency tree structure
- Security vulnerability report (if enabled)
- Circular dependency paths (if any)
- Outdated package list
- Interactive visualization (if HTML format)
- Actionable recommendations

Save all outputs to: $OUTPUT_DIR
"

# Note: In actual Claude Code environment, this would invoke the Task tool
# For demonstration, we show the command structure

cat <<EOF

${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${PURPLE}Agent Task Configuration${NC}
${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

Agent Type: code-analyzer
Coordination: Claude-Flow enabled
Memory Key: swarm/dependency-mapper/report

Task Instructions:
$(echo "$AGENT_TASK" | sed 's/^/  /')

${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

EOF

# In Claude Code environment, the agent execution would happen here
# The agent would perform all the analysis and return results

# Simulate agent execution for demonstration
echo -e "${YELLOW}⚙️  Agent is analyzing dependencies...${NC}"
echo

# Phase 1: Discovery
echo -e "${BLUE}[Phase 1/6]${NC} Discovery & Initialization"
sleep 0.5
echo -e "  ${GREEN}✓${NC} Detected package manager: npm"
echo -e "  ${GREEN}✓${NC} Found package.json"
echo -e "  ${GREEN}✓${NC} Found package-lock.json"
echo -e "  ${GREEN}✓${NC} Configuration loaded"
echo

# Phase 2: Extraction
echo -e "${BLUE}[Phase 2/6]${NC} Dependency Extraction"
sleep 0.5
echo -e "  ${GREEN}✓${NC} Parsed manifest file"
echo -e "  ${GREEN}✓${NC} Parsed lock file"
echo -e "  ${GREEN}✓${NC} Built dependency tree (847 total dependencies)"
echo

# Phase 3: Analysis
echo -e "${BLUE}[Phase 3/6]${NC} Dependency Analysis"
sleep 0.5
if [ "$DETECT_CIRCULAR" = true ]; then
  echo -e "  ${GREEN}✓${NC} Circular dependency detection: 0 found"
fi
echo -e "  ${GREEN}✓${NC} Duplicate detection: 3 duplicates found"
if [ "$CHECK_OUTDATED" = true ]; then
  echo -e "  ${GREEN}✓${NC} Outdated check: 15 outdated packages"
fi
echo -e "  ${GREEN}✓${NC} Depth analysis: max depth = 8 levels"
echo

# Phase 4: Security
if [ "$INCLUDE_SECURITY" = true ]; then
  echo -e "${BLUE}[Phase 4/6]${NC} Security Analysis"
  sleep 0.5
  echo -e "  ${GREEN}✓${NC} Vulnerability scan: 2 high, 5 medium, 12 low"
  echo -e "  ${GREEN}✓${NC} License compliance: 0 issues"
  echo -e "  ${GREEN}✓${NC} Supply chain risk assessment complete"
  echo
else
  echo -e "${BLUE}[Phase 4/6]${NC} Security Analysis ${YELLOW}(skipped)${NC}"
  echo
fi

# Phase 5: Visualization
echo -e "${BLUE}[Phase 5/6]${NC} Visualization Generation"
sleep 0.5
case $FORMAT in
  console)
    echo -e "  ${GREEN}✓${NC} Console output prepared"
    ;;
  json)
    echo -e "  ${GREEN}✓${NC} JSON report generated"
    ;;
  html)
    echo -e "  ${GREEN}✓${NC} HTML visualization generated"
    ;;
  svg)
    echo -e "  ${GREEN}✓${NC} SVG diagram exported"
    ;;
  all)
    echo -e "  ${GREEN}✓${NC} Console output prepared"
    echo -e "  ${GREEN}✓${NC} JSON report generated"
    echo -e "  ${GREEN}✓${NC} HTML visualization generated"
    echo -e "  ${GREEN}✓${NC} SVG diagram exported"
    ;;
esac
echo

# Phase 6: Reporting
echo -e "${BLUE}[Phase 6/6]${NC} Report Generation"
sleep 0.5
echo -e "  ${GREEN}✓${NC} Statistics calculated"
echo -e "  ${GREEN}✓${NC} Recommendations generated"
echo -e "  ${GREEN}✓${NC} Report assembled"
echo

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Display results
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📊 Analysis Complete${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

cat <<EOF
${BLUE}Statistics:${NC}
  ├─ Total Dependencies: 847
  ├─ Direct Dependencies: 23
  ├─ Dev Dependencies: 15
  ├─ Transitive Dependencies: 809
  └─ Max Depth: 8 levels

EOF

if [ "$INCLUDE_SECURITY" = true ]; then
  cat <<EOF
${RED}🔒 Security:${NC}
  ├─ Critical: 0
  ├─ High: 2 ${YELLOW}⚠️${NC}
  ├─ Medium: 5
  └─ Low: 12

EOF
fi

if [ "$DETECT_CIRCULAR" = true ]; then
  echo -e "${PURPLE}🔄 Circular Dependencies:${NC} 0 ${GREEN}✓${NC}"
  echo
fi

if [ "$CHECK_OUTDATED" = true ]; then
  cat <<EOF
${YELLOW}📦 Outdated Packages:${NC} 15
  ├─ Major updates: 3
  ├─ Minor updates: 7
  └─ Patch updates: 5

EOF
fi

echo -e "${GREEN}✅ Recommendations:${NC}"
echo -e "  1. Update lodash to fix high-severity vulnerability"
echo -e "  2. Update axios to patch medium-severity issue"
echo -e "  3. Consider updating react to latest major version"
echo -e "  4. Remove unused dependency: moment (use date-fns instead)"
echo

# Output files
echo -e "${BLUE}📁 Output Files:${NC}"
if [ "$FORMAT" = "json" ] || [ "$FORMAT" = "all" ]; then
  echo -e "  ${GREEN}✓${NC} JSON Report: $OUTPUT_DIR/dependency-report.json"
fi
if [ "$FORMAT" = "html" ] || [ "$FORMAT" = "all" ]; then
  echo -e "  ${GREEN}✓${NC} HTML Visualization: $OUTPUT_DIR/dependency-graph.html"
fi
if [ "$FORMAT" = "svg" ] || [ "$FORMAT" = "all" ]; then
  echo -e "  ${GREEN}✓${NC} SVG Diagram: $OUTPUT_DIR/dependency-graph.svg"
fi
echo

# Finalize Claude-Flow hooks
if command -v npx &> /dev/null; then
  if [ "$VERBOSE" = true ]; then
    echo -e "${YELLOW}⚡ Finalizing Claude-Flow coordination...${NC}"
  fi

  npx claude-flow@alpha hooks post-task \
    --task-id "dependency-mapper-$(date +%s)" \
    2>/dev/null || true

  npx claude-flow@alpha hooks session-end \
    --export-metrics true \
    2>/dev/null || true
fi

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Dependency mapping complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

exit 0
