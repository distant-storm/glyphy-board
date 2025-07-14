# PiJuice Diagnostic Script

This script helps diagnose PiJuice API issues and identify available methods in your PiJuice library version.

## Purpose

The diagnostic script helps troubleshoot the common error:
```
'PiJuicePower' object has no attribute 'GetPowerOffOnShutdown'
```

This error occurs because different versions of the PiJuice library have different API methods available.

## Usage

### Run the diagnostic:
```bash
python3 scripts/pijuice_diagnostic.py
```

### What it checks:

1. **PiJuice Installation** - Verifies the PiJuice library is installed
2. **PiJuice Connection** - Tests if PiJuice is connected and responding
3. **Available Methods** - Lists all available PiJuice methods
4. **Power Method Testing** - Tests specific power-related methods
5. **Current Status** - Shows current PiJuice status and battery info

## Output Example

```
=== PiJuice Diagnostic Tool ===
✓ PiJuice library is installed
PiJuice version: 1.4.2
✓ PiJuice is connected and responding
Status: {'powerInput': 'PRESENT', 'battery': 'FULL', 'powerInput5vIo': 'PRESENT'}

=== Available PiJuice Methods ===
Power methods:
  pj.power.GetPowerOffOnShutdown
  pj.power.PowerOff
  pj.power.SetPowerOffOnShutdown
  pj.power.SetSystemPowerSwitch

Status methods:
  pj.status.GetBatteryStatus
  pj.status.GetChargeLevel
  pj.status.GetStatus

=== Testing Power Methods ===
✓ GetPowerOffOnShutdown method exists
  Result: {'error': 'NO_ERROR', 'data': True}
✓ SetPowerOffOnShutdown method exists
✓ PowerOff method exists
✗ SetPowerOff method not found

=== Current PiJuice Status ===
Status: {'powerInput': 'PRESENT', 'battery': 'FULL', 'powerInput5vIo': 'PRESENT'}
Battery: {'status': 'FULL', 'charge': 100, 'voltage': 4200}
Charge Level: {'data': 100, 'error': 'NO_ERROR'}
```

## Common Issues

### 1. PiJuice Library Not Installed
```
✗ PiJuice library is not installed
Install with: pip3 install pijuice
```

**Solution**: Install the PiJuice library
```bash
pip3 install pijuice
```

### 2. PiJuice Not Connected
```
✗ PiJuice connection failed: COMM_ERROR
```

**Solution**: Check physical connections and I2C setup
```bash
# Check I2C
i2cdetect -y 1

# Check PiJuice CLI
pijuice_cli status
```

### 3. Missing Power Methods
```
✗ GetPowerOffOnShutdown method not found
```

**Solution**: The script now handles this automatically by:
- Detecting available methods
- Using alternative methods when available
- Falling back to system shutdown

## Integration with Other Scripts

The diagnostic script helps identify issues that affect:

- `pijuice_shutdown.py` - PiJuice shutdown script
- `simple_wakeup_handler.py` - Wakeup handler script

Both scripts have been updated to handle missing PiJuice methods gracefully.

## Troubleshooting Steps

1. **Run the diagnostic**:
   ```bash
   python3 scripts/pijuice_diagnostic.py
   ```

2. **Check PiJuice CLI**:
   ```bash
   pijuice_cli status
   ```

3. **Check I2C connection**:
   ```bash
   i2cdetect -y 1
   ```

4. **Check PiJuice library version**:
   ```bash
   pip3 show pijuice
   ```

5. **Update PiJuice library** (if needed):
   ```bash
   pip3 install --upgrade pijuice
   ```

## Files

- `pijuice_diagnostic.py` - Main diagnostic script
- `README_pijuice_diagnostic.md` - This documentation
- `pijuice_shutdown.py` - Updated shutdown script
- `simple_wakeup_handler.py` - Updated wakeup handler

## Support

If you continue to have issues:

1. Check the diagnostic output for specific error messages
2. Verify your PiJuice hardware is properly connected
3. Ensure you're using a compatible PiJuice library version
4. Consider updating to the latest PiJuice library version 