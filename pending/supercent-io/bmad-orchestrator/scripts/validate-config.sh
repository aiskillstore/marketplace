#!/bin/bash
# BMAD Configuration Validator
# Validates YAML configuration files for syntax and required fields

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default file to validate
CONFIG_FILE="${1:-bmad/config.yaml}"

# Check if file exists
if [ ! -f "$CONFIG_FILE" ]; then
  echo -e "${RED}Error: File not found: ${CONFIG_FILE}${NC}"
  exit 1
fi

echo -e "${BLUE}Validating YAML configuration: ${CONFIG_FILE}${NC}"
echo ""

# Track validation status
ERRORS=0
WARNINGS=0

# Function to report error
error() {
  echo -e "${RED}✗ ERROR:${NC} $1"
  ((ERRORS++))
}

# Function to report warning
warning() {
  echo -e "${YELLOW}⚠ WARNING:${NC} $1"
  ((WARNINGS++))
}

# Function to report success
success() {
  echo -e "${GREEN}✓${NC} $1"
}

# Check if yq is available for proper YAML parsing
HAS_YQ=false
if command -v yq &> /dev/null; then
  HAS_YQ=true
  echo -e "${GREEN}✓ yq found - using proper YAML parser${NC}"
else
  echo -e "${YELLOW}⚠ yq not found - using basic validation${NC}"
  echo -e "${GRAY}  Install yq for better validation: https://github.com/mikefarah/yq${NC}"
fi
echo ""

# Test 1: YAML Syntax
echo -e "${BLUE}Test 1: YAML Syntax${NC}"
if [ "$HAS_YQ" = true ]; then
  if yq eval '.' "$CONFIG_FILE" > /dev/null 2>&1; then
    success "Valid YAML syntax"
  else
    error "Invalid YAML syntax"
    yq eval '.' "$CONFIG_FILE" 2>&1 | head -5
  fi
else
  # Basic syntax check
  if grep -q "^[^#]" "$CONFIG_FILE"; then
    success "File contains content"
  else
    error "File appears empty or only contains comments"
  fi
fi
echo ""

# Determine config type
CONFIG_TYPE="unknown"
if grep -q "project_name:" "$CONFIG_FILE"; then
  CONFIG_TYPE="project"
elif grep -q "user_name:" "$CONFIG_FILE"; then
  CONFIG_TYPE="global"
fi

echo -e "${BLUE}Configuration type: ${CONFIG_TYPE}${NC}"
echo ""

# Test 2: Required Fields (Project Config)
if [ "$CONFIG_TYPE" = "project" ]; then
  echo -e "${BLUE}Test 2: Required Fields (Project Config)${NC}"

  # Check project_name
  if grep -q "^project_name:" "$CONFIG_FILE"; then
    PROJECT_NAME=$(grep "^project_name:" "$CONFIG_FILE" | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"')
    if [ -n "$PROJECT_NAME" ]; then
      success "project_name: ${PROJECT_NAME}"
    else
      error "project_name is empty"
    fi
  else
    error "Missing required field: project_name"
  fi

  # Check project_type
  if grep -q "^project_type:" "$CONFIG_FILE"; then
    PROJECT_TYPE=$(grep "^project_type:" "$CONFIG_FILE" | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"')
    if [ -n "$PROJECT_TYPE" ]; then
      success "project_type: ${PROJECT_TYPE}"
      # Validate project type
      valid_types=("web-app" "mobile-app" "api" "game" "library" "other")
      if [[ ! " ${valid_types[@]} " =~ " ${PROJECT_TYPE} " ]]; then
        warning "Unknown project_type '${PROJECT_TYPE}'. Valid: ${valid_types[*]}"
      fi
    else
      error "project_type is empty"
    fi
  else
    error "Missing required field: project_type"
  fi

  # Check project_level
  if grep -q "^project_level:" "$CONFIG_FILE"; then
    PROJECT_LEVEL=$(grep "^project_level:" "$CONFIG_FILE" | sed 's/.*: *//;s/ *#.*//')
    if [ -n "$PROJECT_LEVEL" ]; then
      success "project_level: ${PROJECT_LEVEL}"
      # Validate level is 0-4
      if ! [[ "$PROJECT_LEVEL" =~ ^[0-4]$ ]]; then
        error "project_level must be 0-4, got: ${PROJECT_LEVEL}"
      fi
    else
      error "project_level is empty"
    fi
  else
    error "Missing required field: project_level"
  fi

  echo ""
fi

# Test 3: Optional but Recommended Fields
echo -e "${BLUE}Test 3: Optional Fields${NC}"

# Check output_folder
if grep -q "^output_folder:" "$CONFIG_FILE"; then
  OUTPUT_FOLDER=$(grep "^output_folder:" "$CONFIG_FILE" | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"')
  success "output_folder: ${OUTPUT_FOLDER}"
else
  warning "output_folder not specified (will default to 'docs')"
fi

# Check communication_language
if grep -q "^communication_language:" "$CONFIG_FILE"; then
  COMM_LANG=$(grep "^communication_language:" "$CONFIG_FILE" | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"')
  success "communication_language: ${COMM_LANG}"
else
  warning "communication_language not specified (will default to 'English')"
fi

echo ""

# Test 4: BMAD Version
echo -e "${BLUE}Test 4: Version Check${NC}"
if grep -q "^bmad_version:" "$CONFIG_FILE" || grep -q "^version:" "$CONFIG_FILE"; then
  VERSION=$(grep -E "^(bmad_version|version):" "$CONFIG_FILE" | head -1 | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"')
  success "BMAD version: ${VERSION}"

  # Check if version is current
  if [[ "$VERSION" == "6.0.0" ]]; then
    success "Running latest BMAD version"
  else
    warning "BMAD version ${VERSION} detected. Current version is 6.0.0"
  fi
else
  warning "No version specified"
fi

echo ""

# Test 5: File Permissions
echo -e "${BLUE}Test 5: File Permissions${NC}"
if [ -r "$CONFIG_FILE" ]; then
  success "File is readable"
else
  error "File is not readable"
fi

if [ -w "$CONFIG_FILE" ]; then
  success "File is writable"
else
  warning "File is not writable (updates may fail)"
fi

echo ""

# Test 6: Referenced Folders (if project config)
if [ "$CONFIG_TYPE" = "project" ]; then
  echo -e "${BLUE}Test 6: Referenced Folders${NC}"

  # Check if output folder exists
  if [ -n "$OUTPUT_FOLDER" ]; then
    if [ -d "$OUTPUT_FOLDER" ]; then
      success "Output folder exists: ${OUTPUT_FOLDER}"
    else
      warning "Output folder does not exist: ${OUTPUT_FOLDER}"
      echo -e "  ${GRAY}Run /workflow-init to create it${NC}"
    fi
  fi

  # Check if bmad folder exists
  if [ -d "bmad" ]; then
    success "BMAD config folder exists: bmad/"
  else
    warning "BMAD config folder does not exist: bmad/"
  fi

  # Check for workflow status file
  STATUS_FILE="${OUTPUT_FOLDER:-docs}/bmm-workflow-status.yaml"
  if [ -f "$STATUS_FILE" ]; then
    success "Workflow status file exists: ${STATUS_FILE}"
  else
    warning "Workflow status file not found: ${STATUS_FILE}"
    echo -e "  ${GRAY}Run /workflow-init to create it${NC}"
  fi

  echo ""
fi

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✓ Validation passed with no errors or warnings!${NC}"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠ Validation passed with ${WARNINGS} warning(s)${NC}"
  echo -e "${GRAY}  Configuration is valid but has recommendations${NC}"
  exit 0
else
  echo -e "${RED}✗ Validation failed with ${ERRORS} error(s) and ${WARNINGS} warning(s)${NC}"
  echo -e "${GRAY}  Please fix errors before proceeding${NC}"
  exit 1
fi
