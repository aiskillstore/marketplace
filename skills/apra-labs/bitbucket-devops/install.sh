#!/bin/bash
# Installation script for Claude Bitbucket DevOps Skill
# Validates prerequisites, builds in source, then deploys to Claude Code skills directory

set -e  # Exit on error

SKILL_NAME="bitbucket-devops"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.claude/skills/$SKILL_NAME"

echo "🚀 Installing Claude Bitbucket DevOps Skill..."
echo ""

# ========== PREREQUISITE CHECKS ==========

echo "🔍 Checking prerequisites..."
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is required but not installed"
    echo "   Please install Node.js from: https://nodejs.org/"
    echo "   Minimum version: v18"
    exit 1
fi
echo "✓ Node.js found: $(node --version)"

# Check for Git
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is required but not installed"
    echo "   Please install Git from: https://git-scm.com/"
    exit 1
fi
echo "✓ Git found: $(git --version)"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is required but not installed"
    echo "   npm should come with Node.js"
    exit 1
fi
echo "✓ npm found: $(npm --version)"

# Check if Claude Code is installed (look for .claude directory potential)
if [ ! -d "$HOME/.claude" ]; then
    echo "⚠️  Warning: Claude Code directory not found at ~/.claude"
    echo "   This might mean Claude Code is not installed or not configured yet."
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled"
        exit 1
    fi
fi

echo ""

# ========== REPOSITORY VALIDATION ==========

# Check if we're in a git repository
if [ ! -d "$SCRIPT_DIR/.git" ]; then
    echo "❌ Error: Not a git repository"
    echo "   Please clone the repository first:"
    echo "   git clone https://github.com/Apra-Labs/claude-bitbucket-devops-skill.git"
    exit 1
fi

# Check if .gitmodules exists
if [ ! -f "$SCRIPT_DIR/.gitmodules" ]; then
    echo "❌ Error: .gitmodules not found"
    echo "   This repository should have a bitbucket-mcp submodule"
    echo "   Please clone with: git clone --recursive"
    exit 1
fi

# Check if essential files exist
REQUIRED_FILES=("SKILL.md" "credentials.json.template" "lib/helpers.js")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ] && [ ! -d "$SCRIPT_DIR/$file" ]; then
        echo "❌ Error: Required file missing: $file"
        echo "   Repository may be corrupted. Try re-cloning."
        exit 1
    fi
done

echo "✓ Repository structure validated"
echo ""

# ========== SUBMODULE INITIALIZATION ==========

echo "📦 Initializing bitbucket-mcp submodule..."
cd "$SCRIPT_DIR"

# Initialize submodule
if ! git submodule update --init --recursive 2>/dev/null; then
    echo "❌ Error: Failed to initialize git submodule"
    echo "   This might be a git configuration issue"
    echo "   Try manually: cd $SCRIPT_DIR && git submodule update --init --recursive"
    exit 1
fi

echo "✓ Submodule initialized"
echo ""

# Verify submodule directory exists and has content
if [ ! -d "bitbucket-mcp" ] || [ -z "$(ls -A bitbucket-mcp)" ]; then
    echo "❌ Error: bitbucket-mcp submodule is empty"
    echo "   Try: git submodule update --init --recursive --force"
    exit 1
fi

# ========== BUILD ==========

echo "🔨 Building bitbucket-mcp..."
cd bitbucket-mcp

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in bitbucket-mcp"
    echo "   Submodule may not have been cloned correctly"
    exit 1
fi

# Install dependencies
echo "   Installing dependencies..."
if ! npm install --silent 2>&1 | grep -i "error" && npm install --silent > /dev/null 2>&1; then
    :
else
    echo "❌ Error: npm install failed"
    exit 1
fi

# Build TypeScript
echo "   Compiling TypeScript..."
if ! npm run build 2>&1 | grep -i "error" && npm run build > /dev/null 2>&1; then
    :
else
    echo "❌ Error: Build failed"
    exit 1
fi

cd "$SCRIPT_DIR"

# Verify build output
if [ ! -f "bitbucket-mcp/dist/index-cli.js" ]; then
    echo "❌ Error: Build output not found (dist/index-cli.js)"
    exit 1
fi

echo "✓ Build successful"
echo ""

# ========== DEPLOYMENT ==========

# Check if we're already in the target directory
if [ "$SCRIPT_DIR" = "$TARGET_DIR" ]; then
    echo "✓ Already in target directory: $TARGET_DIR"
    echo "✓ Build completed in place"
else
    echo "📍 Source location: $SCRIPT_DIR"
    echo "📍 Target location: $TARGET_DIR"
    echo ""

    # Backup user configuration if target exists
    BACKUP_DIR=""
    if [ -d "$TARGET_DIR" ]; then
        echo "⚠️  Target directory already exists"

        # Check if credentials.json exists and back it up
        if [ -f "$TARGET_DIR/credentials.json" ]; then
            BACKUP_DIR=$(mktemp -d)
            echo "💾 Backing up user credentials to temporary location"
            cp "$TARGET_DIR/credentials.json" "$BACKUP_DIR/credentials.json"
        fi

        echo "🗑️  Removing existing installation..."
        rm -rf "$TARGET_DIR"
    fi

    echo "📦 Deploying built files to Claude Code skills directory..."

    # Create skills directory if needed
    mkdir -p "$(dirname "$TARGET_DIR")"
    mkdir -p "$TARGET_DIR"

    # Copy only files needed by Claude (selective copy)
    echo "   Copying SKILL.md..."
    cp "$SCRIPT_DIR/SKILL.md" "$TARGET_DIR/"

    echo "   Copying credentials template..."
    cp "$SCRIPT_DIR/credentials.json.template" "$TARGET_DIR/"

    echo "   Copying package.json (required for ES modules)..."
    cp "$SCRIPT_DIR/package.json" "$TARGET_DIR/"

    echo "   Copying lib/ (helper scripts)..."
    cp -r "$SCRIPT_DIR/lib" "$TARGET_DIR/"

    echo "   Copying docs/ (referenced documentation)..."
    mkdir -p "$TARGET_DIR/docs"
    cp "$SCRIPT_DIR/docs/REFERENCE.md" "$TARGET_DIR/docs/"
    cp "$SCRIPT_DIR/docs/PATTERNS.md" "$TARGET_DIR/docs/"
    cp "$SCRIPT_DIR/docs/TROUBLESHOOTING.md" "$TARGET_DIR/docs/"
    cp "$SCRIPT_DIR/docs/GIT_OPERATIONS.md" "$TARGET_DIR/docs/"
    cp -r "$SCRIPT_DIR/docs/bitbucket-api" "$TARGET_DIR/docs/"

    echo "   Copying bitbucket-mcp/ (built CLI)..."
    mkdir -p "$TARGET_DIR/bitbucket-mcp"
    cp -r "$SCRIPT_DIR/bitbucket-mcp/dist" "$TARGET_DIR/bitbucket-mcp/"
    cp -r "$SCRIPT_DIR/bitbucket-mcp/node_modules" "$TARGET_DIR/bitbucket-mcp/"
    cp "$SCRIPT_DIR/bitbucket-mcp/package.json" "$TARGET_DIR/bitbucket-mcp/"

    echo "✓ Files copied to $TARGET_DIR"

    # Restore backed up credentials if they existed
    if [ -n "$BACKUP_DIR" ] && [ -f "$BACKUP_DIR/credentials.json" ]; then
        echo "♻️  Restoring user credentials"
        cp "$BACKUP_DIR/credentials.json" "$TARGET_DIR/credentials.json"
        rm -rf "$BACKUP_DIR"
        echo "✓ User credentials restored"
    fi

    echo ""

    cd "$TARGET_DIR"
fi

# ========== CREDENTIALS ==========

echo "📝 Setting up credentials..."

if [ ! -f "credentials.json" ]; then
    cp credentials.json.template credentials.json
    echo "✓ Created credentials.json from template"
    echo "⚠️  You MUST edit credentials.json with your Bitbucket credentials"
else
    echo "✓ credentials.json already exists (preserved from previous installation)"
fi

echo ""

# ========== COMPLETION ==========

echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ========== VALIDATION ==========

echo "🔬 Running validation tests..."
echo ""

# Run smoke test if available
if [ -f "$SCRIPT_DIR/smoke-test.sh" ]; then
    if bash "$SCRIPT_DIR/smoke-test.sh" "$TARGET_DIR"; then
        echo ""
        echo "✓ All validation tests passed!"
    else
        echo ""
        echo "⚠️  Some validation tests failed - please review output above"
        echo "   Installation may still work, but please verify manually"
    fi
else
    echo "⚠️  smoke-test.sh not found - skipping validation"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 NEXT STEPS:"
echo ""
echo "1️⃣  Configure your Bitbucket credentials:"
if [ "$SCRIPT_DIR" = "$TARGET_DIR" ]; then
    echo "    nano $SCRIPT_DIR/credentials.json"
else
    echo "    nano $TARGET_DIR/credentials.json"
fi
echo ""
echo "    Required info:"
echo "    - workspace: Your Bitbucket workspace slug"
echo "    - user_email: Your Bitbucket account email (for API auth)"
echo "    - username: Your Bitbucket username (same as workspace, for git ops)"
echo "    - password: App password (get from link below)"
echo ""
echo "    🔗 Get app password:"
echo "    https://bitbucket.org/account/settings/app-passwords/"
echo "    Required scopes: Repository (Read), Pipelines (Read, Write)"
echo ""
echo "2️⃣  Restart VSCode to load the skill"
echo ""
echo "3️⃣  Test the skill:"
echo "    - Open a Bitbucket project in VSCode"
echo "    - Ask Claude: \"What's the latest failed pipeline?\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Quick test command:"
if [ "$SCRIPT_DIR" = "$TARGET_DIR" ]; then
    echo "   node $SCRIPT_DIR/lib/helpers.js get-latest \"workspace\" \"repo\""
else
    echo "   node $TARGET_DIR/lib/helpers.js get-latest \"workspace\" \"repo\""
fi
echo ""
echo "📚 Documentation: $([ "$SCRIPT_DIR" = "$TARGET_DIR" ] && echo "$SCRIPT_DIR" || echo "$TARGET_DIR")/README.md"
echo ""
