#!/usr/bin/env python3

"""
Simple Wakeup Handler for Raspberry Pi with PiJuice
Handles both battery and mains power scenarios
"""

import os
import sys
import time
import subprocess
import logging
import signal
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
MAIN_SCRIPT = "/home/webdev/glyphy-board/run_scheduler.sh"
LOG_FILE = "/var/log/simple_wakeup.log"
SHUTDOWN_DELAY = 120  # seconds
TOTAL_TIMEOUT = 300  # 5 minutes total timeout for battery mode

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def log_message(message):
    """Log a message with timestamp"""
    logger.info(message)

def check_pijuice_available():
    """Check if PiJuice CLI is available"""
    try:
        result = subprocess.run(['which', 'pijuice_cli'], 
                              capture_output=True, text=True, check=False)
        return result.returncode == 0
    except Exception:
        return False

def configure_pijuice_shutdown():
    """Configure PiJuice to properly cut power on shutdown"""
    log_message("Configuring PiJuice shutdown behavior...")
    
    try:
        # Import PiJuice library
        import pijuice
        
        # Initialize PiJuice
        pj = pijuice.PiJuice(1, 0x14)
        
        # Check if the method exists (different PiJuice versions have different APIs)
        if hasattr(pj.power, 'GetPowerOffOnShutdown'):
            # Check current power off on shutdown setting
            result = pj.power.GetPowerOffOnShutdown()
            if result['error'] == 'NO_ERROR':
                current_setting = result['data']
                log_message(f"Current PiJuice power off on shutdown setting: {current_setting}")
                
                # Enable power off on shutdown if not already enabled
                if not current_setting:
                    log_message("Enabling PiJuice power off on shutdown...")
                    result = pj.power.SetPowerOffOnShutdown(True)
                    if result['error'] == 'NO_ERROR':
                        log_message("✓ PiJuice power off on shutdown enabled")
                    else:
                        log_message(f"✗ Failed to enable PiJuice power off on shutdown: {result['error']}")
                else:
                    log_message("✓ PiJuice power off on shutdown already enabled")
            else:
                log_message(f"✗ Failed to get PiJuice power off setting: {result['error']}")
        elif hasattr(pj.power, 'GetPowerOff'):
            # Use GetPowerOff/SetPowerOff methods (PiJuice v1.8+)
            log_message("Using GetPowerOff/SetPowerOff methods (PiJuice v1.8+)")
            result = pj.power.GetPowerOff()
            if result['error'] == 'NO_ERROR':
                current_setting = result['data']
                log_message(f"Current PiJuice power off setting: {current_setting}")
                
                # Set power off to enabled (0 = disabled, 1 = enabled)
                if current_setting == 0:
                    log_message("Enabling PiJuice power off...")
                    result = pj.power.SetPowerOff(1)
                    if result['error'] == 'NO_ERROR':
                        log_message("✓ PiJuice power off enabled")
                    else:
                        log_message(f"✗ Failed to enable PiJuice power off: {result['error']}")
                else:
                    log_message("✓ PiJuice power off already enabled")
            else:
                log_message(f"✗ Failed to get PiJuice power off setting: {result['error']}")
        else:
            # Try alternative method names or skip configuration
            log_message("PiJuice power off configuration methods not available in this version")
            log_message("Available power methods:")
            available_methods = [method for method in dir(pj.power) if not method.startswith('_')]
            log_message(f"  {available_methods}")
            
            # Try to set power off using alternative method if available
            if hasattr(pj.power, 'SetPowerOff'):
                log_message("Using SetPowerOff method...")
                result = pj.power.SetPowerOff(1)  # Enable power off
                if result['error'] == 'NO_ERROR':
                    log_message("✓ PiJuice power off configured")
                else:
                    log_message(f"✗ Failed to configure PiJuice power off: {result['error']}")
            else:
                log_message("No power off configuration method found - using system shutdown")
            
    except ImportError:
        log_message("✗ PiJuice library not available - using fallback shutdown method")
    except Exception as e:
        log_message(f"✗ Error configuring PiJuice shutdown: {e}")

def get_power_status():
    """Get power status (battery or mains)"""
    # First try using the official PiJuice utility
    try:
        # Get input status using pijuice_util.py
        result = subprocess.run(
            ['/home/webdev/.virtualenvs/pimoroni/bin/python3', str(SCRIPT_DIR / 'pijuice_util.py'), '--get-input'],
            capture_output=True, text=True, check=False, timeout=10
        )
        if result.returncode == 0:
            # Parse the output to find power input status
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'usbPowerInput' in line:
                    # Extract the power input status - be more specific about the value
                    if "'usbPowerInput': 'PRESENT'" in line or '"usbPowerInput": "PRESENT"' in line:
                        log_message("PiJuice power input: PRESENT (mains detected)")
                        return True
                    elif "'usbPowerInput': 'NOT PRESENT'" in line or '"usbPowerInput": "NOT PRESENT"' in line:
                        log_message("PiJuice power input: NOT PRESENT (battery mode)")
                        return False
    except Exception as e:
        log_message(f"Error using PiJuice utility: {e}")
    
    # Fallback: check system files for PiJuice setups
    try:
        # Check if we're using PiJuice by looking for PiJuice power supply
        if os.path.exists("/sys/class/power_supply/pijuice/online"):
            with open("/sys/class/power_supply/pijuice/online", "r") as f:
                pijuice_status = f.read().strip()
                is_mains = pijuice_status == "1"
                log_message(f"PiJuice system power status: {'Mains' if is_mains else 'Battery'}")
                return is_mains
        
        # Check for PiJuice battery status - if charging, likely on mains
        if os.path.exists("/sys/class/power_supply/pijuice/status"):
            with open("/sys/class/power_supply/pijuice/status", "r") as f:
                status = f.read().strip().lower()
                if status in ['charging', 'full']:
                    log_message(f"PiJuice battery status: {status} (likely on mains)")
                    return True
                elif status == 'discharging':
                    log_message(f"PiJuice battery status: {status} (battery mode)")
                    return False
        
        # Fallback: check traditional AC power (only works if Pi is powered directly)
        if os.path.exists("/sys/class/power_supply/AC/online"):
            with open("/sys/class/power_supply/AC/online", "r") as f:
                ac_status = f.read().strip()
                is_mains = ac_status == "1"
                log_message(f"System AC power status: {'Mains' if is_mains else 'Battery'}")
                return is_mains
                
    except Exception as e:
        log_message(f"Error checking system power status: {e}")
    
    # Default to battery if we can't determine
    log_message("Could not determine power status, assuming battery")
    return False

def get_battery_info():
    """Get battery information"""
    # Try using the official PiJuice utility first
    try:
        # Get battery status using pijuice_util.py
        result = subprocess.run(
            ['/home/webdev/.virtualenvs/pimoroni/bin/python3', str(SCRIPT_DIR / 'pijuice_util.py'), '--get-battery'],
            capture_output=True, text=True, check=False, timeout=10
        )
        if result.returncode == 0:
            # Parse the output to find battery information
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'chargeLevel' in line:
                    log_message(f"Found chargeLevel line: {line}")
                    # Extract charge level - try multiple patterns
                    import re
                    
                    # Try different patterns in order of specificity
                    patterns = [
                        r"'chargeLevel':\s*(\d+)",  # Single quotes
                        r'"chargeLevel":\s*(\d+)',  # Double quotes
                        r'chargeLevel.*?(\d+)',     # Any format with chargeLevel followed by number
                        r'(\d+)'                    # Fallback: any number (original behavior)
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, line)
                        if match:
                            charge_level = match.group(1)
                            # Validate the result is reasonable (0-100)
                            try:
                                charge_int = int(charge_level)
                                if 0 <= charge_int <= 100:
                                    log_message(f"Battery charge: {charge_int}% (pattern: {pattern})")
                                    break
                                else:
                                    log_message(f"Charge level out of range (0-100): {charge_int}%")
                            except ValueError:
                                log_message(f"Invalid charge level value: {charge_level}")
                    else:
                        log_message(f"Could not parse charge level from line: {line}")
                
                if 'batteryVoltage' in line:
                    # Extract voltage
                    import re
                    match = re.search(r'(\d+\.?\d*)', line)
                    if match:
                        voltage = match.group(1)
                        log_message(f"Battery voltage: {voltage}V")
                
                if 'batteryStatus' in line:
                    # Extract battery status
                    if 'CHARGING' in line:
                        log_message("Battery status: CHARGING")
                    elif 'FULL' in line:
                        log_message("Battery status: FULL")
                    elif 'DISCHARGING' in line:
                        log_message("Battery status: DISCHARGING")
                
    except Exception as e:
        log_message(f"Error using PiJuice utility for battery info: {e}")
    
    # Fallback: check system files for PiJuice
    try:
        # Check PiJuice-specific battery files
        if os.path.exists("/sys/class/power_supply/pijuice/capacity"):
            with open("/sys/class/power_supply/pijuice/capacity", "r") as f:
                capacity = f.read().strip()
                log_message(f"PiJuice battery capacity: {capacity}%")
        
        if os.path.exists("/sys/class/power_supply/pijuice/status"):
            with open("/sys/class/power_supply/pijuice/status", "r") as f:
                status = f.read().strip()
                log_message(f"PiJuice battery status: {status}")
                
    except Exception as e:
        log_message(f"Error getting PiJuice system battery info: {e}")

def get_system_info():
    """Get basic system information"""
    try:
        # CPU temperature
        if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read().strip()) / 1000
                log_message(f"CPU temperature: {temp:.1f}°C")
        
        # Memory usage
        result = subprocess.run(['free', '-h'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                mem_line = lines[1]
                log_message(f"Memory: {mem_line}")
        
        # Disk usage
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                disk_line = lines[1]
                log_message(f"Disk: {disk_line}")
                
    except Exception as e:
        log_message(f"Error getting system info: {e}")

def run_main_script():
    """Run the main scheduler script"""
    log_message("=== Starting Main Script ===")
    
    if not os.path.exists(MAIN_SCRIPT):
        log_message(f"ERROR: Main script not found at {MAIN_SCRIPT}")
        return False
    
    log_message(f"Executing: {MAIN_SCRIPT}")
    
    try:
        # Run the main script with a timeout
        result = subprocess.run([MAIN_SCRIPT], check=False, timeout=TOTAL_TIMEOUT)
        if result.returncode == 0:
            log_message("Main script completed successfully")
            return True
        else:
            log_message(f"Main script failed with exit code: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        log_message(f"ERROR: Main script timed out after {TOTAL_TIMEOUT} seconds")
        return False
    except Exception as e:
        log_message(f"Error running main script: {e}")
        return False

def shutdown_pi():
    """Shutdown the Raspberry Pi using PiJuice if available"""
    log_message("=== Shutting down Raspberry Pi ===")
    log_message(f"Waiting {SHUTDOWN_DELAY} seconds before shutdown...")
    time.sleep(SHUTDOWN_DELAY)
    
    try:
        # Try to use PiJuice for proper shutdown
        import pijuice
        pj = pijuice.PiJuice(1, 0x14)
        
        log_message("Using PiJuice for shutdown...")
        result = pj.power.PowerOff(0)  # Power off immediately
        if result['error'] == 'NO_ERROR':
            log_message("✓ PiJuice power off command sent successfully")
        else:
            log_message(f"✗ PiJuice power off failed: {result['error']}")
            # Fallback to system shutdown
            log_message("Falling back to system shutdown...")
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
            log_message("System shutdown command sent")
            
    except ImportError:
        log_message("PiJuice library not available - using system shutdown")
        subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
        log_message("System shutdown command sent")
    except Exception as e:
        log_message(f"Error with PiJuice shutdown: {e}")
        log_message("Falling back to system shutdown...")
        try:
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
            log_message("System shutdown command sent")
        except Exception as e2:
            log_message(f"Error sending shutdown command: {e2}")

def timeout_handler(signum, frame):
    """Handle timeout signal"""
    log_message(f"TIMEOUT: Total execution time exceeded {TOTAL_TIMEOUT} seconds")
    log_message("Forcing shutdown due to timeout")
    shutdown_pi()

def main():
    """Main function"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple Wakeup Handler')
    parser.add_argument('--background', '-b', action='store_true',
                       help='Run in background mode (for service)')
    parser.add_argument('--test', '-t', action='store_true',
                       help='Run in test mode (no shutdown)')
    
    args = parser.parse_args()
    
    log_message("=== Simple Wakeup Handler Started ===")
    log_message(f"Script directory: {SCRIPT_DIR}")
    log_message(f"Log file: {LOG_FILE}")
    log_message(f"Main script: {MAIN_SCRIPT}")
    log_message(f"Total timeout: {TOTAL_TIMEOUT} seconds")
    log_message(f"Background mode: {args.background}")
    log_message(f"Test mode: {args.test}")
    
    # Check if running as root (needed for shutdown)
    if os.geteuid() != 0:
        log_message("WARNING: Not running as root - shutdown functionality may not work")
    
    # Configure PiJuice shutdown behavior
    configure_pijuice_shutdown()

    # Get power status
    is_mains = get_power_status()
    log_message(f"Power source: {'Mains' if is_mains else 'Battery'}")
    
    # Set up timeout handler for battery mode
    if not is_mains and not args.test:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TOTAL_TIMEOUT)
        log_message(f"Timeout set for {TOTAL_TIMEOUT} seconds (battery mode)")
    
    try:
        # Get system information
        get_battery_info()
        get_system_info()
        
        # Run the main script
        success = run_main_script()
        
        # Cancel timeout if we get here
        if not is_mains and not args.test:
            signal.alarm(0)
            log_message("Timeout cancelled - script completed normally")
        
        # Handle shutdown based on power status and mode
        if args.test:
            log_message("Test mode - no shutdown will occur")
            log_message("=== Simple Wakeup Handler Completed (Test Mode) ===")
        elif is_mains:
            log_message("Running on mains power - Pi will stay running")
            log_message("=== Simple Wakeup Handler Completed (Mains Mode) ===")
        else:
            log_message("Running on battery power - Pi will shutdown after completion")
            if success:
                shutdown_pi()
            else:
                log_message("Main script failed, but continuing with shutdown due to battery power")
                shutdown_pi()
                
    except Exception as e:
        log_message(f"ERROR: Unexpected error in main function: {e}")
        if not is_mains and not args.test:
            log_message("Forcing shutdown due to error (battery mode)")
            shutdown_pi()
        else:
            log_message("Error occurred but staying running (mains/test mode)")
            if not args.background:
                raise

if __name__ == "__main__":
    main() 