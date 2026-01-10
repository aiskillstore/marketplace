#!/bin/bash
# Architecture Scanner for DevPrep AI
# Scans the 7-folder structure and generates a compact architecture map

set -e

# Base directory (assumes script runs from project root)
BASE_DIR="${1:-.}"
SRC_DIR="$BASE_DIR/frontend/src"

echo "# DevPrep AI Architecture Map"
echo ""
echo "## 📁 7-Folder Structure"
echo ""

# Function to list directories and count files
list_structure() {
    local folder=$1
    local label=$2

    if [ -d "$SRC_DIR/$folder" ]; then
        echo "### $label ($folder/)"
        echo ""

        # Count files
        local file_count=$(find "$SRC_DIR/$folder" -type f -name "*.ts" -o -name "*.tsx" | wc -l | tr -d ' ')
        echo "**Files**: $file_count TypeScript/React files"
        echo ""

        # List subdirectories with descriptions
        if [ -d "$SRC_DIR/$folder" ]; then
            for dir in "$SRC_DIR/$folder"/*/ ; do
                if [ -d "$dir" ]; then
                    local dirname=$(basename "$dir")
                    local subfile_count=$(find "$dir" -type f \( -name "*.ts" -o -name "*.tsx" \) | wc -l | tr -d ' ')
                    echo "- **$dirname/** ($subfile_count files)"
                fi
            done
            echo ""
        fi
    fi
}

# Scan each of the 7 folders
list_structure "modules" "Modules (Domain Logic)"
list_structure "shared" "Shared (UI Components & Utils)"
list_structure "lib" "Lib (External Integrations)"
list_structure "store" "Store (Global State)"
list_structure "types" "Types (TypeScript Definitions)"
list_structure "styles" "Styles (Design System)"
list_structure "app" "App (Next.js Routes)"

echo "## 🎯 Key Locations"
echo ""

# API Layer
if [ -d "$SRC_DIR/lib/trpc" ]; then
    echo "**API Layer**: \`lib/trpc/\`"
    echo "- Routers: \`lib/trpc/routers/\`"
    echo "- Schemas: \`types/ai/api.ts\` (Zod schemas)"
    echo ""
fi

# State Management
if [ -d "$SRC_DIR/store" ]; then
    echo "**State Management**: \`store/\` (Zustand)"
    for slice in "$SRC_DIR/store"/*.ts; do
        if [ -f "$slice" ]; then
            slicename=$(basename "$slice" .ts)
            echo "- \`$slicename.ts\`"
        fi
    done
    echo ""
fi

# UI Components
if [ -d "$SRC_DIR/shared/components" ]; then
    echo "**UI Components**: \`shared/components/\`"
    echo ""
fi

echo "## 📊 Quick Stats"
echo ""

# Total file count
total_files=$(find "$SRC_DIR" -type f \( -name "*.ts" -o -name "*.tsx" \) | wc -l | tr -d ' ')
echo "- **Total TypeScript files**: $total_files"

# Module count
module_count=$(find "$SRC_DIR/modules" -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
echo "- **Feature modules**: $module_count"

# Component count (rough estimate)
component_count=$(find "$SRC_DIR/shared/components" -type f \( -name "*.tsx" \) 2>/dev/null | wc -l | tr -d ' ')
echo "- **Shared components**: ${component_count:-0}"

echo ""
echo "---"
echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
