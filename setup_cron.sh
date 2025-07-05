#!/bin/bash
"""
Setup script for Glyphy Board Scheduler Cron Job

This script helps set up the scheduler to run automatically.
"""

# Interactive cron job setup script for the scheduler

# Get the current directory (where the scheduler wrapper is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_PATH="$SCRIPT_DIR/run_scheduler.sh"

echo "Setting up cron job for InkyPi scheduler..."
echo "Working directory: $SCRIPT_DIR"
echo "Wrapper path: $WRAPPER_PATH"

# Check if wrapper exists
if [ ! -f "$WRAPPER_PATH" ]; then
    echo "ERROR: run_scheduler.sh not found at $WRAPPER_PATH"
    exit 1
fi

echo ""
echo "Choose how often you want the scheduler to run:"
echo "1) Every 5 minutes (recommended)"
echo "2) Every 15 minutes"
echo "3) Every hour"
echo "4) Every 30 minutes"
echo "5) Custom"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "*/5 * * * * cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        CRON_LINE="*/5 * * * * cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        ;;
    2)
        echo "*/15 * * * * cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        CRON_LINE="*/15 * * * * cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        ;;
    3)
        echo "0 * * * * cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        CRON_LINE="0 * * * * cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        ;;
    4)
        echo "*/30 * * * * cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        CRON_LINE="*/30 * * * * cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        ;;
    5)
        read -p "Enter custom cron expression (e.g., '0 */2 * * *' for every 2 hours): " custom_cron
        echo "$custom_cron cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        CRON_LINE="$custom_cron cd $SCRIPT_DIR && ./run_scheduler.sh >> scheduler_cron.log 2>&1"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "The following cron job will be added:"
echo "$CRON_LINE"
echo ""
read -p "Do you want to add this cron job? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    # Remove any existing scheduler cron jobs
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_DIR.*scheduler"; then
        echo "Removing existing scheduler cron jobs..."
        crontab -l 2>/dev/null | grep -v "$SCRIPT_DIR.*scheduler" | crontab -
    fi
    
    # Add the new cron job
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    
    echo "Cron job added successfully!"
    echo ""
    echo "You can view your cron jobs with: crontab -l"
    echo "You can remove the cron job with: crontab -e"
    echo "And delete the line containing 'run_scheduler.sh'"
    echo ""
    echo "Scheduler logs will be saved to: $SCRIPT_DIR/scheduler_cron.log"
else
    echo "Cron job not added."
fi

echo ""
echo "=== Setup Complete ==="
echo "The scheduler is ready to use!"
echo ""
echo "Test it manually with: ./run_scheduler.sh"
echo "View logs with: tail -f $SCRIPT_DIR/scheduler.log" 