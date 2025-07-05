#!/usr/bin/env python3

import os
import sys
import logging
import logging.config
import warnings
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Suppress warning from inky library
warnings.filterwarnings("ignore", message=".*Busy Wait: Held high.*")

from PIL import Image, ImageDraw
from config import Config
from display.display_manager import DisplayManager
from utils.app_utils import get_font

# Set up simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def display_dashboard():
    """Display the text 'dashboard' on the eink screen"""
    
    # Initialize configuration and display manager
    device_config = Config()
    display_manager = DisplayManager(device_config)
    
    # Get screen dimensions
    dimensions = device_config.get_resolution()
    if device_config.get_config("orientation") == "vertical":
        dimensions = dimensions[::-1]
    
    width, height = dimensions
    
    # Create a new image with white background
    bg_color = (255, 255, 255)  # White
    text_color = (0, 0, 0)      # Black
    
    image = Image.new("RGB", dimensions, bg_color)
    image_draw = ImageDraw.Draw(image)
    
    # Calculate font size based on screen width
    font_size = int(width * 0.15)  # 15% of screen width
    
    # Get font
    font = get_font("Jost", font_size, "bold")
    if font is None:
        # Fallback to default font if Jost is not available
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
        except:
            font = None
    
    # Draw the text "dashboard" centered on the screen
    text = "dashboard"
    image_draw.text(
        (width/2, height/2), 
        text, 
        anchor="mm",  # Middle-middle anchor
        fill=text_color, 
        font=font
    )
    
    # Display the image
    display_manager.display_image(image)
    logger.info("Dashboard displayed successfully")

def main():
    try:
        display_dashboard()
        print("Dashboard displayed successfully!")
    except Exception as e:
        logger.error(f"Error displaying dashboard: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 