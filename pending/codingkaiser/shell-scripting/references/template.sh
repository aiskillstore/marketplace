#!/usr/bin/env bash

# Script: template.sh
# Description: Production-ready Bash script template with best practices
# Usage: template.sh [OPTIONS] <command>

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Safer word splitting (newline and tab only)
IFS=$'\n\t'

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly VERSION="1.0.0"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Global variables
VERBOSE=false
DRY_RUN=false
LOG_FILE=""

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_debug() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $*" >&2
    fi
}

# Usage information
usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] <command> [args...]

Description of what this script does.

OPTIONS:
    -h, --help              Show this help message and exit
    -v, --verbose           Enable verbose output
    -d, --dry-run           Show what would be done without doing it
    -l, --log FILE          Write log output to FILE
    -V, --version           Show version information

COMMANDS:
    process <file>          Process the specified file
    batch <dir>             Process all files in directory
    clean                   Clean up temporary files

EXAMPLES:
    $SCRIPT_NAME --verbose process input.txt
    $SCRIPT_NAME --dry-run batch /path/to/files
    $SCRIPT_NAME clean

EOF
}

# Version information
version() {
    echo "$SCRIPT_NAME version $VERSION"
}

# Cleanup function (runs on EXIT)
cleanup() {
    local exit_code=$?
    log_debug "Cleaning up..."
    
    # Remove temporary files
    if [[ -n "${TEMP_FILE:-}" ]] && [[ -f "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
    fi
    
    # Additional cleanup tasks here
    
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script failed with exit code $exit_code"
    fi
}

# Error handler (runs on ERR)
error_handler() {
    local line_num=$1
    log_error "Error occurred in script at line $line_num"
}

# Set up traps
trap cleanup EXIT
trap 'error_handler $LINENO' ERR

# Command implementations
cmd_process() {
    local file=$1
    
    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi
    
    log_info "Processing file: $file"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would process: $file"
        return 0
    fi
    
    # Actual processing logic here
    log_debug "Processing contents of $file"
    
    log_success "Successfully processed: $file"
}

cmd_batch() {
    local dir=$1
    
    if [[ ! -d "$dir" ]]; then
        log_error "Directory not found: $dir"
        return 1
    fi
    
    log_info "Batch processing directory: $dir"
    
    local count=0
    while IFS= read -r -d '' file; do
        if cmd_process "$file"; then
            ((count++))
        fi
    done < <(find "$dir" -type f -name "*.txt" -print0)
    
    log_success "Processed $count files"
}

cmd_clean() {
    log_info "Cleaning up temporary files..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would remove temporary files"
        return 0
    fi
    
    # Clean up logic here
    
    log_success "Cleanup complete"
}

# Main entry point
main() {
    # Check if no arguments provided
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi
    
    # Parse command-line options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -V|--version)
                version
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                log_info "Dry run mode enabled"
                shift
                ;;
            -l|--log)
                if [[ -z "${2:-}" ]]; then
                    log_error "Option --log requires an argument"
                    exit 1
                fi
                LOG_FILE="$2"
                shift 2
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                # First non-option argument is the command
                break
                ;;
        esac
    done
    
    # Redirect output to log file if specified
    if [[ -n "$LOG_FILE" ]]; then
        exec 1> >(tee -a "$LOG_FILE")
        exec 2> >(tee -a "$LOG_FILE" >&2)
    fi
    
    # Get command
    local command="${1:-}"
    if [[ -z "$command" ]]; then
        log_error "No command specified"
        usage
        exit 1
    fi
    shift
    
    # Execute command
    case "$command" in
        process)
            if [[ $# -eq 0 ]]; then
                log_error "process command requires a file argument"
                exit 1
            fi
            cmd_process "$@"
            ;;
        batch)
            if [[ $# -eq 0 ]]; then
                log_error "batch command requires a directory argument"
                exit 1
            fi
            cmd_batch "$@"
            ;;
        clean)
            cmd_clean
            ;;
        *)
            log_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
