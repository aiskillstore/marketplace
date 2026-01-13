#!/bin/bash
# Helper script for standard plugin
# This is an example helper script that can be called by commands or agents

set -e  # Exit on error

function show_help() {
    echo "Usage: helper.sh [command] [args]"
    echo ""
    echo "Commands:"
    echo "  find <pattern>    Find files matching pattern"
    echo "  validate <file>   Validate file syntax"
    echo "  help              Show this help message"
}

function find_files() {
    local pattern="$1"
    if [ -z "$pattern" ]; then
        echo "Error: Pattern required"
        exit 1
    fi

    echo "Searching for files matching: $pattern"
    find . -name "$pattern" -type f
}

function validate_file() {
    local file="$1"
    if [ -z "$file" ]; then
        echo "Error: File path required"
        exit 1
    fi

    if [ ! -f "$file" ]; then
        echo "Error: File not found: $file"
        exit 1
    fi

    echo "Validating: $file"
    # Add validation logic here
    echo "✓ File is valid"
}

# Main command dispatcher
case "$1" in
    find)
        find_files "$2"
        ;;
    validate)
        validate_file "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Error: Unknown command: $1"
        show_help
        exit 1
        ;;
esac
