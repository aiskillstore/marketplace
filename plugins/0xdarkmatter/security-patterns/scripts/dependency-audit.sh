#!/bin/bash
# Audit dependencies for known vulnerabilities
# Usage: ./dependency-audit.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Dependency Security Audit ==="
echo ""

# Python
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "--- Python Dependencies ---"

    if command -v pip-audit &> /dev/null; then
        echo "Running pip-audit..."
        pip-audit || true
    elif command -v safety &> /dev/null; then
        echo "Running safety check..."
        safety check || true
    else
        echo -e "${YELLOW}Install pip-audit or safety for Python vulnerability scanning${NC}"
        echo "  pip install pip-audit"
    fi
    echo ""
fi

# Node.js
if [ -f "package.json" ]; then
    echo "--- Node.js Dependencies ---"

    if command -v npm &> /dev/null; then
        echo "Running npm audit..."
        npm audit --audit-level=moderate || true
    fi
    echo ""
fi

# Go
if [ -f "go.mod" ]; then
    echo "--- Go Dependencies ---"

    if command -v govulncheck &> /dev/null; then
        echo "Running govulncheck..."
        govulncheck ./... || true
    else
        echo -e "${YELLOW}Install govulncheck for Go vulnerability scanning${NC}"
        echo "  go install golang.org/x/vuln/cmd/govulncheck@latest"
    fi
    echo ""
fi

# Rust
if [ -f "Cargo.toml" ]; then
    echo "--- Rust Dependencies ---"

    if command -v cargo-audit &> /dev/null; then
        echo "Running cargo audit..."
        cargo audit || true
    else
        echo -e "${YELLOW}Install cargo-audit for Rust vulnerability scanning${NC}"
        echo "  cargo install cargo-audit"
    fi
    echo ""
fi

# Docker
if [ -f "Dockerfile" ]; then
    echo "--- Docker Image ---"

    if command -v trivy &> /dev/null; then
        echo "Running trivy on Dockerfile..."
        trivy config Dockerfile || true
    else
        echo -e "${YELLOW}Install trivy for container vulnerability scanning${NC}"
        echo "  brew install trivy"
    fi
    echo ""
fi

echo "=== Audit Complete ==="
echo ""
echo "Recommended actions:"
echo "1. Update vulnerable packages to patched versions"
echo "2. Review advisories for workarounds if updates unavailable"
echo "3. Consider alternative packages for unmaintained dependencies"
