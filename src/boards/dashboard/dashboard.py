#!/home/webdev/.virtualenvs/pimoroni/bin/python3

import sys
from pathlib import Path
import tempfile
import os
import subprocess
from datetime import datetime

# Add src directory to Python path - it's 2 levels up from this script
sys.path.insert(0, str(Path(__file__).parents[2]))

from config import Config
from display.display_manager import DisplayManager
import logging
from PIL import Image, ImageDraw, ImageFont

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_writable_config():
    """Create a config with a writable current_image_file path"""
    config = Config()
    
    # Check if the original path is writable
    original_path = Path(config.current_image_file)
    if not original_path.parent.exists() or not os.access(original_path.parent, os.W_OK):
        # Create a temporary directory for the current image
        temp_dir = Path(tempfile.gettempdir()) / "inkypi"
        temp_dir.mkdir(exist_ok=True)
        temp_image_file = temp_dir / "current_image.png"
        
        # Override the current_image_file path
        config.current_image_file = str(temp_image_file)
        logger.info(f"Using temporary image file: {temp_image_file}")
    
    return config

def get_power_status():
    """Get power status (battery or mains)"""
    # First try using the official PiJuice utility
    try:
        # Get input status using pijuice_util.py
        script_dir = Path(__file__).parent.parent.parent.parent / 'scripts'
        logger.info(f"Running PiJuice utility from: {script_dir}")
        result = subprocess.run(
            ['/home/webdev/.virtualenvs/pimoroni/bin/python3', str(script_dir / 'pijuice_util.py'), '--get-input'],
            capture_output=True, text=True, check=False, timeout=10
        )
        logger.info(f"PiJuice utility return code: {result.returncode}")
        logger.info(f"PiJuice utility stdout: {result.stdout}")
        if result.stderr:
            logger.info(f"PiJuice utility stderr: {result.stderr}")
        
        if result.returncode == 0:
            # Parse the output to find power input status
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'usbPowerInput' in line:
                    # Extract the power input status - be more specific about the value
                    if "'usbPowerInput': 'PRESENT'" in line or '"usbPowerInput": "PRESENT"' in line:
                        logger.info("PiJuice power input: PRESENT (mains detected)")
                        return "Mains"
                    elif "'usbPowerInput': 'NOT PRESENT'" in line or '"usbPowerInput": "NOT PRESENT"' in line:
                        logger.info("PiJuice power input: NOT PRESENT (battery mode)")
                        return "Battery"
    except Exception as e:
        logger.error(f"Error using PiJuice utility: {e}")
    
    # Fallback: check system files for PiJuice setups
    try:
        # Check if we're using PiJuice by looking for PiJuice power supply
        if os.path.exists("/sys/class/power_supply/pijuice/online"):
            with open("/sys/class/power_supply/pijuice/online", "r") as f:
                pijuice_status = f.read().strip()
                return "Mains" if pijuice_status == "1" else "Battery"
        
        # Check for PiJuice battery status - if charging, likely on mains
        if os.path.exists("/sys/class/power_supply/pijuice/status"):
            with open("/sys/class/power_supply/pijuice/status", "r") as f:
                status = f.read().strip().lower()
                if status in ['charging', 'full']:
                    return "Mains"
                elif status == 'discharging':
                    return "Battery"
        
        # Fallback: check traditional AC power (only works if Pi is powered directly)
        if os.path.exists("/sys/class/power_supply/AC/online"):
            with open("/sys/class/power_supply/AC/online", "r") as f:
                ac_status = f.read().strip()
                return "Mains" if ac_status == "1" else "Battery"
                
    except Exception as e:
        logger.error(f"Error checking system power status: {e}")
    
    # Default to battery if we can't determine
    return "Battery"

def get_battery_percentage():
    """Get battery percentage"""
    # Try using the official PiJuice utility first
    try:
        # Get battery status using pijuice_util.py
        script_dir = Path(__file__).parent.parent.parent.parent / 'scripts'
        result = subprocess.run(
            ['/home/webdev/.virtualenvs/pimoroni/bin/python3', str(script_dir / 'pijuice_util.py'), '--get-battery'],
            capture_output=True, text=True, check=False, timeout=10
        )
        if result.returncode == 0:
            # Parse the output to find battery information
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'chargeLevel' in line:
                    # Extract charge level
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        return int(match.group(1))
    except Exception as e:
        logger.error(f"Error using PiJuice utility for battery info: {e}")
    
    # Fallback: check system battery files
    try:
        # Try PiJuice-specific battery paths first
        pijuice_battery_paths = [
            "/sys/class/power_supply/pijuice/capacity",
            "/sys/class/power_supply/pijuice/charge_now",
            "/sys/class/power_supply/pijuice/charge_full"
        ]
        
        # If we have charge_now and charge_full, calculate percentage
        if (os.path.exists(pijuice_battery_paths[1]) and 
            os.path.exists(pijuice_battery_paths[2])):
            with open(pijuice_battery_paths[1], "r") as f:
                charge_now = int(f.read().strip())
            with open(pijuice_battery_paths[2], "r") as f:
                charge_full = int(f.read().strip())
            if charge_full > 0:
                return int((charge_now / charge_full) * 100)
        
        # Try direct capacity file
        if os.path.exists(pijuice_battery_paths[0]):
            with open(pijuice_battery_paths[0], "r") as f:
                capacity = f.read().strip()
                try:
                    return int(capacity)
                except ValueError:
                    logger.error(f"Invalid capacity value from PiJuice: {capacity}")
        
        # Try different standard battery paths
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
    return None

def main():
    try:
        # Create config with writable image file path
        config = create_writable_config()
        display_manager = DisplayManager(config)
        
        # Get screen dimensions from config
        width, height = config.get_resolution()
        
        # Create a new image with white background
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        
        # Get power status
        power_status = get_power_status()
        battery_percentage = None
        
        logger.info(f"Power status detected: {power_status}")
        
        # Get battery percentage regardless of power status (useful information)
        battery_percentage = get_battery_percentage()
        
        # Create power status text
        if power_status == "Mains":
            if battery_percentage is not None:
                power_text = f"Powered by mains (Battery: {battery_percentage}%)"
                logger.info(f"Setting power text to: Powered by mains (Battery: {battery_percentage}%)")
            else:
                power_text = "Powered by mains"
                logger.info("Setting power text to: Powered by mains")
        else:
            # Battery power
            if battery_percentage is not None:
                power_text = f"Battery powered ({battery_percentage}%)"
                logger.info(f"Setting power text to: Battery powered ({battery_percentage}%)")
            else:
                power_text = "Battery powered (unknown)"
                logger.info("Setting power text to: Battery powered (unknown)")
        
        # Choose font sizes - smaller fonts for top positioning
        large_font_size = min(width, height) // 20  # Smaller than before
        medium_font_size = min(width, height) // 25
        small_font_size = min(width, height) // 30
        
        try:
            large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", large_font_size)
            medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", medium_font_size)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", small_font_size)
        except:
            large_font = ImageFont.load_default()
            medium_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Position text at the top with some padding
        padding = 20
        y_position = padding
        
        # Draw "No Schedule" text (largest)
        no_schedule_text = "No Schedule"
        bbox = draw.textbbox((0, 0), no_schedule_text, font=large_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_position), no_schedule_text, fill='black', font=large_font)
        y_position += bbox[3] - bbox[1] + 15
        
        # Draw date (medium)
        bbox = draw.textbbox((0, 0), date_str, font=medium_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_position), date_str, fill='black', font=medium_font)
        y_position += bbox[3] - bbox[1] + 10
        
        # Draw time (medium)
        bbox = draw.textbbox((0, 0), time_str, font=medium_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_position), time_str, fill='black', font=medium_font)
        y_position += bbox[3] - bbox[1] + 15
        
        # Draw power status (smallest)
        bbox = draw.textbbox((0, 0), power_text, font=small_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_position), power_text, fill='black', font=small_font)
        
        # Display the image
        display_manager.display_image(image)
        
        logger.info("Dashboard displayed successfully")
        logger.info(f"Power status: {power_text}")
        logger.info(f"Date: {date_str}")
        logger.info(f"Time: {time_str}")
        
    except Exception as e:
        logger.error(f"Error displaying dashboard: {e}")
        raise

if __name__ == "__main__":
    main() 