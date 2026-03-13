#!/bin/bash
# BMAD Project Initialization Script
# Creates BMAD directory structure and configuration files

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_NAME=""
PROJECT_TYPE=""
PROJECT_LEVEL=""
OUTPUT_FOLDER="docs"
SKILL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      PROJECT_NAME="$2"
      shift 2
      ;;
    --type)
      PROJECT_TYPE="$2"
      shift 2
      ;;
    --level)
      PROJECT_LEVEL="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FOLDER="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 --name <project-name> --type <project-type> --level <0-4> [--output <folder>]"
      echo ""
      echo "Options:"
      echo "  --name    Project name (required)"
      echo "  --type    Project type: web-app, mobile-app, api, game, library, other (required)"
      echo "  --level   Project level: 0-4 (required)"
      echo "  --output  Output folder for documents (default: docs)"
      echo "  -h, --help  Show this help message"
      echo ""
      echo "Example:"
      echo "  $0 --name MyApp --type web-app --level 2"
      exit 0
      ;;
    *)
      echo -e "${RED}Error: Unknown option $1${NC}"
      exit 1
      ;;
  esac
done

# Interactive mode if parameters not provided
if [ -z "$PROJECT_NAME" ]; then
  echo -e "${BLUE}Enter project name:${NC}"
  read -r PROJECT_NAME
fi

if [ -z "$PROJECT_TYPE" ]; then
  echo -e "${BLUE}Enter project type (web-app, mobile-app, api, game, library, other):${NC}"
  read -r PROJECT_TYPE
fi

if [ -z "$PROJECT_LEVEL" ]; then
  echo -e "${BLUE}Enter project level (0-4):${NC}"
  echo "  0 - Single atomic change (1 story)"
  echo "  1 - Small feature (1-10 stories)"
  echo "  2 - Medium feature set (5-15 stories)"
  echo "  3 - Complex integration (12-40 stories)"
  echo "  4 - Enterprise expansion (40+ stories)"
  read -r PROJECT_LEVEL
fi

# Validate inputs
if [ -z "$PROJECT_NAME" ] || [ -z "$PROJECT_TYPE" ] || [ -z "$PROJECT_LEVEL" ]; then
  echo -e "${RED}Error: Project name, type, and level are required${NC}"
  exit 1
fi

# Validate project level
if ! [[ "$PROJECT_LEVEL" =~ ^[0-4]$ ]]; then
  echo -e "${RED}Error: Project level must be 0-4${NC}"
  exit 1
fi

# Validate project type
valid_types=("web-app" "mobile-app" "api" "game" "library" "other")
if [[ ! " ${valid_types[@]} " =~ " ${PROJECT_TYPE} " ]]; then
  echo -e "${YELLOW}Warning: Unknown project type '${PROJECT_TYPE}'. Valid types: ${valid_types[*]}${NC}"
  echo -e "${YELLOW}Continuing anyway...${NC}"
fi

echo -e "${GREEN}Initializing BMAD for project: ${PROJECT_NAME}${NC}"
echo ""

# Create directory structure
echo -e "${BLUE}Creating directory structure...${NC}"

mkdir -p bmad/agent-overrides
mkdir -p "${OUTPUT_FOLDER}/stories"
mkdir -p .claude/commands/bmad

echo -e "${GREEN}✓ Directories created${NC}"

# Determine conditional workflow statuses based on project level
if [ "$PROJECT_LEVEL" -ge 2 ]; then
  PRD_STATUS="required"
else
  if [ "$PROJECT_LEVEL" -eq 1 ]; then
    PRD_STATUS="recommended"
  else
    PRD_STATUS="optional"
  fi
fi

if [ "$PROJECT_LEVEL" -le 1 ]; then
  TECH_SPEC_STATUS="required"
else
  TECH_SPEC_STATUS="optional"
fi

if [ "$PROJECT_LEVEL" -ge 2 ]; then
  ARCHITECTURE_STATUS="required"
else
  ARCHITECTURE_STATUS="optional"
fi

# Generate timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create project config from template
echo -e "${BLUE}Creating project configuration...${NC}"

CONFIG_TEMPLATE="${SKILL_PATH}/templates/config.template.yaml"
CONFIG_OUTPUT="bmad/config.yaml"

if [ -f "$CONFIG_TEMPLATE" ]; then
  # Use template if available
  sed -e "s/{{PROJECT_NAME}}/${PROJECT_NAME}/g" \
      -e "s/{{PROJECT_TYPE}}/${PROJECT_TYPE}/g" \
      -e "s/{{PROJECT_LEVEL}}/${PROJECT_LEVEL}/g" \
      -e "s/{{TIMESTAMP}}/${TIMESTAMP}/g" \
      "$CONFIG_TEMPLATE" > "$CONFIG_OUTPUT"
else
  # Fallback: create minimal config
  cat > "$CONFIG_OUTPUT" <<EOF
# BMAD Method v6 - Project Configuration
# Generated: ${TIMESTAMP}

bmad_version: "6.0.0"
project_name: "${PROJECT_NAME}"
project_type: "${PROJECT_TYPE}"
project_level: ${PROJECT_LEVEL}
output_folder: "${OUTPUT_FOLDER}"
stories_folder: "${OUTPUT_FOLDER}/stories"
communication_language: "English"
document_output_language: "English"
EOF
fi

echo -e "${GREEN}✓ Created: ${CONFIG_OUTPUT}${NC}"

# Create workflow status from template
echo -e "${BLUE}Creating workflow status file...${NC}"

STATUS_TEMPLATE="${SKILL_PATH}/templates/workflow-status.template.yaml"
STATUS_OUTPUT="${OUTPUT_FOLDER}/bmm-workflow-status.yaml"

if [ -f "$STATUS_TEMPLATE" ]; then
  # Use template if available
  sed -e "s/{{PROJECT_NAME}}/${PROJECT_NAME}/g" \
      -e "s/{{PROJECT_TYPE}}/${PROJECT_TYPE}/g" \
      -e "s/{{PROJECT_LEVEL}}/${PROJECT_LEVEL}/g" \
      -e "s/{{TIMESTAMP}}/${TIMESTAMP}/g" \
      -e "s/{{PRD_STATUS}}/${PRD_STATUS}/g" \
      -e "s/{{TECH_SPEC_STATUS}}/${TECH_SPEC_STATUS}/g" \
      -e "s/{{ARCHITECTURE_STATUS}}/${ARCHITECTURE_STATUS}/g" \
      "$STATUS_TEMPLATE" > "$STATUS_OUTPUT"
else
  # Fallback: create minimal status file
  cat > "$STATUS_OUTPUT" <<EOF
# BMAD Method Workflow Status
# Generated: ${TIMESTAMP}

project_name: "${PROJECT_NAME}"
project_type: "${PROJECT_TYPE}"
project_level: ${PROJECT_LEVEL}
last_updated: "${TIMESTAMP}"

workflow_status:
  - name: prd
    phase: 2
    status: "${PRD_STATUS}"
    description: "Product Requirements Document"

  - name: tech-spec
    phase: 2
    status: "${TECH_SPEC_STATUS}"
    description: "Technical Specification"

  - name: architecture
    phase: 3
    status: "${ARCHITECTURE_STATUS}"
    description: "System architecture design"

  - name: sprint-planning
    phase: 4
    status: "required"
    description: "Sprint planning and story creation"
EOF
fi

echo -e "${GREEN}✓ Created: ${STATUS_OUTPUT}${NC}"

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   BMAD Method Initialized Successfully!       ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${BLUE}Project:${NC} ${PROJECT_NAME}"
echo -e "${BLUE}Type:${NC} ${PROJECT_TYPE}"
echo -e "${BLUE}Level:${NC} ${PROJECT_LEVEL}"
echo ""
echo -e "${BLUE}Configuration:${NC} ${CONFIG_OUTPUT}"
echo -e "${BLUE}Status tracking:${NC} ${STATUS_OUTPUT}"
echo ""

# Recommend next step based on project level
echo -e "${YELLOW}Recommended next step:${NC}"
if [ "$PROJECT_LEVEL" -ge 2 ]; then
  echo -e "  Start with ${GREEN}/product-brief${NC} to define your product vision"
  echo -e "  Then create ${GREEN}/prd${NC} for detailed requirements"
else
  if [ "$PROJECT_LEVEL" -eq 1 ]; then
    echo -e "  Start with ${GREEN}/product-brief${NC} (recommended) or ${GREEN}/tech-spec${NC}"
  else
    echo -e "  Start with ${GREEN}/tech-spec${NC} to define your implementation"
  fi
fi

echo ""
echo -e "${BLUE}Check status anytime with:${NC} /workflow-status"
echo ""
