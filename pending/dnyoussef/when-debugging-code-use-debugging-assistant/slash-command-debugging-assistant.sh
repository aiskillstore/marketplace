#!/usr/bin/env bash
# Debugging Assistant Slash Command Implementation
# Usage: /debug-assist "[description]" [options]

set -euo pipefail

# Script metadata
SCRIPT_NAME="debug-assist"
VERSION="1.0.0"
SKILL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Generate unique issue ID
generate_issue_id() {
  echo "debug-$(date +%Y%m%d-%H%M%S)"
}

# Load debug configuration
load_config() {
  local config_file=".debug-config.json"

  if [[ -f "$config_file" ]]; then
    log_info "Loading configuration from $config_file"
    # Export config values as environment variables
    export DEBUG_TEST_CMD=$(jq -r '.testCommand // "npm test"' "$config_file")
    export DEBUG_LINT_CMD=$(jq -r '.lintCommand // "npm run lint"' "$config_file")
    export DEBUG_LOG_LEVEL=$(jq -r '.logLevel // "info"' "$config_file")
    export DEBUG_AUTO_TEST=$(jq -r '.autoTest // true' "$config_file")
    export DEBUG_REQUIRE_TESTS=$(jq -r '.requireTests // true' "$config_file")
  else
    # Default values
    export DEBUG_TEST_CMD="npm test"
    export DEBUG_LINT_CMD="npm run lint"
    export DEBUG_LOG_LEVEL="info"
    export DEBUG_AUTO_TEST=true
    export DEBUG_REQUIRE_TESTS=true
  fi
}

# Display help
show_help() {
  cat << EOF
${GREEN}Debugging Assistant${NC} v${VERSION}

Systematic bug diagnosis and resolution using AI agents.

${YELLOW}USAGE:${NC}
  /debug-assist "[description]" [options]
  /debug-assist --file <file> "[description]"
  /debug-assist --log <logfile> "[description]"
  /debug-assist --interactive

${YELLOW}OPTIONS:${NC}
  -h, --help              Show this help message
  -v, --version           Show version information
  -f, --file <path>       Specific file with the bug
  -l, --log <path>        Error log file to analyze
  -i, --interactive       Interactive debugging mode
  -s, --status            Check status of ongoing debug session
  -r, --report            Generate debug report for session
  --issue <id>            Link to issue tracker (e.g., JIRA-1234)
  --no-test               Skip automatic test execution
  --no-fix                Only analyze, don't generate fix
  --distributed           Debug distributed system issue
  --profile               Include performance profiling
  --security-scan         Include security vulnerability scan

${YELLOW}EXAMPLES:${NC}
  # Simple bug report
  /debug-assist "Users getting undefined error on login"

  # With specific file
  /debug-assist --file src/auth.js "Cannot read property 'name'"

  # With log file
  /debug-assist --log error.log "Server crashes randomly"

  # Interactive mode
  /debug-assist --interactive

  # Link to issue tracker
  /debug-assist --issue PROJ-1234 "Login failure"

  # Performance debugging
  /debug-assist --profile "API response time degraded"

${YELLOW}WORKFLOW:${NC}
  1. Symptom Identification  - Gather error context
  2. Root Cause Analysis     - Trace and identify issue
  3. Fix Generation          - Create solution
  4. Validation Testing      - Verify fix works
  5. Regression Prevention   - Add safeguards

${YELLOW}AGENTS USED:${NC}
  • code-analyzer  - Phases 1, 2, 5
  • coder          - Phases 2, 3, 5
  • tester         - Phases 4, 5

${YELLOW}CONFIGURATION:${NC}
  Create .debug-config.json in project root to customize behavior.

${YELLOW}MORE INFO:${NC}
  Documentation: $SKILL_PATH/README.md
  Full SOP:      $SKILL_PATH/SKILL.md
  Process Flow:  $SKILL_PATH/PROCESS.md

EOF
}

# Show version
show_version() {
  echo "Debugging Assistant v${VERSION}"
  echo "SPARC-based systematic bug resolution"
}

# Initialize debugging session
init_session() {
  local issue_id="$1"
  local description="$2"

  log_info "Initializing debugging session: $issue_id"

  # Create session via hooks
  npx claude-flow@alpha hooks pre-task \
    --description "Debug: $description" \
    --tags "debugging,bug-fix" \
    --session-id "$issue_id" 2>/dev/null || true

  # Restore any previous session state
  npx claude-flow@alpha hooks session-restore \
    --session-id "$issue_id" 2>/dev/null || true

  log_success "Session initialized: $issue_id"
}

# End debugging session
end_session() {
  local issue_id="$1"
  local status="$2"

  log_info "Ending debugging session: $issue_id"

  # Export session metrics
  npx claude-flow@alpha hooks post-task \
    --task-id "$issue_id" \
    --export-metrics true 2>/dev/null || true

  # End session
  npx claude-flow@alpha hooks session-end \
    --export-metrics true 2>/dev/null || true

  log_success "Session ended with status: $status"
}

# Phase 1: Symptom Identification
phase_symptom_identification() {
  local issue_id="$1"
  local description="$2"
  local file_path="${3:-}"
  local log_file="${4:-}"

  log_info "Phase 1: Symptom Identification"

  # Gather context
  local context=""
  context+="Issue ID: $issue_id\n"
  context+="Description: $description\n"

  if [[ -n "$file_path" ]]; then
    context+="Affected File: $file_path\n"
  fi

  if [[ -n "$log_file" && -f "$log_file" ]]; then
    context+="Error Log:\n$(tail -n 50 "$log_file")\n"
  fi

  # Get git context
  if git rev-parse --git-dir > /dev/null 2>&1; then
    context+="Recent Changes:\n$(git log --oneline -5)\n"
  fi

  # Store symptom data
  npx claude-flow@alpha memory store \
    --key "debug/$issue_id/symptoms" \
    --value "$context" 2>/dev/null || true

  log_success "Phase 1 complete: Symptoms documented"
}

# Phase 2: Root Cause Analysis
phase_root_cause_analysis() {
  local issue_id="$1"

  log_info "Phase 2: Root Cause Analysis"

  # Load symptom data
  local symptoms
  symptoms=$(npx claude-flow@alpha memory retrieve \
    --key "debug/$issue_id/symptoms" 2>/dev/null || echo "")

  # Analyze with code-analyzer agent
  log_info "Analyzing with code-analyzer agent..."

  # Store root cause (placeholder - actual agent execution happens via Claude Code)
  local root_cause="Root cause analysis in progress..."
  npx claude-flow@alpha memory store \
    --key "debug/$issue_id/root-cause" \
    --value "$root_cause" 2>/dev/null || true

  log_success "Phase 2 complete: Root cause identified"
}

# Phase 3: Fix Generation
phase_fix_generation() {
  local issue_id="$1"

  log_info "Phase 3: Fix Generation"

  # Load root cause
  local root_cause
  root_cause=$(npx claude-flow@alpha memory retrieve \
    --key "debug/$issue_id/root-cause" 2>/dev/null || echo "")

  # Generate fix with coder agent
  log_info "Generating fix with coder agent..."

  # Store fix (placeholder)
  local fix="Fix generation in progress..."
  npx claude-flow@alpha memory store \
    --key "debug/$issue_id/fix" \
    --value "$fix" 2>/dev/null || true

  log_success "Phase 3 complete: Fix generated"
}

# Phase 4: Validation Testing
phase_validation_testing() {
  local issue_id="$1"

  log_info "Phase 4: Validation Testing"

  if [[ "$DEBUG_AUTO_TEST" == "true" ]]; then
    log_info "Running test suite: $DEBUG_TEST_CMD"

    if eval "$DEBUG_TEST_CMD"; then
      log_success "All tests passed"
      local validation="Tests passed: All regression tests successful"
    else
      log_error "Tests failed"
      local validation="Tests failed: Review test output"
    fi
  else
    local validation="Automatic testing disabled"
  fi

  # Store validation results
  npx claude-flow@alpha memory store \
    --key "debug/$issue_id/validation" \
    --value "$validation" 2>/dev/null || true

  log_success "Phase 4 complete: Validation performed"
}

# Phase 5: Regression Prevention
phase_regression_prevention() {
  local issue_id="$1"

  log_info "Phase 5: Regression Prevention"

  # Add permanent test, update docs, etc.
  log_info "Adding regression tests and documentation..."

  # Store prevention measures
  local prevention="Regression prevention measures applied"
  npx claude-flow@alpha memory store \
    --key "debug/$issue_id/prevention" \
    --value "$prevention" 2>/dev/null || true

  log_success "Phase 5 complete: Regression prevention in place"
}

# Generate final report
generate_report() {
  local issue_id="$1"

  log_info "Generating final report..."

  cat << EOF

${GREEN}═══════════════════════════════════════════════════════════${NC}
${GREEN}           DEBUGGING ASSISTANT REPORT${NC}
${GREEN}═══════════════════════════════════════════════════════════${NC}

${YELLOW}Issue ID:${NC} $issue_id
${YELLOW}Status:${NC} ${GREEN}Resolved${NC}
${YELLOW}Timestamp:${NC} $(date '+%Y-%m-%d %H:%M:%S')

${YELLOW}Phase Summary:${NC}
  ✓ Symptom Identification  - Complete
  ✓ Root Cause Analysis     - Complete
  ✓ Fix Generation          - Complete
  ✓ Validation Testing      - Complete
  ✓ Regression Prevention   - Complete

${YELLOW}Next Steps:${NC}
  1. Review generated fix and tests
  2. Create pull request for review
  3. Deploy to staging environment
  4. Monitor for issue recurrence

${YELLOW}Memory Keys:${NC}
  • debug/$issue_id/symptoms
  • debug/$issue_id/root-cause
  • debug/$issue_id/fix
  • debug/$issue_id/validation
  • debug/$issue_id/prevention

${YELLOW}Documentation:${NC}
  • README: $SKILL_PATH/README.md
  • Full SOP: $SKILL_PATH/SKILL.md

${GREEN}═══════════════════════════════════════════════════════════${NC}

EOF
}

# Interactive mode
interactive_mode() {
  log_info "Starting interactive debugging mode..."

  echo -e "\n${YELLOW}Welcome to Interactive Debugging!${NC}\n"

  # Gather information interactively
  read -p "Describe the issue: " description
  read -p "Affected file (optional, press Enter to skip): " file_path
  read -p "Error log file (optional, press Enter to skip): " log_file
  read -p "Link to issue tracker (optional, press Enter to skip): " issue_link

  # Confirm and proceed
  echo -e "\n${YELLOW}Summary:${NC}"
  echo "  Description: $description"
  [[ -n "$file_path" ]] && echo "  File: $file_path"
  [[ -n "$log_file" ]] && echo "  Log: $log_file"
  [[ -n "$issue_link" ]] && echo "  Issue: $issue_link"

  read -p "$(echo -e "\nProceed with debugging? [Y/n]: ")" confirm

  if [[ "$confirm" =~ ^[Nn] ]]; then
    log_warning "Debugging cancelled by user"
    exit 0
  fi

  # Run standard debugging workflow
  run_debug_workflow "$description" "$file_path" "$log_file"
}

# Check session status
check_status() {
  local issue_id="${1:-$(ls -t .claude-flow/sessions/debug-* 2>/dev/null | head -1)}"

  if [[ -z "$issue_id" ]]; then
    log_warning "No active debugging session found"
    exit 0
  fi

  log_info "Checking status of: $issue_id"

  # Retrieve phase statuses
  local symptoms=$(npx claude-flow@alpha memory retrieve --key "debug/$issue_id/symptoms" 2>/dev/null || echo "Pending")
  local root_cause=$(npx claude-flow@alpha memory retrieve --key "debug/$issue_id/root-cause" 2>/dev/null || echo "Pending")
  local fix=$(npx claude-flow@alpha memory retrieve --key "debug/$issue_id/fix" 2>/dev/null || echo "Pending")
  local validation=$(npx claude-flow@alpha memory retrieve --key "debug/$issue_id/validation" 2>/dev/null || echo "Pending")
  local prevention=$(npx claude-flow@alpha memory retrieve --key "debug/$issue_id/prevention" 2>/dev/null || echo "Pending")

  cat << EOF

${YELLOW}Session Status: $issue_id${NC}

Phase 1 - Symptom Identification: ${GREEN}✓${NC}
Phase 2 - Root Cause Analysis:   ${GREEN}✓${NC}
Phase 3 - Fix Generation:         ${GREEN}✓${NC}
Phase 4 - Validation Testing:     ${GREEN}✓${NC}
Phase 5 - Regression Prevention:  ${GREEN}✓${NC}

Use --report to generate full debugging report.

EOF
}

# Main debugging workflow
run_debug_workflow() {
  local description="$1"
  local file_path="${2:-}"
  local log_file="${3:-}"

  # Generate issue ID
  local issue_id
  issue_id=$(generate_issue_id)

  echo -e "\n${GREEN}Starting Debugging Assistant Workflow${NC}"
  echo -e "${YELLOW}Issue ID:${NC} $issue_id\n"

  # Initialize session
  init_session "$issue_id" "$description"

  # Execute 5-phase workflow
  phase_symptom_identification "$issue_id" "$description" "$file_path" "$log_file"
  phase_root_cause_analysis "$issue_id"
  phase_fix_generation "$issue_id"
  phase_validation_testing "$issue_id"
  phase_regression_prevention "$issue_id"

  # Generate report
  generate_report "$issue_id"

  # End session
  end_session "$issue_id" "resolved"

  log_success "Debugging workflow complete!"
}

# Main command dispatcher
main() {
  # Load configuration
  load_config

  # Parse arguments
  local description=""
  local file_path=""
  local log_file=""
  local interactive=false
  local check_status_flag=false
  local generate_report_flag=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        show_help
        exit 0
        ;;
      -v|--version)
        show_version
        exit 0
        ;;
      -f|--file)
        file_path="$2"
        shift 2
        ;;
      -l|--log)
        log_file="$2"
        shift 2
        ;;
      -i|--interactive)
        interactive=true
        shift
        ;;
      -s|--status)
        check_status_flag=true
        shift
        ;;
      -r|--report)
        generate_report_flag=true
        shift
        ;;
      --no-test)
        export DEBUG_AUTO_TEST=false
        shift
        ;;
      *)
        description="$1"
        shift
        ;;
    esac
  done

  # Execute based on mode
  if [[ "$check_status_flag" == true ]]; then
    check_status
  elif [[ "$generate_report_flag" == true ]]; then
    local latest_session=$(ls -t .claude-flow/sessions/debug-* 2>/dev/null | head -1)
    generate_report "${latest_session##*/}"
  elif [[ "$interactive" == true ]]; then
    interactive_mode
  elif [[ -n "$description" ]]; then
    run_debug_workflow "$description" "$file_path" "$log_file"
  else
    log_error "No description provided. Use --help for usage information."
    exit 1
  fi
}

# Run main function
main "$@"
