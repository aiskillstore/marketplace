#!/bin/bash
# setup-sandbox.sh - Create persistent validation container
# Part of code-validation-sandbox v3.0 (Reasoning-Activated)

set -euo pipefail

CONTAINER_NAME="code-validation-sandbox"
BASE_IMAGE="${1:-python:3.14-slim}"

echo "=== Code Validation Sandbox Setup ===" >&2
echo >&2

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Container '$CONTAINER_NAME' already exists" >&2

  # Check if running
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "✅ Container is running" >&2
    container_id=$(docker ps --filter "name=$CONTAINER_NAME" --format '{{.ID}}')
    echo "Container ID: $container_id" >&2
    exit 0
  else
    echo "Container exists but is stopped. Starting..." >&2
    docker start "$CONTAINER_NAME" >&2
    echo "✅ Container started" >&2
    exit 0
  fi
fi

echo "Creating new container with base image: $BASE_IMAGE" >&2
echo >&2

# Create persistent container
container_id=$(docker run -d \
  --name "$CONTAINER_NAME" \
  --mount type=bind,src="$(pwd)",dst=/workspace \
  "$BASE_IMAGE" \
  tail -f /dev/null)

echo "Container created: $container_id" >&2
echo >&2

# Install base tools
echo "Installing base tools..." >&2

docker exec "$CONTAINER_NAME" bash -c "
  set -e
  apt-get update -qq
  apt-get install -y -qq curl git build-essential > /dev/null 2>&1
  echo '✓ Base tools installed'
"

# Install Python tools (if Python base image)
if [[ $BASE_IMAGE == python:* ]]; then
  echo "Installing Python tools..." >&2

  docker exec "$CONTAINER_NAME" bash -c "
    set -e
    # Install UV package manager
    curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null 2>&1
    export PATH=\"\$HOME/.cargo/bin:\$PATH\"

    # Install common Python tools
    pip install --quiet pytest mypy ruff 2>/dev/null
    echo '✓ Python tools installed (UV, pytest, mypy, ruff)'
  "
fi

# Install Node.js (for multi-language support)
echo "Installing Node.js..." >&2

docker exec "$CONTAINER_NAME" bash -c "
  set -e
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1
  apt-get install -y -qq nodejs > /dev/null 2>&1
  npm install -g pnpm > /dev/null 2>&1
  echo '✓ Node.js 20 + pnpm installed'
"

echo >&2
echo "=== Setup Complete ===" >&2
echo "Container: $CONTAINER_NAME" >&2
echo "ID: $container_id" >&2
echo >&2
echo "Installed:" >&2
echo "  - Python 3.14 + UV + pytest + mypy + ruff" >&2
echo "  - Node.js 20 + pnpm" >&2
echo "  - Base tools (curl, git, build-essential)" >&2
echo >&2
echo "✅ Sandbox ready for validation" >&2
