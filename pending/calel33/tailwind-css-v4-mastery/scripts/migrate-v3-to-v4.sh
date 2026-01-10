#!/bin/bash
#
# Tailwind CSS v3 → v4 Migration Script
# This script automates the common migration patterns
# 
# Usage: bash migrate-v3-to-v4.sh [project-directory]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="${1:-.}"
BACKUP_DIR="${PROJECT_DIR}/.tailwind-v3-backup"

echo -e "${BLUE}Tailwind CSS v3 → v4 Migration Tool${NC}\n"

# Function to print status
status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print warning
warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# 1. Backup existing files
echo -e "${BLUE}[1/6] Backing up existing files...${NC}"
mkdir -p "$BACKUP_DIR"

if [ -f "$PROJECT_DIR/tailwind.config.js" ]; then
    cp "$PROJECT_DIR/tailwind.config.js" "$BACKUP_DIR/"
    status "Backed up tailwind.config.js"
fi

if [ -f "$PROJECT_DIR/package.json" ]; then
    cp "$PROJECT_DIR/package.json" "$BACKUP_DIR/"
    status "Backed up package.json"
fi

# 2. Update package.json dependencies
echo -e "\n${BLUE}[2/6] Updating package.json...${NC}"
if [ -f "$PROJECT_DIR/package.json" ]; then
    # Remove old tailwindcss version
    cd "$PROJECT_DIR"
    npm install -D tailwindcss@latest
    
    # Determine which plugin to install
    if [ -f "vite.config.js" ] || [ -f "vite.config.ts" ]; then
        npm install -D "@tailwindcss/vite"
        status "Added @tailwindcss/vite (detected Vite project)"
    elif [ -f "next.config.js" ]; then
        npm install -D "@tailwindcss/postcss"
        status "Added @tailwindcss/postcss (detected Next.js project)"
    else
        npm install -D "@tailwindcss/postcss"
        status "Added @tailwindcss/postcss (PostCSS setup)"
    fi
fi

# 3. Find and update CSS import statements
echo -e "\n${BLUE}[3/6] Updating CSS imports...${NC}"
find "$PROJECT_DIR" -type f \( -name "*.css" -o -name "*.scss" \) | while read -r file; do
    if grep -q "@tailwind" "$file"; then
        sed -i.bak \
            -e 's/@tailwind base;//g' \
            -e 's/@tailwind components;//g' \
            -e 's/@tailwind utilities;//g' \
            "$file"
        
        # Add @import "tailwindcss" if not already present
        if ! grep -q '@import "tailwindcss"' "$file"; then
            sed -i.bak '1s/^/@import "tailwindcss";\n/' "$file"
        fi
        
        status "Updated imports in $(basename $file)"
        rm -f "$file.bak"
    fi
done

# 4. Find and replace utility class names
echo -e "\n${BLUE}[4/6] Migrating utility class names...${NC}"

UTILITY_PATTERNS=(
    # Shadows
    's/\.shadow\b/.shadow-sm/g'
    's/\.shadow-sm\b/.shadow-xs/g'
    # Rounded
    's/\.rounded\b/.rounded-sm/g'
    's/\.rounded-sm\b/.rounded-xs/g'
    # Outline
    's/\.outline-none\b/.outline-hidden/g'
    # Ring (replace standalone .ring with .ring-1)
    's/\.ring\b/.ring-1/g'
    # Opacity utilities
    's/\.bg-opacity-0\b/.bg-black\/0/g'
    's/\.bg-opacity-5\b/.bg-black\/5/g'
    's/\.bg-opacity-10\b/.bg-black\/10/g'
    's/\.bg-opacity-20\b/.bg-black\/20/g'
    's/\.bg-opacity-25\b/.bg-black\/25/g'
    's/\.bg-opacity-30\b/.bg-black\/30/g'
    's/\.bg-opacity-40\b/.bg-black\/40/g'
    's/\.bg-opacity-50\b/.bg-black\/50/g'
    's/\.bg-opacity-60\b/.bg-black\/60/g'
    's/\.bg-opacity-70\b/.bg-black\/70/g'
    's/\.bg-opacity-75\b/.bg-black\/75/g'
    's/\.bg-opacity-80\b/.bg-black\/80/g'
    's/\.bg-opacity-90\b/.bg-black\/90/g'
    's/\.bg-opacity-95\b/.bg-black\/95/g'
    # Typography
    's/\.overflow-ellipsis\b/.text-ellipsis/g'
    # Flexbox
    's/\.flex-grow-0\b/.grow-0/g'
    's/\.flex-grow-1\b/.grow/g'
    's/\.flex-grow\b/.grow/g'
    's/\.flex-shrink-0\b/.shrink-0/g'
    's/\.flex-shrink\b/.shrink/g'
)

# Apply patterns to HTML/JSX/Vue files
find "$PROJECT_DIR" -type f \( -name "*.html" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.vue" \) | while read -r file; do
    for pattern in "${UTILITY_PATTERNS[@]}"; do
        sed -i.bak "$pattern" "$file"
    done
    rm -f "$file.bak"
    status "Migrated utilities in $(basename $file)"
done

# 5. Remove tailwind.config.js
echo -e "\n${BLUE}[5/6] Cleaning up old configuration...${NC}"
if [ -f "$PROJECT_DIR/tailwind.config.js" ]; then
    rm "$PROJECT_DIR/tailwind.config.js"
    status "Removed tailwind.config.js (now using CSS configuration)"
    warn "You'll need to add @theme block to your CSS file with any custom config"
fi

# 6. Summary
echo -e "\n${BLUE}[6/6] Migration Complete!${NC}\n"

echo -e "${GREEN}Next Steps:${NC}"
echo "1. Review .css files - ensure @import \"tailwindcss\" is at the top"
echo "2. Add any custom theme to @theme { } block in your CSS"
echo "3. Test your build: npm run build"
echo "4. Check for any broken layouts due to default value changes:"
echo "   - Border colors (changed from currentColor to gray-200)"
echo "   - Ring widths (changed from 3px to 1px)"
echo ""
echo -e "${YELLOW}Backup location: $BACKUP_DIR${NC}"
echo -e "${YELLOW}Original files available if needed for reference${NC}"
echo ""
echo -e "${GREEN}Documentation: references/breaking-changes.md${NC}"

