# Power Status Board

A board that detects the power source (mains or battery) and displays the current power status on the Inky screen.

## Features

- **Power Source Detection**: Automatically detects whether the Raspberry Pi is powered by mains electricity or battery
- **Battery Percentage**: Shows the current battery percentage when running on battery power
- **PiJuice Support**: Primary detection method uses PiJuice CLI for accurate power and battery information
- **System Fallback**: Falls back to system power supply files if PiJuice is not available
- **Timestamp Display**: Shows the current date and time when the status was checked

## Display Output

The board will display one of the following messages:

- **"Powered by mains"** - When connected to mains power
- **"Battery powered (XX%)"** - When running on battery, showing the actual percentage
- **"Battery powered (unknown)"** - When running on battery but percentage cannot be determined

## Power Detection Methods

### Primary: PiJuice CLI
If PiJuice CLI is available, the board uses:
- `pijuice_cli status --get power_input` - To detect mains vs battery
- `pijuice_cli status --get charge` - To get battery percentage

### Fallback: System Files
If PiJuice is not available, the board checks:
- `/sys/class/power_supply/AC/online` - To detect mains connection
- `/sys/class/power_supply/BAT0/capacity` - To get battery percentage
- `/sys/class/power_supply/BAT1/capacity` - Alternative battery path
- `/sys/class/power_supply/battery/capacity` - Alternative battery path

## Usage

### Direct Execution
```bash
cd src/boards/power-status
python3 power-status.py
```

### As a Scheduled Board
Add this board to your scheduler or playlist to display power status at regular intervals.

## Dependencies

- Python 3
- PIL (Pillow) for image creation
- PiJuice CLI (optional, for enhanced detection)
- InkyPi display manager and configuration

## Logging

The board logs its operation with timestamps and power status information. Check the console output or system logs for detailed information about power detection and any errors.

## Error Handling

The board gracefully handles:
- Missing PiJuice CLI
- Unreadable system power files
- Invalid battery percentage values
- Display configuration issues

If power detection fails, it defaults to assuming battery power to ensure the system continues to function. 