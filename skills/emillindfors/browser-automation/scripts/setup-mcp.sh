#!/bin/bash
# Setup script for rust-browser-mcp server
# This script helps configure the MCP server for use with Claude Desktop

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=== rust-browser-mcp Setup Script ==="
echo ""

# Check for required dependencies
check_dependencies() {
    echo "Checking dependencies..."

    # Check for Rust
    if ! command -v cargo &> /dev/null; then
        echo "ERROR: Rust/Cargo not found. Please install from https://rustup.rs"
        exit 1
    fi
    echo "✓ Rust/Cargo found"

    # Check for WebDrivers
    local driver_found=false

    if command -v chromedriver &> /dev/null; then
        echo "✓ ChromeDriver found"
        driver_found=true
    fi

    if command -v geckodriver &> /dev/null; then
        echo "✓ GeckoDriver found"
        driver_found=true
    fi

    if command -v msedgedriver &> /dev/null; then
        echo "✓ MSEdgeDriver found"
        driver_found=true
    fi

    if [ "$driver_found" = false ]; then
        echo "WARNING: No WebDriver found. Please install at least one:"
        echo "  - ChromeDriver: https://chromedriver.chromium.org/downloads"
        echo "  - GeckoDriver: https://github.com/mozilla/geckodriver/releases"
        echo "  - MSEdgeDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/"
    fi
}

# Build the project
build_project() {
    echo ""
    echo "Building rust-browser-mcp..."
    cd "$PROJECT_DIR"
    cargo build --release
    echo "✓ Build complete"
    echo "Binary location: $PROJECT_DIR/target/release/rust-browser-mcp"
}

# Generate Claude Desktop configuration
generate_config() {
    local binary_path="$PROJECT_DIR/target/release/rust-browser-mcp"
    local browser="${1:-chrome}"

    echo ""
    echo "Generating Claude Desktop configuration..."

    cat << EOF

Add the following to your Claude Desktop config file:

macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
Windows: %APPDATA%\\Claude\\claude_desktop_config.json
Linux: ~/.config/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "browser": {
      "command": "$binary_path",
      "args": ["--transport", "stdio", "--browser", "$browser"]
    }
  }
}

EOF
}

# Environment variable configuration
show_env_config() {
    echo ""
    echo "=== Optional Environment Variables ==="
    echo ""
    echo "WEBDRIVER_ENDPOINT=auto           # WebDriver URL or 'auto'"
    echo "WEBDRIVER_HEADLESS=true           # Run in headless mode"
    echo "WEBDRIVER_PREFERRED_DRIVER=chrome # Preferred browser"
    echo "WEBDRIVER_CONCURRENT_DRIVERS=firefox,chrome"
    echo "WEBDRIVER_POOL_ENABLED=true       # Enable connection pooling"
    echo "WEBDRIVER_POOL_MAX_CONNECTIONS=3  # Max connections per driver"
}

# Main
main() {
    check_dependencies

    read -p "Build the project? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_project
    fi

    read -p "Which browser do you prefer? (chrome/firefox/edge) [chrome]: " browser
    browser=${browser:-chrome}

    generate_config "$browser"
    show_env_config

    echo ""
    echo "=== Setup Complete ==="
    echo "Restart Claude Desktop to load the MCP server."
}

main "$@"
