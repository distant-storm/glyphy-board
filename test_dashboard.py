#!/usr/bin/env python3

"""
Standalone test version of the dashboard
"""

import sys
from pathlib import Path
import tempfile
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_power_status():
    """Get power status (battery or mains) - simplified for testing"""
    # For testing, just return a mock status
    return "Mains"

def get_battery_percentage():
    """Get battery percentage - simplified for testing"""
    # For testing, just return a mock percentage
    return 85

def main():
    try:
        # Use a test resolution (similar to InkyPi)
        width, height = 1600, 1200
        
        # Create a new image with white background
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%H:%M")  # Use 24-hour format for testing
        
        # Get power status
        power_status = get_power_status()
        battery_percentage = None
        if power_status == "Battery":
            battery_percentage = get_battery_percentage()
        
        # Create power status text
        if power_status == "Mains":
            power_text = "Powered by mains"
        else:
            if battery_percentage is not None:
                power_text = f"Battery powered ({battery_percentage}%)"
            else:
                power_text = "Battery powered (unknown)"
        
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
        
        # Save the image for testing
        output_path = "dashboard_test.png"
        image.save(output_path)
        
        logger.info("Dashboard test image created successfully")
        logger.info(f"Power status: {power_text}")
        logger.info(f"Date: {date_str}")
        logger.info(f"Time: {time_str}")
        logger.info(f"Image saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating dashboard test image: {e}")
        raise

if __name__ == "__main__":
    main() 