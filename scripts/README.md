# Simple Wakeup Handler

A simplified solution for Raspberry Pi with PiJuice that runs your main script on wakeup and handles both battery and mains power scenarios.

## Overview

- **One Python script** handles everything
- **Automatic power detection** (battery vs mains) - **FIXED for PiJuice setups**
- **Smart shutdown** (only on battery power)
- **Safety timeout** (prevents infinite loops in battery mode)
- **Runs on every boot** (no PiJuice wakeup command needed)
- **Uses official PiJuice utility** for reliable power detection

## Power Detection Fix

**Bug Fixed**: The startup script now properly detects power connection when using PiJuice. Previously, when power was connected through PiJuice (not directly to the Pi), the system would incorrectly assume battery power.

**Solution**: The handler now uses the official PiJuice utility script (`pijuice_util.py`) for reliable power detection, with fallback to system files.

## Files

- `simple_wakeup_handler.py` - Main handler script
- `pijuice_util.py` - Official PiJuice utility (downloaded from PiJuice repo)
- `simple-wakeup-handler.service` - Systemd service
- `install_simple_handler.sh` - Installation script
- `test_simple_handler.sh` - Test script (created during install)
- `check_simple_status.sh` - Status checker (created during install)
- `test_power_detection.py` - Power detection test script

## Additional Scripts

### Weather Info Script
- `weather_info.py` - Fetches weather data from Open-Meteo API
- `weather_config.txt` - Weather script configuration
- `README_weather_info.md` - Weather script documentation

### Fact Script
- `fact.py` - Fetches random facts from API Ninjas
- `fact_config.txt` - Fact script configuration
- `README_fact.md` - Fact script documentation
- `test_fact.py` - Test script for fact functionality

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
4. Handler detects battery power using PiJuice utility
5. Runs your main script
6. Shuts down Pi after completion

### Mains Mode
1. PiJuice wakes up Pi (or Pi boots normally)
2. Pi boots normally
3. Systemd service starts automatically
4. Handler detects mains power using PiJuice utility
5. Runs your main script
6. Pi stays running (no shutdown)

## Power Detection Methods

### Primary: PiJuice Utility
The handler uses the official PiJuice utility script:
- `python3 pijuice_util.py --get-input` - To detect mains vs battery
- `python3 pijuice_util.py --get-battery` - To get battery information

### Fallback: System Files
If the utility fails, the handler checks:
- `/sys/class/power_supply/pijuice/online` - PiJuice power status
- `/sys/class/power_supply/pijuice/status` - Battery charging status
- `/sys/class/power_supply/AC/online` - Traditional AC power (direct Pi power)

## Usage

### Test the Handler
```bash
sudo ./scripts/test_simple_handler.sh
```

### Test Power Detection
```bash
python3 scripts/test_power_detection.py
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
2024-01-15 06:00:01 - INFO - PiJuice power input: PRESENT (mains detected)
2024-01-15 06:00:01 - INFO - Power source: Mains
2024-01-15 06:00:01 - INFO - Battery charge: 85%
2024-01-15 06:00:01 - INFO - === Starting Main Script ===
2024-01-15 06:00:05 - INFO - Main script completed successfully
2024-01-15 06:00:05 - INFO - Running on mains power - Pi will stay running
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

### Power detection issues
```bash
# Test power detection specifically
python3 scripts/test_power_detection.py

# Check if PiJuice utility is working
python3 scripts/pijuice_util.py --get-input
python3 scripts/pijuice_util.py --get-battery
```

### Not shutting down on battery
```bash
# Check if running as root
sudo python3 scripts/simple_wakeup_handler.py

# Check power detection
python3 scripts/test_power_detection.py
```

## Dependencies

- Python 3
- PiJuice Python library (`pijuice`)
- Official PiJuice utility script (`pijuice_util.py`)
- systemd

## Support

For issues:
1. Check the logs: `tail -f /var/log/simple_wakeup.log`
2. Test power detection: `python3 scripts/test_power_detection.py`
3. Run the status check: `./scripts/check_simple_status.sh`
4. Test manually: `sudo ./scripts/test_simple_handler.sh` 