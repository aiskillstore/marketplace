#!/bin/bash
# Quick simulator management
# Usage: simulator.sh <command> [args]
#   list              List all simulators
#   boot <name>       Boot simulator by name
#   shutdown          Shutdown all simulators
#   reset             Reset all simulators
#   install <app>     Install app on booted simulator
#   launch <bundleid> Launch app by bundle ID
#   screenshot [file] Take screenshot
#   dark              Enable dark mode
#   light             Enable light mode

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
if ! command -v xcrun &> /dev/null; then
    echo_error "xcrun is not available. Install Xcode Command Line Tools: xcode-select --install"
    exit 1
fi

if ! xcrun simctl help &> /dev/null; then
    echo_error "simctl is not available. Install Xcode Command Line Tools: xcode-select --install"
    exit 1
fi

CMD="${1:-list}"
shift || true

case $CMD in
    list)
        if ! xcrun simctl list devices available 2>&1; then
            echo_error "Failed to list simulators"
            exit 1
        fi
        ;;

    boot)
        NAME="${1:?Usage: simulator.sh boot <name>}"
        echo_step "Booting: $NAME"
        if ! xcrun simctl boot "$NAME" 2>/dev/null; then
            # Check if already booted or if there's an error
            if xcrun simctl list devices | grep -q "$NAME.*Booted"; then
                echo "         Simulator '$NAME' is already booted"
            else
                echo_error "Failed to boot simulator '$NAME'"
                echo "         Available simulators:" >&2
                xcrun simctl list devices available | grep -i "$NAME" || true
                exit 1
            fi
        fi
        if command -v open &> /dev/null; then
            open -a Simulator 2>/dev/null || true
        fi
        ;;

    shutdown)
        echo_step "Shutting down all simulators..."
        if ! xcrun simctl shutdown all 2>&1; then
            echo_warning "Some simulators may not have shut down properly"
        fi
        ;;

    reset)
        echo_step "Resetting all simulators..."
        echo_warning "This will erase all simulator data!"
        if ! xcrun simctl shutdown all 2>&1; then
            echo_warning "Some simulators may not have shut down properly"
        fi
        if ! xcrun simctl erase all 2>&1; then
            echo_error "Failed to reset simulators"
            exit 1
        fi
        echo_step "Done!"
        ;;

    install)
        APP="${1:?Usage: simulator.sh install <path/to/app>}"
        if [[ ! -e "$APP" ]]; then
            echo_error "App path '$APP' does not exist"
            exit 1
        fi
        echo_step "Installing: $APP"
        if ! xcrun simctl install booted "$APP" 2>&1; then
            echo_error "Failed to install app. Make sure a simulator is booted."
            exit 1
        fi
        ;;

    launch)
        BUNDLE="${1:?Usage: simulator.sh launch <bundle.id>}"
        echo_step "Launching: $BUNDLE"
        if ! xcrun simctl launch booted "$BUNDLE" 2>&1; then
            echo_error "Failed to launch app with bundle ID '$BUNDLE'"
            echo "         Make sure the app is installed and a simulator is booted." >&2
            exit 1
        fi
        ;;

    screenshot)
        FILE="${1:-screenshot-$(date +%Y%m%d-%H%M%S).png}"
        if ! xcrun simctl io booted screenshot "$FILE" 2>&1; then
            echo_error "Failed to take screenshot. Make sure a simulator is booted."
            exit 1
        fi
        echo_step "Screenshot saved: $FILE"
        ;;

    dark)
        if ! xcrun simctl ui booted appearance dark 2>&1; then
            echo_error "Failed to set dark mode. Make sure a simulator is booted."
            exit 1
        fi
        echo_step "Dark mode enabled"
        ;;

    light)
        if ! xcrun simctl ui booted appearance light 2>&1; then
            echo_error "Failed to set light mode. Make sure a simulator is booted."
            exit 1
        fi
        echo_step "Light mode enabled"
        ;;

    *)
        echo_error "Unknown command: $CMD"
        echo "Usage: simulator.sh <list|boot|shutdown|reset|install|launch|screenshot|dark|light>" >&2
        exit 1
        ;;
esac
