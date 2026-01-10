#!/bin/bash
# Slash Command: /doc-readme
# Description: Generate comprehensive README.md for the project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Configuration
PROJECT_ROOT=$(pwd)
README_FILE="$PROJECT_ROOT/README.md"
PACKAGE_JSON="$PROJECT_ROOT/package.json"
PYPROJECT_TOML="$PROJECT_ROOT/pyproject.toml"

# Parse arguments
OVERWRITE=false
INCLUDE_BADGES=true
INCLUDE_TOC=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --overwrite)
            OVERWRITE=true
            shift
            ;;
        --no-badges)
            INCLUDE_BADGES=false
            shift
            ;;
        --no-toc)
            INCLUDE_TOC=false
            shift
            ;;
        --help)
            echo "Usage: /doc-readme [options]"
            echo ""
            echo "Generate comprehensive README.md for the project"
            echo ""
            echo "Options:"
            echo "  --overwrite          Overwrite existing README.md"
            echo "  --no-badges          Don't include badges"
            echo "  --no-toc             Don't include table of contents"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  /doc-readme                    # Generate README (backs up existing)"
            echo "  /doc-readme --overwrite        # Overwrite existing README"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Run '/doc-readme --help' for usage information"
            exit 1
            ;;
    esac
done

# Print header
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  README.md Generation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Pre-task hook
print_info "Registering with swarm..."
npx claude-flow@alpha hooks pre-task \
    --description "README generation" \
    --agent "doc-generator" 2>/dev/null || true

# Check if README exists
if [ -f "$README_FILE" ] && [ "$OVERWRITE" = false ]; then
    BACKUP_FILE="$README_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    print_warning "README.md already exists"
    print_info "Creating backup: $BACKUP_FILE"
    cp "$README_FILE" "$BACKUP_FILE"
    print_success "Backup created"
fi

# Extract project information
print_info "Analyzing project..."

PROJECT_NAME=$(basename "$PROJECT_ROOT")
PROJECT_DESCRIPTION=""
PROJECT_VERSION="1.0.0"
PROJECT_LICENSE="MIT"
PROJECT_AUTHOR=""
REPO_URL=""

# Try to extract from package.json (Node.js)
if [ -f "$PACKAGE_JSON" ]; then
    if command -v jq &> /dev/null; then
        PROJECT_NAME=$(jq -r '.name // empty' "$PACKAGE_JSON" || echo "$PROJECT_NAME")
        PROJECT_DESCRIPTION=$(jq -r '.description // empty' "$PACKAGE_JSON" || echo "")
        PROJECT_VERSION=$(jq -r '.version // empty' "$PACKAGE_JSON" || echo "1.0.0")
        PROJECT_LICENSE=$(jq -r '.license // empty' "$PACKAGE_JSON" || echo "MIT")
        PROJECT_AUTHOR=$(jq -r '.author // empty' "$PACKAGE_JSON" || echo "")
        REPO_URL=$(jq -r '.repository.url // empty' "$PACKAGE_JSON" | sed 's/git+//; s/.git$//' || echo "")
        print_success "Extracted information from package.json"
    else
        print_warning "jq not installed, using defaults"
    fi
fi

# Try to extract from pyproject.toml (Python)
if [ -f "$PYPROJECT_TOML" ] && [ -z "$PROJECT_DESCRIPTION" ]; then
    if command -v python3 &> /dev/null; then
        PROJECT_NAME=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])" 2>/dev/null || echo "$PROJECT_NAME")
        PROJECT_DESCRIPTION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['description'])" 2>/dev/null || echo "")
        PROJECT_VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "1.0.0")
        print_success "Extracted information from pyproject.toml"
    fi
fi

# Get repository URL from git
if [ -z "$REPO_URL" ] && git rev-parse --git-dir > /dev/null 2>&1; then
    REPO_URL=$(git config --get remote.origin.url | sed 's/git@github.com:/https:\/\/github.com\//' | sed 's/.git$//')
fi

# Detect project type
PROJECT_TYPE="unknown"
if [ -f "$PACKAGE_JSON" ]; then
    if grep -q "\"react\"" "$PACKAGE_JSON" 2>/dev/null; then
        PROJECT_TYPE="react"
    elif grep -q "\"express\"" "$PACKAGE_JSON" 2>/dev/null; then
        PROJECT_TYPE="express"
    elif grep -q "\"next\"" "$PACKAGE_JSON" 2>/dev/null; then
        PROJECT_TYPE="nextjs"
    else
        PROJECT_TYPE="nodejs"
    fi
elif [ -f "$PYPROJECT_TOML" ]; then
    PROJECT_TYPE="python"
elif [ -f "go.mod" ]; then
    PROJECT_TYPE="go"
elif [ -f "Cargo.toml" ]; then
    PROJECT_TYPE="rust"
fi

print_success "Detected project type: $PROJECT_TYPE"

# Generate README
print_info "Generating README.md..."

cat > "$README_FILE" << EOF
# $PROJECT_NAME

EOF

# Add badges if requested
if [ "$INCLUDE_BADGES" = true ]; then
    cat >> "$README_FILE" << EOF
[![Build Status](https://img.shields.io/travis/username/$PROJECT_NAME.svg)](https://travis-ci.org/username/$PROJECT_NAME)
[![Coverage](https://img.shields.io/codecov/c/github/username/$PROJECT_NAME.svg)](https://codecov.io/gh/username/$PROJECT_NAME)
[![Version](https://img.shields.io/badge/version-$PROJECT_VERSION-blue.svg)](https://github.com/username/$PROJECT_NAME/releases)
[![License](https://img.shields.io/badge/license-$PROJECT_LICENSE-green.svg)](LICENSE)

EOF
fi

# Add description
if [ -n "$PROJECT_DESCRIPTION" ]; then
    cat >> "$README_FILE" << EOF
> $PROJECT_DESCRIPTION

EOF
else
    cat >> "$README_FILE" << EOF
> A comprehensive $PROJECT_TYPE project with modern development practices

EOF
fi

# Add table of contents if requested
if [ "$INCLUDE_TOC" = true ]; then
    cat >> "$README_FILE" << EOF
## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
- [Documentation](#documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

EOF
fi

# Add Features section
cat >> "$README_FILE" << EOF
## Features

- Modern $PROJECT_TYPE architecture
- Comprehensive test coverage
- Production-ready configuration
- CI/CD pipeline integration
- Detailed documentation

## Quick Start

### Prerequisites

EOF

# Add project-specific prerequisites
case $PROJECT_TYPE in
    "react"|"express"|"nextjs"|"nodejs")
        cat >> "$README_FILE" << EOF
- Node.js >= 18.0.0
- npm >= 9.0.0 or yarn >= 1.22.0

EOF
        ;;
    "python")
        cat >> "$README_FILE" << EOF
- Python >= 3.9
- pip >= 21.0

EOF
        ;;
    "go")
        cat >> "$README_FILE" << EOF
- Go >= 1.20

EOF
        ;;
    "rust")
        cat >> "$README_FILE" << EOF
- Rust >= 1.70
- Cargo >= 1.70

EOF
        ;;
esac

# Add Installation section
cat >> "$README_FILE" << EOF
### Installation

\`\`\`bash
# Clone the repository
git clone ${REPO_URL:-https://github.com/username/$PROJECT_NAME.git}
cd $PROJECT_NAME

EOF

# Add project-specific installation
case $PROJECT_TYPE in
    "react"|"express"|"nextjs"|"nodejs")
        cat >> "$README_FILE" << EOF
# Install dependencies
npm install

# Or using yarn
yarn install
EOF
        ;;
    "python")
        cat >> "$README_FILE" << EOF
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or using poetry
poetry install
EOF
        ;;
    "go")
        cat >> "$README_FILE" << EOF
# Download dependencies
go mod download
EOF
        ;;
    "rust")
        cat >> "$README_FILE" << EOF
# Build project
cargo build
EOF
        ;;
esac

cat >> "$README_FILE" << EOF
\`\`\`

### Usage

EOF

# Add project-specific usage
case $PROJECT_TYPE in
    "express"|"nodejs")
        cat >> "$README_FILE" << EOF
\`\`\`bash
# Development mode
npm run dev

# Production mode
npm start
\`\`\`

The server will start on http://localhost:3000

EOF
        ;;
    "react"|"nextjs")
        cat >> "$README_FILE" << EOF
\`\`\`bash
# Development mode
npm run dev

# Build for production
npm run build

# Start production server
npm start
\`\`\`

Open http://localhost:3000 in your browser.

EOF
        ;;
    "python")
        cat >> "$README_FILE" << EOF
\`\`\`bash
# Run application
python main.py

# Or with module
python -m $PROJECT_NAME
\`\`\`

EOF
        ;;
    "go")
        cat >> "$README_FILE" << EOF
\`\`\`bash
# Run application
go run main.go

# Build executable
go build -o $PROJECT_NAME
./$PROJECT_NAME
\`\`\`

EOF
        ;;
    "rust")
        cat >> "$README_FILE" << EOF
\`\`\`bash
# Run application
cargo run

# Build release
cargo build --release
./target/release/$PROJECT_NAME
\`\`\`

EOF
        ;;
esac

# Add remaining sections
cat >> "$README_FILE" << EOF
## Documentation

- [API Reference](docs/api/README.md) - Complete API documentation
- [Architecture](docs/architecture/overview.md) - System architecture and design
- [Configuration](docs/configuration.md) - Configuration options
- [Examples](docs/examples/) - Usage examples and tutorials

## Development

### Project Structure

\`\`\`
$PROJECT_NAME/
├── src/                # Source code
├── tests/              # Test files
├── docs/               # Documentation
├── config/             # Configuration files
└── scripts/            # Utility scripts
\`\`\`

### Development Scripts

\`\`\`bash
# Run tests
npm test

# Run linter
npm run lint

# Format code
npm run format

# Type checking
npm run typecheck
\`\`\`

## Testing

\`\`\`bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- path/to/test.spec.js
\`\`\`

## Deployment

See [Deployment Guide](docs/deployment.md) for detailed deployment instructions.

### Quick Deploy

\`\`\`bash
# Build for production
npm run build

# Deploy (example with Vercel)
vercel deploy --prod
\`\`\`

## Configuration

Key configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| \`PORT\` | Server port | 3000 |
| \`NODE_ENV\` | Environment | development |
| \`DATABASE_URL\` | Database connection | - |

See [.env.example](.env.example) for all available options.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Process

1. Fork the repository
2. Create a feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'Add amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

## Support

- Documentation: ${REPO_URL:+$REPO_URL/wiki}
- Issues: ${REPO_URL:+$REPO_URL/issues}
- Discussions: ${REPO_URL:+$REPO_URL/discussions}

## License

$PROJECT_LICENSE © $(date +%Y) ${PROJECT_AUTHOR:-Your Name}

See [LICENSE](LICENSE) for details.

---

**Built with** ❤️ **by** ${PROJECT_AUTHOR:-the community}
**Last Updated**: $(date +"%Y-%m-%d")
EOF

print_success "Generated: $README_FILE"

# Notify progress
npx claude-flow@alpha hooks notify \
    --message "README.md generated" \
    --agent "doc-generator" 2>/dev/null || true

# Store results in memory
npx claude-flow@alpha memory store \
    --key "swarm/doc-generator/readme" \
    --value "{\"file\": \"$README_FILE\", \"type\": \"$PROJECT_TYPE\"}" 2>/dev/null || true

# Post-task hook
npx claude-flow@alpha hooks post-task \
    --task-id "readme-generation" 2>/dev/null || true

# Print summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "README.md generated successfully"
echo ""
echo "Project Details:"
echo "  • Name:          $PROJECT_NAME"
echo "  • Version:       $PROJECT_VERSION"
echo "  • Type:          $PROJECT_TYPE"
echo "  • License:       $PROJECT_LICENSE"
echo ""
echo "Generated File:"
echo "  • $README_FILE"
echo ""
echo "Next Steps:"
echo "  1. Review and customize the README"
echo "  2. Add project screenshots"
echo "  3. Update badge URLs"
echo "  4. Add specific usage examples"
echo "  5. Configure contributing guidelines"
echo ""

exit 0
