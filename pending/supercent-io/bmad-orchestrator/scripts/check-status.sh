#!/bin/bash
# BMAD Workflow Status Checker
# Reads and displays current workflow status from YAML file

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Default paths
CONFIG_FILE="bmad/config.yaml"
STATUS_FILE="docs/bmm-workflow-status.yaml"

# Check if project is initialized
if [ ! -f "$CONFIG_FILE" ]; then
  echo -e "${RED}Error: BMAD not initialized in this project${NC}"
  echo -e "${YELLOW}Run /workflow-init to initialize BMAD${NC}"
  exit 1
fi

# Read output folder from config if available
if command -v yq &> /dev/null; then
  OUTPUT_FOLDER=$(yq eval '.output_folder' "$CONFIG_FILE" 2>/dev/null || echo "docs")
  STATUS_FILE="${OUTPUT_FOLDER}/bmm-workflow-status.yaml"
elif grep -q "output_folder:" "$CONFIG_FILE"; then
  OUTPUT_FOLDER=$(grep "output_folder:" "$CONFIG_FILE" | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"')
  STATUS_FILE="${OUTPUT_FOLDER}/bmm-workflow-status.yaml"
fi

# Check if status file exists
if [ ! -f "$STATUS_FILE" ]; then
  echo -e "${RED}Error: Workflow status file not found: ${STATUS_FILE}${NC}"
  echo -e "${YELLOW}Run /workflow-init to create status file${NC}"
  exit 1
fi

# Parse config for project info
PROJECT_NAME="Unknown"
PROJECT_TYPE="Unknown"
PROJECT_LEVEL="Unknown"

if command -v yq &> /dev/null; then
  # Use yq if available for proper YAML parsing
  PROJECT_NAME=$(yq eval '.project_name' "$STATUS_FILE" 2>/dev/null || echo "Unknown")
  PROJECT_TYPE=$(yq eval '.project_type' "$STATUS_FILE" 2>/dev/null || echo "Unknown")
  PROJECT_LEVEL=$(yq eval '.project_level' "$STATUS_FILE" 2>/dev/null || echo "Unknown")
else
  # Fallback to grep/sed
  if grep -q "project_name:" "$STATUS_FILE"; then
    PROJECT_NAME=$(grep "project_name:" "$STATUS_FILE" | head -1 | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"')
  fi
  if grep -q "project_type:" "$STATUS_FILE"; then
    PROJECT_TYPE=$(grep "project_type:" "$STATUS_FILE" | head -1 | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"')
  fi
  if grep -q "project_level:" "$STATUS_FILE"; then
    PROJECT_LEVEL=$(grep "project_level:" "$STATUS_FILE" | head -1 | sed 's/.*: *//;s/ *#.*//')
  fi
fi

# Display header
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        BMAD Workflow Status Report            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Project:${NC} ${PROJECT_NAME}"
echo -e "${BLUE}Type:${NC} ${PROJECT_TYPE}"
echo -e "${BLUE}Level:${NC} ${PROJECT_LEVEL}"
echo ""

# Function to parse workflow status
parse_workflows() {
  local current_phase=0
  local phase_complete=true
  local recommended_workflow=""
  local phase_1_complete=true
  local phase_2_complete=false
  local phase_3_complete=false
  local phase_4_started=false

  # Headers
  echo -e "${GREEN}Phase 1: Analysis${NC} (Optional)"

  # Parse workflows using python3 to avoid nested while loop stdin consumption bug
  while IFS='|' read -r name phase status command; do
    # Print phase headers
    if [ "$phase" != "$current_phase" ]; then
      current_phase=$phase
      echo ""
      case $phase in
        2)
          echo -e "${GREEN}Phase 2: Planning${NC} (Required)"
          ;;
        3)
          echo -e "${GREEN}Phase 3: Solutioning${NC} (Conditional)"
          ;;
        4)
          echo -e "${GREEN}Phase 4: Implementation${NC} (Required)"
          ;;
      esac
    fi

    # Determine status icon and color
    if [[ $status == /* ]] || [[ $status == docs/* ]]; then
      # Completed - has file path
      echo -e "  ${GREEN}✓${NC} ${name} ${GRAY}(${status})${NC}"

      # Track phase completion
      case $phase in
        2) phase_2_complete=true ;;
        3) phase_3_complete=true ;;
        4) phase_4_started=true ;;
      esac
    elif [[ $status == "required" ]]; then
      echo -e "  ${YELLOW}⚠${NC} ${name} ${YELLOW}(required - NOT STARTED)${NC}"
      if [ -z "$recommended_workflow" ]; then
        recommended_workflow="$command"
      fi
      phase_complete=false
    elif [[ $status == "recommended" ]]; then
      echo -e "  ${BLUE}→${NC} ${name} ${BLUE}(recommended)${NC}"
      if [ -z "$recommended_workflow" ]; then
        recommended_workflow="$command"
      fi
    elif [[ $status == "skipped" ]]; then
      echo -e "  ${GRAY}-${NC} ${name} ${GRAY}(skipped)${NC}"
    else
      echo -e "  ${GRAY}-${NC} ${name} ${GRAY}(${status})${NC}"
    fi
  done < <(python3 -c "
import sys

with open(sys.argv[1]) as f:
    content = f.read()

workflows = []
current = {}
in_workflows = False

for line in content.split('\n'):
    stripped = line.strip()

    if stripped == 'workflow_status:':
        in_workflows = True
        continue

    if not in_workflows:
        continue

    if stripped.startswith('- name:'):
        if current:
            workflows.append(current)
        current = {'name': stripped[7:].strip().strip('\"')}
    elif current and stripped.startswith('phase:'):
        current['phase'] = stripped[6:].strip().strip('\"')
    elif current and stripped.startswith('status:'):
        current['status'] = stripped[7:].strip().strip('\"')
    elif current and stripped.startswith('command:'):
        current['command'] = stripped[8:].strip().strip('\"')
    elif current and stripped.startswith('description:'):
        current['description'] = stripped[12:].strip().strip('\"')

if current:
    workflows.append(current)

for wf in workflows:
    name = wf.get('name', '')
    phase = wf.get('phase', '')
    status = wf.get('status', '')
    command = wf.get('command', '')
    print(f'{name}|{phase}|{status}|{command}')
" "$STATUS_FILE" 2>/dev/null)

  # Recommendations
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  if [ -n "$recommended_workflow" ]; then
    echo ""
    echo -e "${YELLOW}Recommended next step:${NC}"
    echo -e "  Run ${GREEN}${recommended_workflow}${NC} to continue"
  else
    echo ""
    echo -e "${GREEN}All required workflows complete!${NC}"
    if [ "$phase_4_started" = true ]; then
      echo -e "Continue with ${GREEN}/dev-story${NC} to implement stories"
    else
      echo -e "Start implementation with ${GREEN}/sprint-planning${NC}"
    fi
  fi

  echo ""
}

# Parse and display workflows
parse_workflows

# Display legend
echo -e "${GRAY}Legend:${NC}"
echo -e "  ${GREEN}✓${NC} Completed    ${YELLOW}⚠${NC} Required    ${BLUE}→${NC} Recommended    ${GRAY}-${NC} Optional"
echo ""
