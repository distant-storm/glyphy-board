#!/usr/bin/env python3
"""
Photo Album Board Script

Displays images from a photos directory. If no specific image is provided,
randomly selects one from the photos directory.

Usage:
    python3 photo-album.py [image_path] [--pad] [--background-color COLOR]
"""

import sys
from pathlib import Path
import tempfile
import os

# Add src directory to Python path - it's 2 levels up from this script
sys.path.insert(0, str(Path(__file__).parents[2]))

from config import Config
from display.display_manager import DisplayManager
import logging
import argparse
import random
from PIL import Image, ImageOps, ImageColor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_random_photo(photos_dir):
    """Get a random photo from the photos directory"""
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp']
    
    photos_path = Path(photos_dir)
    if not photos_path.exists():
        raise FileNotFoundError(f"Photos directory not found: {photos_path}")
    
    photo_files = []
    for file_path in photos_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            photo_files.append(str(file_path))
    
    if not photo_files:
        raise FileNotFoundError(f"No photos found in {photos_path}. Supported formats: {supported_formats}")
    
    selected_photo = random.choice(photo_files)
    logger.info(f"Selected random photo: {Path(selected_photo).name} from {len(photo_files)} available photos")
    return selected_photo

def process_image_like_upload_plugin(image, device_config, pad_image=False, background_color="white"):
    """Process image exactly like the image_upload plugin does"""
    if pad_image:
        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        frame_ratio = dimensions[0] / dimensions[1]
        img_width, img_height = image.size
        padded_img_size = (int(img_height * frame_ratio) if img_width >= img_height else img_width,
                          img_height if img_width >= img_height else int(img_width / frame_ratio))
        background_color = ImageColor.getcolor(background_color, "RGB")
        return ImageOps.pad(image, padded_img_size, color=background_color, method=Image.Resampling.LANCZOS)
    return image

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

def main():
    parser = argparse.ArgumentParser(description='Display a random photo from the photo album on the eink display')
    parser.add_argument('image_path', nargs='?', help='Path to specific image file (optional)')
    parser.add_argument('--pad', action='store_true', help='Pad the image to fit the screen while maintaining aspect ratio')
    parser.add_argument('--background-color', default='white', help='Background color for padding (default: white)')
    
    args = parser.parse_args()
    
    try:
        # Get the photos directory relative to this script
        photos_dir = Path(__file__).parent / 'photos'
        logger.info(f"Photos directory: {photos_dir.absolute()}")
        
        # Determine which image to use
        if args.image_path:
            image_path = args.image_path
            logger.info(f"Using specified image: {image_path}")
        else:
            image_path = get_random_photo(photos_dir)
            logger.info(f"Selected random photo: {image_path}")
        
        # Create config with writable image file path
        config = create_writable_config()
        display_manager = DisplayManager(config)
        
        # Open the image using Pillow (exactly like image_upload plugin)
        try:
            image = Image.open(image_path)
            logger.info(f"Successfully loaded image: {image_path}")
        except Exception as e:
            logger.error(f"Failed to read image file: {str(e)}")
            raise RuntimeError("Failed to read image file.")
        
        # Process image exactly like image_upload plugin
        processed_image = process_image_like_upload_plugin(
            image, 
            config, 
            args.pad, 
            args.background_color
        )
        
        # Display the image (pass PIL Image object directly)
        logger.info("Displaying image on eink screen...")
        display_manager.display_image(processed_image)
        
        logger.info("Photo album display completed successfully")
        
    except Exception as e:
        logger.error(f"Error in photo album: {e}")
        raise

if __name__ == "__main__":
    main() 