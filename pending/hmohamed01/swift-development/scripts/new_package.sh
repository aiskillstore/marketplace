#!/bin/bash
# Creates a new Swift package with common configuration
# Usage: new_package.sh <name> [--type library|executable|empty] [--ios] [--macos] [--swift-version 5.10|6.0]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "${GREEN}==>${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

echo_error() {
    echo -e "${RED}Error:${NC} $1" >&2
}

# Check prerequisites
if ! command -v swift &> /dev/null; then
    echo_error "swift is not available. Install Xcode Command Line Tools: xcode-select --install"
    exit 1
fi

NAME="${1:?Usage: new_package.sh <name> [--type library|executable|empty] [--ios] [--macos] [--swift-version 5.10|6.0]}"
TYPE="library"
PLATFORMS=""
SWIFT_VERSION="5.10"

# Get script directory to find assets
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../assets"
if [[ -d "$ASSETS_DIR" ]]; then
    ASSETS_DIR="$(cd "$ASSETS_DIR" && pwd)"
else
    ASSETS_DIR=""  # Assets not available, will use inline configs
fi

shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --type) TYPE="$2"; shift 2 ;;
        --ios) PLATFORMS="${PLATFORMS}iOS "; shift ;;
        --macos) PLATFORMS="${PLATFORMS}macOS "; shift ;;
        --swift-version) SWIFT_VERSION="$2"; shift 2 ;;
        *) echo_error "Unknown option: $1"; echo "Usage: new_package.sh <name> [--type library|executable|empty] [--ios] [--macos] [--swift-version 5.10|6.0]" >&2; exit 1 ;;
    esac
done

# Check Swift version compatibility
INSTALLED_SWIFT_VERSION=$(swift --version 2>/dev/null | grep -oE 'Swift version [0-9]+\.[0-9]+' | grep -oE '[0-9]+\.[0-9]+' | head -1)
if [[ -n "$INSTALLED_SWIFT_VERSION" ]]; then
    # Compare versions (basic major.minor comparison)
    INSTALLED_MAJOR="${INSTALLED_SWIFT_VERSION%%.*}"
    INSTALLED_MINOR="${INSTALLED_SWIFT_VERSION#*.}"
    INSTALLED_MINOR="${INSTALLED_MINOR%%.*}"  # Remove any patch version
    REQUESTED_MAJOR="${SWIFT_VERSION%%.*}"
    REQUESTED_MINOR="${SWIFT_VERSION#*.}"
    REQUESTED_MINOR="${REQUESTED_MINOR%%.*}"  # Remove any patch version

    if [[ "$REQUESTED_MAJOR" -gt "$INSTALLED_MAJOR" ]] || \
       [[ "$REQUESTED_MAJOR" -eq "$INSTALLED_MAJOR" && "$REQUESTED_MINOR" -gt "$INSTALLED_MINOR" ]]; then
        echo_warning "Requested Swift $SWIFT_VERSION but installed version is $INSTALLED_SWIFT_VERSION."
        echo "         Package.swift will target $SWIFT_VERSION but local builds use $INSTALLED_SWIFT_VERSION."
    fi
fi

# Check Xcode version for Swift 6.0+ compatibility
if [[ "${SWIFT_VERSION%%.*}" -ge 6 ]]; then
    XCODE_VERSION=$(xcodebuild -version 2>/dev/null | grep "Xcode" | grep -oE '[0-9]+' | head -1)
    if [[ -n "$XCODE_VERSION" && "$XCODE_VERSION" -lt 16 ]]; then
        echo_warning "Swift $SWIFT_VERSION requires Xcode 16+. Detected Xcode $XCODE_VERSION."
        echo "         Update Xcode or use --swift-version 5.10 for compatibility."
    fi
fi

# Validate package name
if [[ ! "$NAME" =~ ^[a-zA-Z][a-zA-Z0-9_-]*$ ]]; then
    echo_error "Invalid package name '$NAME'. Must start with a letter and contain only alphanumeric characters, hyphens, and underscores."
    exit 1
fi

# Warn about naming conventions
# PascalCase: starts with uppercase, contains at least one lowercase (unless single char)
if [[ ! "$NAME" =~ ^[A-Z][a-zA-Z0-9]*$ ]] || [[ ${#NAME} -gt 1 && ! "$NAME" =~ [a-z] ]]; then
    echo_warning "Package name '$NAME' doesn't follow Swift PascalCase convention (e.g., 'NetworkKit', 'MyPackage')."
    echo "         This is valid but unconventional for Swift packages."
fi

# Check if directory already exists
if [[ -e "$NAME" ]]; then
    echo_error "Directory '$NAME' already exists."
    exit 1
fi

# Warn if creating inside an existing git repository
if git rev-parse --is-inside-work-tree &>/dev/null; then
    REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
    echo_warning "Creating package inside existing git repository: $REPO_ROOT"
    echo "         Consider using 'git submodule add' if this should be a separate repo."
fi

echo_step "Creating Swift package: $NAME (type: $TYPE, Swift $SWIFT_VERSION)"

# Create package
if ! swift package init --type "$TYPE" --name "$NAME"; then
    echo_error "Failed to create Swift package"
    exit 1
fi

cd "$NAME"

# If platforms specified, update Package.swift
if [[ -n "$PLATFORMS" ]]; then
    echo_step "Adding platform support: $PLATFORMS"

    # Build platforms array
    PLATFORM_ARRAY=""
    [[ "$PLATFORMS" == *"iOS"* ]] && PLATFORM_ARRAY="${PLATFORM_ARRAY}.iOS(.v15), "
    [[ "$PLATFORMS" == *"macOS"* ]] && PLATFORM_ARRAY="${PLATFORM_ARRAY}.macOS(.v13), "
    PLATFORM_ARRAY="${PLATFORM_ARRAY%, }"

    # Insert platforms into Package.swift after 'name:'
    sed -i '' "s/name: \"$NAME\"/name: \"$NAME\",\n    platforms: [$PLATFORM_ARRAY]/" Package.swift
fi

# Create standard directories
echo_step "Creating directory structure..."
mkdir -p Sources/$NAME/{Models,Services,Utilities}
mkdir -p Tests/${NAME}Tests

# Add .gitignore
cat > .gitignore << 'EOF'
.DS_Store
/.build
/Packages
xcuserdata/
DerivedData/
.swiftpm/
*.xcodeproj
Package.resolved
EOF

# Add SwiftFormat config (use asset if available, otherwise create inline)
if [[ -n "$ASSETS_DIR" && -f "$ASSETS_DIR/.swiftformat" ]]; then
    echo_step "Using SwiftFormat config from assets..."
    cp "$ASSETS_DIR/.swiftformat" .swiftformat
    # Update swiftversion if different
    if [[ "$SWIFT_VERSION" != "5.10" ]]; then
        sed -i '' "s/--swiftversion 5.10/--swiftversion $SWIFT_VERSION/" .swiftformat 2>/dev/null || \
        sed -i '' "s/--swiftversion .*/--swiftversion $SWIFT_VERSION/" .swiftformat 2>/dev/null || true
    fi
else
    echo_step "Creating SwiftFormat config..."
    cat > .swiftformat << EOF
--indent 4
--indentcase false
--trimwhitespace always
--voidtype void
--wraparguments before-first
--wrapcollections before-first
--maxwidth 120
--swiftversion $SWIFT_VERSION
--exclude Pods,Generated,*.generated.swift
--disable redundantSelf
--enable isEmpty
EOF
fi

# Add SwiftLint config (use asset if available, otherwise create inline)
if [[ -n "$ASSETS_DIR" && -f "$ASSETS_DIR/.swiftlint.yml" ]]; then
    echo_step "Using SwiftLint config from assets..."
    cp "$ASSETS_DIR/.swiftlint.yml" .swiftlint.yml
else
    echo_step "Creating SwiftLint config..."
    cat > .swiftlint.yml << 'EOF'
disabled_rules:
  - trailing_whitespace

opt_in_rules:
  - empty_count
  - closure_spacing

excluded:
  - .build

line_length:
  warning: 120
  error: 200

identifier_name:
  min_length: 2
  excluded:
    - id
    - x
    - y
EOF
fi

# Check if SwiftFormat is installed
if ! command -v swiftformat &>/dev/null; then
    echo_warning "SwiftFormat is not installed. Config file created but formatting won't work."
    echo "         Install with: brew install swiftformat"
fi

# Check if SwiftLint is installed
if ! command -v swiftlint &>/dev/null; then
    echo_warning "SwiftLint is not installed. Config file created but linting won't work."
    echo "         Install with: brew install swiftlint"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Package '$NAME' created successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  cd $NAME"
echo "  swift build"
echo "  swift test"
