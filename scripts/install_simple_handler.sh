#!/bin/bash

# Simple Wakeup Handler Installation Script
# This script installs the simple wakeup handler as a systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_status "Simple Wakeup Handler Installation"
print_status "Script directory: $SCRIPT_DIR"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root"
    print_status "Run with: sudo $0"
    exit 1
fi

# Check if we're on a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "This doesn't appear to be a Raspberry Pi"
    print_status "Continuing anyway..."
fi

# Check if Python 3 is available
print_status "Checking Python 3 availability..."
if command -v python3 &> /dev/null; then
    print_success "Python 3 found"
else
    print_error "Python 3 not found"
    print_status "Please install Python 3: sudo apt install python3"
    exit 1
fi

# Check if PiJuice is available
print_status "Checking PiJuice availability..."
if command -v pijuice_cli &> /dev/null; then
    print_success "PiJuice CLI found"
    PIJUICE_AVAILABLE=true
else
    print_warning "PiJuice CLI not found"
    print_status "The handler will use alternative power detection methods"
    PIJUICE_AVAILABLE=false
fi

# Create log directory
print_status "Creating log directory..."
mkdir -p /var/log
touch /var/log/simple_wakeup.log
chmod 644 /var/log/simple_wakeup.log

# Make the Python script executable
print_status "Making Python script executable..."
chmod +x "$SCRIPT_DIR/simple_wakeup_handler.py"
print_success "Python script made executable"

# Install systemd service
print_status "Installing systemd service..."
SERVICE_FILE="$SCRIPT_DIR/simple-wakeup-handler.service"
SERVICE_NAME="simple-wakeup-handler"

if [ -f "$SERVICE_FILE" ]; then
    # Copy service file to systemd directory
    cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"
    print_success "Systemd service installed"
else
    print_error "Service file not found at $SERVICE_FILE"
    exit 1
fi

# Reload systemd
print_status "Reloading systemd..."
systemctl daemon-reload

# Enable the service
print_status "Enabling service..."
systemctl enable "$SERVICE_NAME"

# Create a test script
print_status "Creating test script..."
cat > "$SCRIPT_DIR/test_simple_handler.sh" << 'EOF'
#!/bin/bash

# Test script for the simple wakeup handler
# This script can be run manually to test the handler

echo "Testing Simple Wakeup Handler..."
echo "This will run the handler in test mode"

# Run the handler
sudo python3 "$(dirname "$0")/simple_wakeup_handler.py"

echo "Test completed"
EOF

chmod +x "$SCRIPT_DIR/test_simple_handler.sh"

# Create a status check script
print_status "Creating status check script..."
cat > "$SCRIPT_DIR/check_simple_status.sh" << 'EOF'
#!/bin/bash

# Status check script for the simple wakeup handler

echo "=== Simple Wakeup Handler Status ==="
echo ""

# Check if service is enabled
if systemctl is-enabled simple-wakeup-handler >/dev/null 2>&1; then
    echo "✓ Service is enabled"
else
    echo "✗ Service is not enabled"
fi

# Check if service is active
if systemctl is-active simple-wakeup-handler >/dev/null 2>&1; then
    echo "✓ Service is active"
else
    echo "✗ Service is not active (normal for oneshot service)"
fi

# Check log file
LOG_FILE="/var/log/simple_wakeup.log"
if [ -f "$LOG_FILE" ]; then
    echo "✓ Log file exists: $LOG_FILE"
    echo "  Last 5 log entries:"
    tail -5 "$LOG_FILE" | sed 's/^/    /'
else
    echo "✗ Log file not found: $LOG_FILE"
fi

# Check PiJuice
if command -v pijuice_cli &> /dev/null; then
    echo ""
    echo "✓ PiJuice CLI available"
    echo "  Power status:"
    pijuice_cli status --get power_input 2>/dev/null | sed 's/^/    Power: /'
    pijuice_cli status --get charge 2>/dev/null | sed 's/^/    Charge: /'
else
    echo ""
    echo "✗ PiJuice CLI not available"
fi

echo ""
echo "=== Usage ==="
echo "Test the handler: sudo $(dirname "$0")/test_simple_handler.sh"
echo "View logs: tail -f $LOG_FILE"
echo "Service status: systemctl status simple-wakeup-handler"
echo "Start service: sudo systemctl start simple-wakeup-handler"
EOF

chmod +x "$SCRIPT_DIR/check_simple_status.sh"

print_success "Installation completed successfully!"
echo ""
echo "=== Installation Summary ==="
echo "✓ Python script installed and made executable"
echo "✓ Systemd service installed and enabled"
echo "✓ Log file created at /var/log/simple_wakeup.log"
echo "✓ Test scripts created"
echo ""
echo "=== How It Works ==="
echo "1. PiJuice wakes up the Pi"
echo "2. Pi boots normally"
echo "3. Systemd starts the simple-wakeup-handler service"
echo "4. Handler detects power source (battery or mains)"
echo "5. Handler runs your main script"
echo "6. If on battery: Pi shuts down after completion"
echo "7. If on mains: Pi stays running"
echo ""
echo "=== Next Steps ==="
echo "1. Test the handler: sudo $SCRIPT_DIR/test_simple_handler.sh"
echo "2. Check status: $SCRIPT_DIR/check_simple_status.sh"
echo "3. View logs: tail -f /var/log/simple_wakeup.log"
echo "4. Start the service: sudo systemctl start simple-wakeup-handler"
echo ""
echo "=== Important Notes ==="
echo "- The service runs automatically on every boot"
echo "- No need to configure PiJuice wakeup commands"
echo "- Works with both battery and mains power"
echo "- Logs are written to /var/log/simple_wakeup.log"
echo "- The handler requires root privileges for shutdown functionality" 