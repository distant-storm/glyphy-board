#!/bin/bash

# Simple Wakeup Handler Installation Script v2
# This script installs the simple wakeup handler as a systemd service
# with options for different service configurations

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

print_status "Simple Wakeup Handler Installation v2"
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

# Ask user for service type
echo ""
print_status "Choose service configuration:"
echo "1) Standard service (runs once per boot, recommended for most setups)"
echo "2) Background service (stays running, for continuous monitoring)"
echo "3) Manual service (runs only when manually started)"
read -p "Enter choice (1-3): " SERVICE_CHOICE

case $SERVICE_CHOICE in
    1)
        SERVICE_FILE="$SCRIPT_DIR/simple-wakeup-handler.service"
        SERVICE_NAME="simple-wakeup-handler"
        print_status "Installing standard service..."
        ;;
    2)
        SERVICE_FILE="$SCRIPT_DIR/simple-wakeup-handler-background.service"
        SERVICE_NAME="simple-wakeup-handler-background"
        print_status "Installing background service..."
        ;;
    3)
        SERVICE_FILE="$SCRIPT_DIR/simple-wakeup-handler.service"
        SERVICE_NAME="simple-wakeup-handler"
        print_status "Installing manual service (will not auto-start)..."
        ;;
    *)
        print_error "Invalid choice. Using standard service."
        SERVICE_FILE="$SCRIPT_DIR/simple-wakeup-handler.service"
        SERVICE_NAME="simple-wakeup-handler"
        ;;
esac

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

# Enable the service (unless manual mode)
if [ "$SERVICE_CHOICE" != "3" ]; then
    print_status "Enabling service..."
    systemctl enable "$SERVICE_NAME"
    print_success "Service enabled and will start on boot"
else
    print_status "Service installed but not enabled (manual mode)"
    print_status "To start manually: sudo systemctl start $SERVICE_NAME"
fi

# Create a test script
print_status "Creating test script..."
cat > "$SCRIPT_DIR/test_simple_handler.sh" << 'EOF'
#!/bin/bash

# Test script for the simple wakeup handler
# This script can be run manually to test the handler

echo "Testing Simple Wakeup Handler..."
echo "This will run the handler in test mode (no shutdown)"

# Run the handler in test mode
sudo python3 "$(dirname "$0")/simple_wakeup_handler.py" --test

echo "Test completed"
EOF

chmod +x "$SCRIPT_DIR/test_simple_handler.sh"

# Create a status check script
print_status "Creating status check script..."
cat > "$SCRIPT_DIR/check_simple_status.sh" << EOF
#!/bin/bash

# Status check script for the simple wakeup handler

SERVICE_NAME="$SERVICE_NAME"

echo "=== Simple Wakeup Handler Status ==="
echo "Service: \$SERVICE_NAME"
echo ""

# Check if service is enabled
if systemctl is-enabled \$SERVICE_NAME >/dev/null 2>&1; then
    echo "✓ Service is enabled"
else
    echo "✗ Service is not enabled"
fi

# Check if service is active
if systemctl is-active \$SERVICE_NAME >/dev/null 2>&1; then
    echo "✓ Service is active"
else
    echo "✗ Service is not active"
fi

# Check service status
echo ""
echo "Service status:"
systemctl status \$SERVICE_NAME --no-pager -l

# Check log file
LOG_FILE="/var/log/simple_wakeup.log"
if [ -f "\$LOG_FILE" ]; then
    echo ""
    echo "✓ Log file exists: \$LOG_FILE"
    echo "  Last 10 log entries:"
    tail -10 "\$LOG_FILE" | sed 's/^/    /'
else
    echo ""
    echo "✗ Log file not found: \$LOG_FILE"
fi

# Check PiJuice
if command -v pijuice_cli &> /dev/null; then
    echo ""
    echo "✓ PiJuice CLI available"
else
    echo ""
    echo "✗ PiJuice CLI not available"
fi

echo ""
echo "=== Usage ==="
echo "Test the handler: sudo $(dirname "$0")/test_simple_handler.sh"
echo "View logs: tail -f \$LOG_FILE"
echo "Service status: systemctl status \$SERVICE_NAME"
echo "Start service: sudo systemctl start \$SERVICE_NAME"
echo "Stop service: sudo systemctl stop \$SERVICE_NAME"
echo "Restart service: sudo systemctl restart \$SERVICE_NAME"
EOF

chmod +x "$SCRIPT_DIR/check_simple_status.sh"

# Create a service management script
print_status "Creating service management script..."
cat > "$SCRIPT_DIR/manage_simple_service.sh" << EOF
#!/bin/bash

# Service management script for the simple wakeup handler

SERVICE_NAME="$SERVICE_NAME"

case "\$1" in
    start)
        echo "Starting \$SERVICE_NAME..."
        sudo systemctl start \$SERVICE_NAME
        ;;
    stop)
        echo "Stopping \$SERVICE_NAME..."
        sudo systemctl stop \$SERVICE_NAME
        ;;
    restart)
        echo "Restarting \$SERVICE_NAME..."
        sudo systemctl restart \$SERVICE_NAME
        ;;
    status)
        echo "Status of \$SERVICE_NAME:"
        sudo systemctl status \$SERVICE_NAME --no-pager -l
        ;;
    enable)
        echo "Enabling \$SERVICE_NAME..."
        sudo systemctl enable \$SERVICE_NAME
        ;;
    disable)
        echo "Disabling \$SERVICE_NAME..."
        sudo systemctl disable \$SERVICE_NAME
        ;;
    logs)
        echo "Recent logs:"
        tail -20 /var/log/simple_wakeup.log
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|enable|disable|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  restart - Restart the service"
        echo "  status  - Show service status"
        echo "  enable  - Enable service to start on boot"
        echo "  disable - Disable service from starting on boot"
        echo "  logs    - Show recent logs"
        exit 1
        ;;
esac
EOF

chmod +x "$SCRIPT_DIR/manage_simple_service.sh"

print_success "Installation completed successfully!"
echo ""
echo "=== Installation Summary ==="
echo "✓ Python script installed and made executable"
echo "✓ Systemd service installed: \$SERVICE_NAME"
if [ "$SERVICE_CHOICE" != "3" ]; then
    echo "✓ Service enabled and will start on boot"
else
    echo "✓ Service installed but not enabled (manual mode)"
fi
echo "✓ Log file created at /var/log/simple_wakeup.log"
echo "✓ Management scripts created"
echo ""
echo "=== How It Works ==="
echo "1. PiJuice wakes up the Pi"
echo "2. Pi boots normally"
echo "3. Systemd starts the \$SERVICE_NAME service"
echo "4. Handler detects power source (battery or mains)"
echo "5. Handler runs your main script"
echo "6. If on battery: Pi shuts down after completion"
echo "7. If on mains: Pi stays running"
echo ""
echo "=== Next Steps ==="
echo "1. Test the handler: sudo $SCRIPT_DIR/test_simple_handler.sh"
echo "2. Check status: $SCRIPT_DIR/check_simple_status.sh"
echo "3. Manage service: $SCRIPT_DIR/manage_simple_service.sh"
echo "4. View logs: tail -f /var/log/simple_wakeup.log"
if [ "$SERVICE_CHOICE" != "3" ]; then
    echo "5. Start the service: sudo systemctl start \$SERVICE_NAME"
else
    echo "5. Start the service manually: sudo systemctl start \$SERVICE_NAME"
fi 