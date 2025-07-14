#!/bin/bash

# Simple Service Installation Script
# Installs the wakeup handler to run automatically on boot

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_status "Installing wakeup handler service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root"
    echo "Run with: sudo $0"
    exit 1
fi

# Create log directory
print_status "Creating log directory..."
mkdir -p /var/log
touch /var/log/simple_wakeup.log
chmod 644 /var/log/simple_wakeup.log

# Make the Python script executable
print_status "Making Python script executable..."
chmod +x "$SCRIPT_DIR/simple_wakeup_handler.py"

# Install systemd service
print_status "Installing systemd service..."
SERVICE_FILE="$SCRIPT_DIR/simple-wakeup-handler.service"
SERVICE_NAME="simple-wakeup-handler"

cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"

# Reload systemd
print_status "Reloading systemd..."
systemctl daemon-reload

# Enable the service
print_status "Enabling service..."
systemctl enable "$SERVICE_NAME"

print_success "Installation completed!"
echo ""
echo "The service will now run automatically when the system boots."
echo ""
echo "To check status: systemctl status $SERVICE_NAME"
echo "To view logs: tail -f /var/log/simple_wakeup.log"
echo "To start now: systemctl start $SERVICE_NAME" 