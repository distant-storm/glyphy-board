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
    echo "  Note: PiJuice CLI is interactive and may not work in automated scripts"
    echo "  The handler will use system files for power detection"
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
