#!/usr/bin/env python3

"""
PiJuice Diagnostic Script
Helps identify available PiJuice methods and troubleshoot API issues
"""

import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_pijuice_installation():
    """Check if PiJuice library is installed"""
    try:
        import pijuice
        logger.info("✓ PiJuice library is installed")
        logger.info(f"PiJuice version: {pijuice.__version__ if hasattr(pijuice, '__version__') else 'Unknown'}")
        return True
    except ImportError:
        logger.error("✗ PiJuice library is not installed")
        logger.info("Install with: pip3 install pijuice")
        return False

def check_pijuice_connection():
    """Check if PiJuice is connected and accessible"""
    try:
        import pijuice
        pj = pijuice.PiJuice(1, 0x14)
        
        # Try to get status
        result = pj.status.GetStatus()
        if result['error'] == 'NO_ERROR':
            logger.info("✓ PiJuice is connected and responding")
            status = result['data']
            logger.info(f"Status: {status}")
            return True
        else:
            logger.error(f"✗ PiJuice connection failed: {result['error']}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error connecting to PiJuice: {e}")
        return False

def list_available_methods():
    """List all available PiJuice methods"""
    try:
        import pijuice
        pj = pijuice.PiJuice(1, 0x14)
        
        logger.info("=== Available PiJuice Methods ===")
        
        # Power methods
        logger.info("Power methods:")
        power_methods = [method for method in dir(pj.power) if not method.startswith('_')]
        for method in sorted(power_methods):
            logger.info(f"  pj.power.{method}")
        
        # Status methods
        logger.info("Status methods:")
        status_methods = [method for method in dir(pj.status) if not method.startswith('_')]
        for method in sorted(status_methods):
            logger.info(f"  pj.status.{method}")
        
        # Config methods
        logger.info("Config methods:")
        config_methods = [method for method in dir(pj.config) if not method.startswith('_')]
        for method in sorted(config_methods):
            logger.info(f"  pj.config.{method}")
        
        # IO methods
        logger.info("IO methods:")
        io_methods = [method for method in dir(pj.io) if not method.startswith('_')]
        for method in sorted(io_methods):
            logger.info(f"  pj.io.{method}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error listing methods: {e}")
        return False

def test_power_methods():
    """Test specific power methods"""
    try:
        import pijuice
        pj = pijuice.PiJuice(1, 0x14)
        
        logger.info("=== Testing Power Methods ===")
        
        # Test GetPowerOffOnShutdown
        if hasattr(pj.power, 'GetPowerOffOnShutdown'):
            logger.info("✓ GetPowerOffOnShutdown method exists")
            try:
                result = pj.power.GetPowerOffOnShutdown()
                logger.info(f"  Result: {result}")
            except Exception as e:
                logger.error(f"  Error calling GetPowerOffOnShutdown: {e}")
        else:
            logger.warning("✗ GetPowerOffOnShutdown method not found")
        
        # Test SetPowerOffOnShutdown
        if hasattr(pj.power, 'SetPowerOffOnShutdown'):
            logger.info("✓ SetPowerOffOnShutdown method exists")
        else:
            logger.warning("✗ SetPowerOffOnShutdown method not found")
        
        # Test PowerOff
        if hasattr(pj.power, 'PowerOff'):
            logger.info("✓ PowerOff method exists")
        else:
            logger.warning("✗ PowerOff method not found")
        
        # Test SetPowerOff
        if hasattr(pj.power, 'SetPowerOff'):
            logger.info("✓ SetPowerOff method exists")
        else:
            logger.warning("✗ SetPowerOff method not found")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error testing power methods: {e}")
        return False

def get_current_status():
    """Get current PiJuice status"""
    try:
        import pijuice
        pj = pijuice.PiJuice(1, 0x14)
        
        logger.info("=== Current PiJuice Status ===")
        
        # Get status
        result = pj.status.GetStatus()
        if result['error'] == 'NO_ERROR':
            status = result['data']
            logger.info(f"Status: {status}")
        
        # Get battery status
        result = pj.status.GetBatteryStatus()
        if result['error'] == 'NO_ERROR':
            battery = result['data']
            logger.info(f"Battery: {battery}")
        
        # Get charge level
        result = pj.status.GetChargeLevel()
        if result['error'] == 'NO_ERROR':
            charge = result['data']
            logger.info(f"Charge Level: {charge}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error getting status: {e}")
        return False

def main():
    """Main diagnostic function"""
    logger.info("=== PiJuice Diagnostic Tool ===")
    
    # Check installation
    if not check_pijuice_installation():
        return False
    
    # Check connection
    if not check_pijuice_connection():
        return False
    
    # List available methods
    list_available_methods()
    
    # Test power methods
    test_power_methods()
    
    # Get current status
    get_current_status()
    
    logger.info("=== Diagnostic Complete ===")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 