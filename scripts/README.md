# Simple Wakeup Handler

A simplified solution for Raspberry Pi with PiJuice that runs your main script on wakeup and handles both battery and mains power scenarios.

## Overview

- **One Python script** handles everything
- **Automatic power detection** (battery vs mains)
- **Smart shutdown** (only on battery power)
- **Safety timeout** (prevents infinite loops in battery mode)
- **Runs on every boot** (no PiJuice wakeup command needed)

## Files

- `simple_wakeup_handler.py` - Main handler script
- `simple-wakeup-handler.service` - Systemd service
- `install_simple_handler.sh` - Installation script
- `test_simple_handler.sh` - Test script (created during install)
- `check_simple_status.sh` - Status checker (created during install)

## Quick Setup

### 1. Install the Handler
```bash
sudo ./scripts/install_simple_handler.sh
```

### 2. Set Up PiJuice Wakeup Alarm
```bash
# Set wakeup alarm for every hour (example)
pijuice_cli system --set-wakeup "$(date -d '+1 hour' +'%Y-%m-%d %H:%M:%S')"
```

## How It Works

### Battery Mode
1. PiJuice wakes up Pi
2. Pi boots normally
3. Systemd service starts automatically
4. Handler detects battery power
5. Runs your main script
6. Shuts down Pi after completion

### Mains Mode
1. PiJuice wakes up Pi (or Pi boots normally)
2. Pi boots normally
3. Systemd service starts automatically
4. Handler detects mains power
5. Runs your main script
6. Pi stays running (no shutdown)

## Usage

### Test the Handler
```bash
sudo ./scripts/test_simple_handler.sh
```

### Check Status
```bash
./scripts/check_simple_status.sh
```

### View Logs
```bash
tail -f /var/log/simple_wakeup.log
```

### Service Management
```bash
# Check service status
systemctl status simple-wakeup-handler

# Start service manually
sudo systemctl start simple-wakeup-handler
```

## Configuration

Edit the Python script to change settings:
- `MAIN_SCRIPT` - Path to your main script
- `LOG_FILE` - Log file location
- `SHUTDOWN_DELAY` - Delay before shutdown (seconds)
- `TOTAL_TIMEOUT` - Total timeout for battery mode (seconds, default: 300)

## Log Example

```
2024-01-15 06:00:01 - INFO - === Simple Wakeup Handler Started ===
2024-01-15 06:00:01 - INFO - Total timeout: 300 seconds
2024-01-15 06:00:01 - INFO - PiJuice power status: NOT_PRESENT
2024-01-15 06:00:01 - INFO - Power source: Battery
2024-01-15 06:00:01 - INFO - Timeout set for 300 seconds (battery mode)
2024-01-15 06:00:01 - INFO - Battery charge: 85%
2024-01-15 06:00:01 - INFO - === Starting Main Script ===
2024-01-15 06:00:05 - INFO - Main script completed successfully
2024-01-15 06:00:05 - INFO - Timeout cancelled - script completed normally
2024-01-15 06:00:05 - INFO - Running on battery power - Pi will shutdown after completion
2024-01-15 06:00:10 - INFO - Shutdown command sent
```

## Troubleshooting

### Handler not running
```bash
# Check service status
systemctl status simple-wakeup-handler

# Check logs
tail -f /var/log/simple_wakeup.log

# Test manually
sudo ./scripts/test_simple_handler.sh
```

### Not shutting down on battery
```bash
# Check if running as root
sudo python3 scripts/simple_wakeup_handler.py

# Check power detection
pijuice_cli status --get power_input
```

## Dependencies

- Python 3
- PiJuice CLI (optional, falls back to system detection)
- systemd

## Support

For issues:
1. Check the logs: `tail -f /var/log/simple_wakeup.log`
2. Run the status check: `./scripts/check_simple_status.sh`
3. Test manually: `sudo ./scripts/test_simple_handler.sh` 