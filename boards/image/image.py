#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import logging.config
import warnings
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Suppress warning from inky library
warnings.filterwarnings("ignore", message=".*Busy Wait: Held high.*")

from PIL import Image, ImageOps, ImageColor
from config import Config
from display.display_manager import DisplayManager

# Set up simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def display_image(image_path, pad_image=False, background_color="#ffffff"):
    """Display an image on the eink screen"""
    
    # Initialize configuration and display manager
    device_config = Config()
    display_manager = DisplayManager(device_config)
    
    # Validate image path
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Load the image
    try:
        image = Image.open(image_path)
        logger.info(f"Successfully loaded image: {image_path}")
    except Exception as e:
        logger.error(f"Failed to load image: {str(e)}")
        raise RuntimeError(f"Failed to load image: {str(e)}")
    
    # Apply padding if requested
    if pad_image:
        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        
        frame_ratio = dimensions[0] / dimensions[1]
        img_width, img_height = image.size
        padded_img_size = (
            int(img_height * frame_ratio) if img_width >= img_height else img_width,
            img_height if img_width >= img_height else int(img_width / frame_ratio)
        )
        
        bg_color = ImageColor.getcolor(background_color, "RGB")
        image = ImageOps.pad(image, padded_img_size, color=bg_color, method=Image.Resampling.LANCZOS)
        logger.info(f"Applied padding with background color: {background_color}")
    
    # Display the image
    display_manager.display_image(image)
    logger.info("Image displayed successfully")

def main():
    parser = argparse.ArgumentParser(description="Display an image on the eink screen")
    parser.add_argument("image_path", help="Path to the image file to display")
    parser.add_argument("--pad", action="store_true", help="Pad the image to fit the screen")
    parser.add_argument("--background-color", default="#ffffff", help="Background color for padding (default: white)")
    
    args = parser.parse_args()
    
    try:
        display_image(args.image_path, args.pad, args.background_color)
        print("Image displayed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 