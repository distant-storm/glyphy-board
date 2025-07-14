# PiJuice Version 1.8 Compatibility Guide

This document outlines the specific changes made to support PiJuice library version 1.8.

## Diagnostic Results Summary

From your diagnostic output:
- **PiJuice Version**: 1.8
- **Available Power Methods**: `GetPowerOff`, `SetPowerOff` (but not `GetPowerOffOnShutdown`)
- **Available Status Methods**: `GetStatus`, `GetChargeLevel` (but not `GetBatteryStatus`)
- **Current Status**: Battery mode, no power input present, fault detected

## Key Changes Made

### 1. Power Off Configuration

**Old Method (not available in v1.8)**:
```python
pj.power.GetPowerOffOnShutdown()
pj.power.SetPowerOffOnShutdown(True)
```

**New Method (v1.8 compatible)**:
```python
pj.power.GetPowerOff()  # Returns 0 (disabled) or 1 (enabled)
pj.power.SetPowerOff(1)  # Enable power off (1 = enabled, 0 = disabled)
```

### 2. Power Off Execution

**Old Method**:
```python
pj.power.PowerOff(0)  # Immediate power off
```

**New Method (v1.8 compatible)**:
```python
pj.power.SetPowerOff(0)  # Immediate power off (0 = trigger power off)
```

### 3. Battery Status

**Old Method (not available in v1.8)**:
```python
pj.status.GetBatteryStatus()
```

**New Method (v1.8 compatible)**:
```python
pj.status.GetBatteryVoltage()  # Get battery voltage
pj.status.GetBatteryCurrent()  # Get battery current
pj.status.GetChargeLevel()     # Get charge level
```

## Updated Scripts

### 1. `pijuice_shutdown.py`
- Added support for `GetPowerOff`/`SetPowerOff` methods
- Updated power off configuration logic
- Added fallback mechanisms for missing methods

### 2. `simple_wakeup_handler.py`
- Added support for `GetPowerOff`/`SetPowerOff` methods
- Updated power off configuration logic
- Maintains compatibility with older versions

### 3. `pijuice_diagnostic.py`
- Added support for missing `io` attribute
- Added fallback for missing `GetBatteryStatus` method
- Enhanced error handling for version differences

## Method Mapping

| Function | Old Method | New Method (v1.8) |
|----------|------------|-------------------|
| Check power off setting | `GetPowerOffOnShutdown()` | `GetPowerOff()` |
| Enable power off | `SetPowerOffOnShutdown(True)` | `SetPowerOff(1)` |
| Trigger power off | `PowerOff(0)` | `SetPowerOff(0)` |
| Get battery status | `GetBatteryStatus()` | `GetBatteryVoltage()` + `GetBatteryCurrent()` |

## Configuration Values

### Power Off Settings
- `0` = Disabled (power off feature disabled)
- `1` = Enabled (power off feature enabled)
- `0` = Trigger immediate power off (when calling SetPowerOff)

### Status Values
- `powerInput`: `'PRESENT'` (mains) or `'NOT_PRESENT'` (battery)
- `battery`: `'NORMAL'`, `'FULL'`, `'CHARGING'`, `'DISCHARGING'`
- `isFault`: `True` or `False`

## Testing Your Setup

### 1. Run the diagnostic:
```bash
python3 scripts/pijuice_diagnostic.py
```

### 2. Test power off configuration:
```bash
python3 scripts/pijuice_shutdown.py --configure
```

### 3. Test shutdown (be careful!):
```bash
python3 scripts/pijuice_shutdown.py --delay 10
```

## Troubleshooting

### If you get "method not found" errors:
1. The scripts now automatically detect available methods
2. They will use alternative methods when primary methods aren't available
3. Check the diagnostic output to see what methods are available

### If power off doesn't work:
1. Check if `SetPowerOff(1)` was called successfully
2. Verify the PiJuice is properly configured
3. Check the logs for any error messages

### If battery status is unclear:
1. The scripts will try multiple methods to get battery information
2. Check the diagnostic output for available status methods
3. The scripts will fall back to system file checks if needed

## Files Updated

- `scripts/pijuice_shutdown.py` - Updated for v1.8 compatibility
- `scripts/simple_wakeup_handler.py` - Updated for v1.8 compatibility  
- `scripts/pijuice_diagnostic.py` - Enhanced error handling
- `scripts/README_pijuice_diagnostic.md` - Documentation
- `scripts/PIJUICE_V1.8_COMPATIBILITY.md` - This guide

## Version Compatibility

The updated scripts maintain backward compatibility:
- **PiJuice v1.8+**: Uses `GetPowerOff`/`SetPowerOff` methods
- **PiJuice v1.4+**: Uses `GetPowerOffOnShutdown`/`SetPowerOffOnShutdown` methods
- **Older versions**: Falls back to system shutdown

All scripts now automatically detect the available methods and use the appropriate ones for your PiJuice version. 