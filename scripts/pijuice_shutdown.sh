#!/bin/bash

# PiJuice Shutdown Script Wrapper
# Simple wrapper for the Python PiJuice shutdown script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/pijuice_shutdown.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}PiJuice Shutdown Script${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --now          Shutdown immediately (no delay)"
    echo "  -d, --delay SEC    Shutdown after SEC seconds (default: 5)"
    echo "  -c, --check        Check power status and battery info only"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Shutdown in 5 seconds"
    echo "  $0 --now           # Shutdown immediately"
    echo "  $0 --delay 10      # Shutdown in 10 seconds"
    echo "  $0 --check         # Check power status only"
    echo ""
}

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Error: Python script not found at $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Warning: Not running as root${NC}"
    echo "Shutdown functionality may not work properly."
    echo "Consider running with: sudo $0"
    echo ""
fi

# Parse arguments
case "$1" in
    -h|--help)
        print_usage
        exit 0
        ;;
    -n|--now)
        sudo python3 "$PYTHON_SCRIPT" --now
        ;;
    -d|--delay)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Delay value required${NC}"
            exit 1
        fi
        sudo python3 "$PYTHON_SCRIPT" --delay "$2"
        ;;
    -c|--check)
        sudo python3 "$PYTHON_SCRIPT" --check
        ;;
    --configure)
        sudo python3 "$PYTHON_SCRIPT" --configure
        ;;
    "")
        # No arguments - default behavior
        sudo python3 "$PYTHON_SCRIPT"
        ;;
    *)
        echo -e "${RED}Error: Unknown option $1${NC}"
        print_usage
        exit 1
        ;;
esac 