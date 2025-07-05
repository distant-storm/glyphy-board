#!/bin/bash

# Wrapper script to run the scheduler with proper environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Virtual environment path
VENV_PATH="/usr/local/inkypi/venv_inkypi"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "ERROR: Virtual environment not found at $VENV_PATH"
    echo "Please run the installation script first."
    exit 1
fi

# Activate virtual environment and run scheduler
source "$VENV_PATH/bin/activate"
cd "$SCRIPT_DIR/src"
python scheduler.py "$@" 