"""
PiJuice Shutdown Script
Manual shutdown script that properly configures PiJuice and shuts down the Pi
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def log_message(message):
    """Log a message with timestamp"""
    logger.info(message)

def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        log_message("WARNING: Not running as root - shutdown functionality may not work")
        log_message("Consider running with: sudo python3 pijuice_shutdown.py")
        return False
    return True

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
                return False
            
    except ImportError:
        log_message("✗ PiJuice library not available - using fallback shutdown method")
        return False
    except Exception as e:
        log_message(f"✗ Error configuring PiJuice shutdown: {e}")
        return False
    
    return True

def get_power_status():
    """Get current power status"""
    try:
        import pijuice
        pj = pijuice.PiJuice(1, 0x14)
        
        # Get input status
        result = pj.status.GetStatus()
        if result['error'] == 'NO_ERROR':
            status = result['data']
            if 'powerInput' in status:
                power_input = status['powerInput']
                if power_input == 'PRESENT':
                    log_message("Power source: Mains (USB power connected)")
                    return 'mains'
                else:
                    log_message("Power source: Battery")
                    return 'battery'
        
        # Fallback: check system files
        if os.path.exists("/sys/class/power_supply/pijuice/online"):
            with open("/sys/class/power_supply/pijuice/online", "r") as f:
                pijuice_status = f.read().strip()
                if pijuice_status == "1":
                    log_message("Power source: Mains (system files)")
                    return 'mains'
                else:
                    log_message("Power source: Battery (system files)")
                    return 'battery'
                    
    except Exception as e:
        log_message(f"Error getting power status: {e}")
    
    log_message("Could not determine power status")
    return 'unknown'

def get_battery_info():
    """Get battery information"""
    try:
        import pijuice
        pj = pijuice.PiJuice(1, 0x14)
        
        # Get battery status
        result = pj.status.GetBatteryStatus()
        if result['error'] == 'NO_ERROR':
            battery = result['data']
            if 'charge' in battery:
                charge = battery['charge']
                log_message(f"Battery charge: {charge}%")
            if 'voltage' in battery:
                voltage = battery['voltage']
                log_message(f"Battery voltage: {voltage}mV")
                
    except Exception as e:
        log_message(f"Error getting battery info: {e}")

def shutdown_with_pijuice(delay_seconds=5):
    """Shutdown the Pi using PiJuice"""
    log_message("=== PiJuice Shutdown Initiated ===")
    
    # Check power status
    power_source = get_power_status()
    get_battery_info()
    
    # Configure PiJuice
    pijuice_configured = configure_pijuice_shutdown()
    
    if delay_seconds > 0:
        log_message(f"Shutdown in {delay_seconds} seconds...")
        time.sleep(delay_seconds)
    
    try:
        if pijuice_configured:
            # Use PiJuice for shutdown
            import pijuice
            pj = pijuice.PiJuice(1, 0x14)
            
            log_message("Using PiJuice for shutdown...")
            
            # Try different power off methods based on available API
            if hasattr(pj.power, 'PowerOff'):
                result = pj.power.PowerOff(0)  # Power off immediately
                if result['error'] == 'NO_ERROR':
                    log_message("✓ PiJuice power off command sent successfully")
                    log_message("Pi will shutdown and PiJuice will cut power")
                else:
                    log_message(f"✗ PiJuice power off failed: {result['error']}")
                    # Fallback to system shutdown
                    log_message("Falling back to system shutdown...")
                    subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
                    log_message("System shutdown command sent")
            elif hasattr(pj.power, 'SetPowerOff'):
                # For PiJuice v1.8+, use SetPowerOff with 0 to trigger immediate power off
                result = pj.power.SetPowerOff(0)  # Power off immediately
                if result['error'] == 'NO_ERROR':
                    log_message("✓ PiJuice power off command sent successfully")
                    log_message("Pi will shutdown and PiJuice will cut power")
                else:
                    log_message(f"✗ PiJuice power off failed: {result['error']}")
                    # Fallback to system shutdown
                    log_message("Falling back to system shutdown...")
                    subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
                    log_message("System shutdown command sent")
            else:
                log_message("No PiJuice power off method available - using system shutdown")
                subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
                log_message("System shutdown command sent")
        else:
            # Fallback to system shutdown
            log_message("PiJuice not available - using system shutdown")
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
            log_message("System shutdown command sent")
            
    except Exception as e:
        log_message(f"Error with shutdown: {e}")
        log_message("Falling back to system shutdown...")
        try:
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
            log_message("System shutdown command sent")
        except Exception as e2:
            log_message(f"Error sending shutdown command: {e2}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PiJuice Shutdown Script')
    parser.add_argument('--delay', '-d', type=int, default=5, 
                       help='Delay in seconds before shutdown (default: 5)')
    parser.add_argument('--now', '-n', action='store_true',
                       help='Shutdown immediately (no delay)')
    parser.add_argument('--check', '-c', action='store_true',
                       help='Check power status and battery info only (no shutdown)')
    parser.add_argument('--configure', action='store_true',
                       help='Configure PiJuice shutdown settings only (no shutdown)')
    
    args = parser.parse_args()
    
    log_message("=== PiJuice Shutdown Script ===")
    
    # Check if running as root
    check_root()
    
    if args.check:
        log_message("=== Power Status Check ===")
        power_source = get_power_status()
        get_battery_info()
        configure_pijuice_shutdown()
        return
    
    if args.configure:
        log_message("=== PiJuice Configuration ===")
        configure_pijuice_shutdown()
        return
    
    # Determine delay
    delay = 0 if args.now else args.delay
    
    # Confirm shutdown
    if delay > 0:
        print(f"\nShutdown will occur in {delay} seconds.")
        print("Press Ctrl+C to cancel...")
        try:
            time.sleep(delay)
        except KeyboardInterrupt:
            log_message("Shutdown cancelled by user")
            return
    
    # Perform shutdown
    shutdown_with_pijuice(0)

if __name__ == "__main__":
    main() 