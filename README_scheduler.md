# Glyphy Board Scheduler

The Glyphy Board Scheduler is a Python script that automatically executes board scripts based on time-based schedules. It supports both absolute datetime schedules and relative recurring patterns.

## Features

- **Absolute Scheduling**: Execute scripts at specific dates and times
- **Relative Scheduling**: Execute scripts on recurring patterns (daily, weekly, monthly)
- **Board Script Execution**: Automatically runs Python scripts in the `boards/` directory
- **Error Handling**: Displays errors on the eink screen if scripts fail or don't exist
- **Comprehensive Logging**: Detailed logs of all scheduler activities
- **Cron Integration**: Easy setup for automatic execution

## How It Works

1. **Check Current Time**: The scheduler gets the current date/time
2. **Find Active Schedules**: Looks for schedules marked as "active"
3. **Match Schedule Items**: Finds schedule items that match the current time
4. **Execute Board Script**: Runs the corresponding Python script from `boards/`
5. **Handle Errors**: Shows error messages on screen if problems occur

## Schedule Types

### Absolute Schedules
Execute at specific dates and times:
- `2024-01-15T14:00:00` to `2024-01-15T15:00:00`
- Perfect for one-time events or specific meeting times

### Relative Schedules
Execute on recurring patterns:
- **Daily**: `09:00 - 17:00` (every day)
- **Weekly**: `Wednesday 16:00 - 18:00` (every Wednesday)  
- **Monthly**: `15th 09:00 - 17:00` (15th of every month)

## File Structure

```
glyphy-board/
├── scheduler.py              # Main scheduler engine
├── data/
│   ├── schedules.json        # Schedule definitions
│   └── schedule-items.json   # Schedule items with times/patterns
├── boards/
│   ├── dashboard.py          # Default dashboard script
│   ├── daily-board.py        # Example daily board
│   └── test-board.py         # Example test board
└── logs/
    ├── scheduler.log         # Detailed scheduler logs
    └── scheduler_cron.log    # Cron execution logs
```

## Usage

### Manual Execution
```bash
# Run once
python3 scheduler.py

# Run with debug output
python3 scheduler.py --debug
```

### Automated Execution (Cron)
```bash
# Setup cron job (interactive)
./setup_cron.sh

# Manual cron setup - run every 5 minutes
*/5 * * * * cd /path/to/glyphy-board && python3 scheduler.py >> scheduler_cron.log 2>&1
```

### Creating Board Scripts

Board scripts should be placed in the `boards/` directory and follow this pattern:

```python
#!/usr/bin/env python3
"""
My Board Script
"""

import sys
from datetime import datetime

def main():
    """Main function for board display"""
    current_time = datetime.now()
    
    print(f"=== My Board Script Executed ===")
    print(f"Current time: {current_time}")
    
    # Your board logic here:
    # 1. Load display manager
    # 2. Create image content
    # 3. Display on eink screen
    
    print("Board content displayed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Example Scenarios

### Daily Work Schedule
- **Schedule**: "Work Schedule" (Active)
- **Item**: Daily 09:00 - 17:00 → `work-board.py`
- **Result**: Shows work-related content during business hours

### Meeting Reminder
- **Schedule**: "Meetings" (Active)  
- **Item**: 2024-01-15T14:00 - 2024-01-15T15:00 → `meeting-board.py`
- **Result**: Shows meeting reminder at specific time

### Weekly Reports
- **Schedule**: "Reports" (Active)
- **Item**: Weekly on Friday 17:00 - 17:30 → `weekly-report.py`
- **Result**: Shows weekly report every Friday evening

## Error Handling

The scheduler handles several error conditions:

1. **No Active Schedules**: Shows dashboard or default content
2. **No Matching Schedule Items**: Shows dashboard or default content  
3. **Missing Board Script**: Displays error message on screen
4. **Script Execution Failure**: Displays error message on screen
5. **Data File Corruption**: Logs error and continues

## Logging

Two log files are created:

- `scheduler.log`: Detailed execution logs with timestamps
- `scheduler_cron.log`: Output from cron executions

View logs in real-time:
```bash
tail -f scheduler.log
tail -f scheduler_cron.log
```

## Testing

Create test schedules and items:
```bash
python3 test_scheduler.py
python3 scheduler.py
```

## Troubleshooting

### Scheduler Not Finding Schedules
- Check `data/schedules.json` exists and has active schedules
- Check `data/schedule-items.json` has items for those schedules

### Board Script Not Executing  
- Ensure script exists in `boards/` directory
- Make script executable: `chmod +x boards/my-board.py`
- Check script has proper shebang: `#!/usr/bin/env python3`

### Cron Job Not Working
- Check cron is running: `sudo service cron status`
- Verify cron job: `crontab -l`
- Check cron logs: `tail -f scheduler_cron.log`
- Use absolute paths in cron commands

### Time Zone Issues
- Scheduler uses local system time
- Ensure system timezone is correct: `timedatectl`
- Schedule items should use local timezone format

## Integration with Web UI

The scheduler works seamlessly with the web-based scheduling interface:

1. Create schedules through the web UI (`/schedules`)
2. Add schedule items with absolute or relative patterns  
3. The scheduler automatically picks up changes
4. No restart required - changes take effect on next run

This creates a complete scheduling system where you can manage schedules through a user-friendly web interface and have them automatically executed by the scheduler engine. 