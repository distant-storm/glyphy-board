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

def get_power_status():
    """Get power status (battery or mains)"""
    if check_pijuice_available():
        try:
            # Get power input status from PiJuice
            result = subprocess.run(
                ['pijuice_cli', 'status', '--get', 'power_input'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                power_status = result.stdout.strip()
                log_message(f"PiJuice power status: {power_status}")
                return power_status == "PRESENT"  # True if mains, False if battery
        except Exception as e:
            log_message(f"Error getting PiJuice power status: {e}")
    
    # Fallback: check system power files
    try:
        if os.path.exists("/sys/class/power_supply/AC/online"):
            with open("/sys/class/power_supply/AC/online", "r") as f:
                ac_status = f.read().strip()
                is_mains = ac_status == "1"
                log_message(f"System power status: {'Mains' if is_mains else 'Battery'}")
                return is_mains
    except Exception as e:
        log_message(f"Error checking system power status: {e}")
    
    # Default to battery if we can't determine
    log_message("Could not determine power status, assuming battery")
    return False

def get_battery_info():
    """Get battery information"""
    if check_pijuice_available():
        try:
            # Get battery charge
            result = subprocess.run(
                ['pijuice_cli', 'status', '--get', 'charge'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                charge = result.stdout.strip()
                log_message(f"Battery charge: {charge}%")
            
            # Get battery voltage
            result = subprocess.run(
                ['pijuice_cli', 'status', '--get', 'vbat'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                voltage = result.stdout.strip()
                log_message(f"Battery voltage: {voltage}V")
                
        except Exception as e:
            log_message(f"Error getting battery info: {e}")

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
    """Shutdown the Raspberry Pi"""
    log_message("=== Shutting down Raspberry Pi ===")
    log_message(f"Waiting {SHUTDOWN_DELAY} seconds before shutdown...")
    time.sleep(SHUTDOWN_DELAY)
    
    try:
        subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
        log_message("Shutdown command sent")
    except Exception as e:
        log_message(f"Error sending shutdown command: {e}")

def timeout_handler(signum, frame):
    """Handle timeout signal"""
    log_message(f"TIMEOUT: Total execution time exceeded {TOTAL_TIMEOUT} seconds")
    log_message("Forcing shutdown due to timeout")
    shutdown_pi()

def main():
    """Main function"""
    log_message("=== Simple Wakeup Handler Started ===")
    log_message(f"Script directory: {SCRIPT_DIR}")
    log_message(f"Log file: {LOG_FILE}")
    log_message(f"Main script: {MAIN_SCRIPT}")
    log_message(f"Total timeout: {TOTAL_TIMEOUT} seconds")
    
    # Check if running as root (needed for shutdown)
    if os.geteuid() != 0:
        log_message("WARNING: Not running as root - shutdown functionality may not work")
    
    # Get power status
    is_mains = get_power_status()
    log_message(f"Power source: {'Mains' if is_mains else 'Battery'}")
    
    # Set up timeout handler for battery mode
    if not is_mains:
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
        if not is_mains:
            signal.alarm(0)
            log_message("Timeout cancelled - script completed normally")
        
        # Handle shutdown based on power status
        if is_mains:
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
        if not is_mains:
            log_message("Forcing shutdown due to error (battery mode)")
            shutdown_pi()
        else:
            log_message("Error occurred but staying running (mains mode)")
            raise

if __name__ == "__main__":
    main() 