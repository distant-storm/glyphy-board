#!/bin/bash
"""
Setup script for Glyphy Board Scheduler Cron Job

This script helps set up the scheduler to run automatically.
"""

# Get the current directory (where the scheduler.py is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SCHEDULER_PATH="$SCRIPT_DIR/scheduler.py"

echo "=== Glyphy Board Scheduler Setup ==="
echo "Script directory: $SCRIPT_DIR"
echo "Scheduler path: $SCHEDULER_PATH"

# Check if scheduler.py exists
if [ ! -f "$SCHEDULER_PATH" ]; then
    echo "ERROR: scheduler.py not found at $SCHEDULER_PATH"
    exit 1
fi

echo ""
echo "Scheduler found! Here are some cron job examples:"
echo ""

echo "1. Run every 5 minutes:"
echo "*/5 * * * * cd $SCRIPT_DIR && python3 scheduler.py >> scheduler_cron.log 2>&1"
echo ""

echo "2. Run every 15 minutes:"
echo "*/15 * * * * cd $SCRIPT_DIR && python3 scheduler.py >> scheduler_cron.log 2>&1"
echo ""

echo "3. Run every hour at minute 0:"
echo "0 * * * * cd $SCRIPT_DIR && python3 scheduler.py >> scheduler_cron.log 2>&1"
echo ""

echo "4. Run every 30 minutes:"
echo "*/30 * * * * cd $SCRIPT_DIR && python3 scheduler.py >> scheduler_cron.log 2>&1"
echo ""

echo "To add a cron job:"
echo "1. Run: crontab -e"
echo "2. Add one of the lines above"
echo "3. Save and exit"
echo ""

echo "To view current cron jobs:"
echo "crontab -l"
echo ""

echo "To view scheduler logs:"
echo "tail -f $SCRIPT_DIR/scheduler.log"
echo "tail -f $SCRIPT_DIR/scheduler_cron.log"
echo ""

# Ask if user wants to automatically add a cron job
read -p "Would you like to automatically add a cron job to run every 5 minutes? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add cron job
    CRON_LINE="*/5 * * * * cd $SCRIPT_DIR && python3 scheduler.py >> scheduler_cron.log 2>&1"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_DIR.*scheduler.py"; then
        echo "Cron job already exists for this scheduler!"
        echo "Current cron jobs:"
        crontab -l | grep scheduler
    else
        # Add the cron job
        (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
        echo "✅ Cron job added successfully!"
        echo "The scheduler will now run every 5 minutes."
        echo ""
        echo "To remove it later, run: crontab -e"
        echo "And delete the line containing 'scheduler.py'"
    fi
else
    echo "No cron job added. You can add one manually using the examples above."
fi

echo ""
echo "=== Setup Complete ==="
echo "The scheduler is ready to use!"
echo ""
echo "Test it manually with: python3 $SCHEDULER_PATH"
echo "View logs with: tail -f $SCRIPT_DIR/scheduler.log" 