#!/bin/bash

# Gate MCP One-Click Installer
# This script automates the setup of Gate MCP (mcporter) for OpenClaw

set -e

echo "=========================================="
echo "  Gate MCP (mcporter) Installer"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if npm is installed
echo "[Step 1/4] Checking npm installation..."
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed. Please install Node.js first.${NC}"
    echo "Visit: https://nodejs.org/ to download and install Node.js"
    exit 1
fi
echo -e "${GREEN}✓ npm is installed ($(npm --version))${NC}"
echo ""

# Step 2: Install mcporter
echo "[Step 2/4] Installing mcporter CLI..."
if command -v mcporter &> /dev/null; then
    echo -e "${YELLOW}⚠ mcporter is already installed ($(mcporter --version))${NC}"
    read -p "Do you want to reinstall/update? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Updating mcporter..."
        npm i -g mcporter
    fi
else
    echo "Installing mcporter globally..."
    npm i -g mcporter
fi

if ! command -v mcporter &> /dev/null; then
    echo -e "${RED}Error: mcporter installation failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ mcporter installed successfully ($(mcporter --version))${NC}"
echo ""

# Step 3: Configure Gate MCP
echo "[Step 3/4] Configuring Gate MCP server..."
GATE_URL="https://api.gatemcp.ai/mcp"

# Check if already configured
if mcporter config get gate &> /dev/null; then
    echo -e "${YELLOW}⚠ Gate MCP is already configured${NC}"
    CURRENT_URL=$(mcporter config get gate 2>/dev/null | grep -o '"url":"[^"]*"' | cut -d'"' -f4 || echo "")
    echo "Current URL: $CURRENT_URL"
    read -p "Do you want to reconfigure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mcporter config add gate "$GATE_URL" --scope home
    fi
else
    echo "Adding Gate MCP configuration..."
    mcporter config add gate "$GATE_URL" --scope home
fi
echo -e "${GREEN}✓ Gate MCP configured${NC}"
echo ""

# Step 4: Verify connectivity
echo "[Step 4/4] Verifying Gate MCP connectivity..."
echo "Testing connection to Gate MCP server..."

if mcporter list gate --schema &> /dev/null; then
    TOOL_COUNT=$(mcporter list gate --schema 2>&1 | grep -o "[0-9]* tools" | head -1 || echo "tools")
    echo -e "${GREEN}✓ Gate MCP is working! Found $TOOL_COUNT${NC}"
    echo ""
    echo "=========================================="
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "Available Gate MCP tools:"
    mcporter list gate --schema 2>&1 | head -30
    echo ""
    echo "You can now use Gate MCP in OpenClaw with queries like:"
    echo "  • 'check BTC/USDT price'"
    echo "  • 'use gate mcp to analyze SOL'"
    echo "  • 'what arbitrage opportunities are there on Gate?'"
else
    echo -e "${RED}✗ Connection test failed${NC}"
    echo "Please check your internet connection and try again."
    echo "If the problem persists, the Gate MCP server may be temporarily unavailable."
    exit 1
fi

echo ""
echo "Happy trading! 🚀"
