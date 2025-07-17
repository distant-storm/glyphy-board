#!/bin/bash

# Test script for the simple wakeup handler
# This script can be run manually to test the handler

echo "Testing Simple Wakeup Handler..."
echo "This will run the handler in test mode"

# Run the handler
sudo python3 "$(dirname "$0")/simple_wakeup_handler.py"

echo "Test completed"
