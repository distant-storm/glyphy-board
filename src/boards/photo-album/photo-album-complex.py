"""
Photo Album Board Script

Displays images from a photos directory. If no specific image is provided,
randomly selects one from the photos directory.

Usage:
    python3 photo-album.py [image_path] [--pad] [--background-color COLOR]
    
    If no image_path is provided, randomly selects from ./photos/ directory
"""

import os
import sys
import random
import argparse
import logging
import logging.config
import warnings
from pathlib import Path
from PIL import Image, ImageOps, ImageColor

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Also add the project root to handle cross-module imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Suppress warning from inky library
warnings.filterwarnings("ignore", message=".*Busy Wait: Held high.*")

from config import Config
from display.display_manager import DisplayManager

# Set up simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_supported_image_extensions():
    """Get list of supported image file extensions"""
    return {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}

def find_random_photo(photos_dir):
    """Find a random photo from the photos directory"""
    photos_path = Path(photos_dir)
    
    if not photos_path.exists():
        logger.error(f"Photos directory not found: {photos_path}")
        return None
    
    # Get all image files from the photos directory
    supported_extensions = get_supported_image_extensions()
    image_files = []
    
    for file_path in photos_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            image_files.append(file_path)
    
    if not image_files:
        logger.error(f"No image files found in {photos_path}")
        return None
    
    # Select random image
    selected_image = random.choice(image_files)
    logger.info(f"Randomly selected photo: {selected_image.name}")
    return selected_image

def load_and_process_image(image_path, pad_to_fit=False, background_color='white'):
    """Load and process image for display"""
    try:
        # Open and convert image
        image = Image.open(image_path)
        logger.info(f"Successfully loaded image: {image_path}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            logger.info(f"Converting image from {image.mode} to RGB")
            image = image.convert('RGB')
        
        original_size = image.size
        logger.info(f"Original image size: {original_size}")
        
        if pad_to_fit:
            # Get device config and dimensions
            device_config = Config()
            dimensions = device_config.get_resolution()
            if device_config.get_config("orientation") == "vertical":
                dimensions = dimensions[::-1]
            
            # Calculate padded size
            frame_ratio = dimensions[0] / dimensions[1]
            img_width, img_height = image.size
            padded_img_size = (
                int(img_height * frame_ratio) if img_width >= img_height else img_width,
                img_height if img_width >= img_height else int(img_width / frame_ratio)
            )
            
            # Apply padding
            bg_color = ImageColor.getcolor(background_color, "RGB")
            image = ImageOps.pad(image, padded_img_size, color=bg_color, method=Image.Resampling.LANCZOS)
            logger.info(f"Applied padding with background color: {background_color}")
        
        logger.info(f"Final image size: {image.size}")
        return image
        
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {str(e)}")
        raise

def main():
    """Main function to display photo album"""
    parser = argparse.ArgumentParser(description='Display image on eink screen from photo album')
    parser.add_argument('image_path', nargs='?', help='Path to image file (optional - if not provided, selects random photo)')
    parser.add_argument('--pad', action='store_true', help='Pad image to fit screen while maintaining aspect ratio')
    parser.add_argument('--background-color', default='white', help='Background color for padding (default: white)')
    
    args = parser.parse_args()
    
    try:
        # Get the photos directory (relative to this script)
        script_dir = Path(__file__).parent
        photos_dir = script_dir / "photos"
        
        # Determine which image to use
        if args.image_path:
            # Use provided image path
            image_path = Path(args.image_path)
            if not image_path.exists():
                logger.error(f"Image file not found: {image_path}")
                return 1
            logger.info(f"Using provided image: {image_path}")
        else:
            # Select random photo from photos directory
            image_path = find_random_photo(photos_dir)
            if not image_path:
                logger.error("No photo could be selected")
                return 1
        
        # Initialize configuration and display manager
        device_config = Config()
        display_manager = DisplayManager(device_config)
        
        # Load and process the image
        logger.info(f"Loading image: {image_path}")
        processed_image = load_and_process_image(
            image_path, 
            args.pad, 
            args.background_color
        )
        
        # Display the image
        logger.info("Displaying image on eink screen...")
        display_manager.display_image(processed_image)
        
        logger.info("Photo album display completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error in photo album display: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 