#!/usr/bin/env python3
"""
Power Status Board Script - Displays power source and battery information
"""

import sys
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Add src directory to Python path - it's 2 levels up from this script
sys.path.insert(0, str(Path(__file__).parents[2]))

from config import Config
from display.display_manager import DisplayManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
                logger.info(f"PiJuice power status: {power_status}")
                return power_status == "PRESENT"  # True if mains, False if battery
        except Exception as e:
            logger.error(f"Error getting PiJuice power status: {e}")
    
    # Fallback: check system power files
    try:
        if os.path.exists("/sys/class/power_supply/AC/online"):
            with open("/sys/class/power_supply/AC/online", "r") as f:
                ac_status = f.read().strip()
                is_mains = ac_status == "1"
                logger.info(f"System power status: {'Mains' if is_mains else 'Battery'}")
                return is_mains
    except Exception as e:
        logger.error(f"Error checking system power status: {e}")
    
    # Default to battery if we can't determine
    logger.warning("Could not determine power status, assuming battery")
    return False

def get_battery_percentage():
    """Get battery percentage"""
    if check_pijuice_available():
        try:
            # Get battery charge from PiJuice
            result = subprocess.run(
                ['pijuice_cli', 'status', '--get', 'charge'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                charge = result.stdout.strip()
                try:
                    return int(charge)
                except ValueError:
                    logger.error(f"Invalid charge value from PiJuice: {charge}")
        except Exception as e:
            logger.error(f"Error getting PiJuice battery charge: {e}")
    
    # Fallback: check system battery files
    try:
        # Try different battery paths
        battery_paths = [
            "/sys/class/power_supply/BAT0/capacity",
            "/sys/class/power_supply/BAT1/capacity",
            "/sys/class/power_supply/battery/capacity"
        ]
        
        for battery_path in battery_paths:
            if os.path.exists(battery_path):
                with open(battery_path, "r") as f:
                    capacity = f.read().strip()
                    try:
                        return int(capacity)
                    except ValueError:
                        logger.error(f"Invalid capacity value from {battery_path}: {capacity}")
                        continue
    except Exception as e:
        logger.error(f"Error checking system battery capacity: {e}")
    
    # Default to unknown if we can't determine
    logger.warning("Could not determine battery percentage")
    return None

def create_power_status_image(config, is_mains, battery_percentage):
    """Create an image showing power status"""
    # Get screen dimensions from config
    width, height = config.get_resolution()
    
    # Create a new image with white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Choose font size based on screen size
    font_size = min(width, height) // 12
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Determine the text to display
    if is_mains:
        text = "Powered by mains"
    else:
        if battery_percentage is not None:
            text = f"Battery powered ({battery_percentage}%)"
        else:
            text = "Battery powered (unknown)"
    
    # Calculate position to center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='black', font=font)
    
    # Add timestamp at the bottom
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_font_size = font_size // 2
    try:
        timestamp_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", timestamp_font_size)
    except:
        timestamp_font = ImageFont.load_default()
    
    timestamp_bbox = draw.textbbox((0, 0), timestamp, font=timestamp_font)
    timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
    timestamp_height = timestamp_bbox[3] - timestamp_bbox[1]
    
    timestamp_x = (width - timestamp_width) // 2
    timestamp_y = y + text_height + 20
    
    draw.text((timestamp_x, timestamp_y), timestamp, fill='black', font=timestamp_font)
    
    return image

def main():
    """Main function for power status board display"""
    try:
        logger.info("=== Power Status Board Started ===")
        
        # Create config and display manager
        config = Config()
        display_manager = DisplayManager(config)
        
        # Get power status
        is_mains = get_power_status()
        battery_percentage = None if is_mains else get_battery_percentage()
        
        logger.info(f"Power source: {'Mains' if is_mains else 'Battery'}")
        if not is_mains and battery_percentage is not None:
            logger.info(f"Battery percentage: {battery_percentage}%")
        
        # Create the power status image
        image = create_power_status_image(config, is_mains, battery_percentage)
        
        # Display the image
        display_manager.display_image(image)
        
        logger.info("Power status board displayed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error displaying power status board: {e}")
        raise

if __name__ == "__main__":
    sys.exit(main()) 