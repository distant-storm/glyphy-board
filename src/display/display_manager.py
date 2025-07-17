import fnmatch
import json
import logging

from utils.image_utils import resize_image, change_orientation, apply_image_enhancement
from utils.app_utils import create_writable_config_if_needed
from display.inky_display import InkyDisplay
from display.waveshare_display import WaveshareDisplay

logger = logging.getLogger(__name__)

class DisplayManager:

    """Manages the display and rendering of images."""

    def __init__(self, device_config):

        """
        Initializes the display manager and selects the correct display type 
        based on the configuration.

        Args:
            device_config (object): Configuration object containing display settings.

        Raises:
            ValueError: If an unsupported display type is specified.
        """
        
        # Check and ensure we have a writable config before proceeding
        self.device_config = create_writable_config_if_needed(device_config)
     
        display_type = device_config.get_config("display_type", default="inky")

        if display_type == "inky":
            self.display = InkyDisplay(device_config)
        elif fnmatch.fnmatch(display_type, "epd*in*"):  
            # derived from waveshare epd - we assume here that will be consistent
            # otherwise we will have to enshring the manufacturer in the 
            # display_type and then have a display_model parameter.  Will leave
            # that for future use if the need arises.
            #
            # see https://github.com/waveshareteam/e-Paper
            self.display = WaveshareDisplay(device_config)
        else:
            raise ValueError(f"Unsupported display type: {display_type}")

    def display_image(self, image, image_settings=[]):
        
        """
        Delegates image rendering to the appropriate display instance.

        Args:
            image (PIL.Image): The image to be displayed.
            image_settings (list, optional): List of settings to modify image rendering.

        Raises:
            ValueError: If no valid display instance is found.
        """

        if not hasattr(self, "display"):
            raise ValueError("No valid display instance initialized.")
        
        # Save the image
        logger.info(f"Saving image to {self.device_config.current_image_file}")
        try:
            # Ensure the image is in a compatible mode for PNG
            if image.mode in ('RGBA', 'LA', 'P'):
                # These modes are fine for PNG, but let's be explicit about transparency handling
                image.save(self.device_config.current_image_file, format='PNG')
            elif image.mode in ('CMYK', 'YCbCr'):
                # Convert unsupported modes to RGB before saving
                logger.info(f"Converting image from {image.mode} to RGB for PNG compatibility")
                rgb_image = image.convert('RGB')
                rgb_image.save(self.device_config.current_image_file, format='PNG')
            else:
                # Standard modes (RGB, L, etc.) should work fine
                image.save(self.device_config.current_image_file, format='PNG')
        except PermissionError as e:
            logger.error(f"Permission denied saving image to {self.device_config.current_image_file}: {e}")
            raise RuntimeError(f"Cannot save image due to permission error. Check file ownership and permissions.")
        except OSError as e:
            if "image has wrong mode" in str(e) or "cannot write mode" in str(e):
                logger.error(f"Image mode error: {e}. Attempting conversion to RGB.")
                try:
                    # Convert to RGB and try again
                    rgb_image = image.convert('RGB')
                    rgb_image.save(self.device_config.current_image_file, format='PNG')
                    logger.info("Successfully saved image after converting to RGB mode")
                except Exception as retry_error:
                    logger.error(f"Failed to save image even after RGB conversion: {retry_error}")
                    raise RuntimeError(f"Image save failed: {retry_error}")
            else:
                logger.error(f"OS error saving image: {e}")
                raise RuntimeError(f"Failed to save image: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving image: {e}")
            raise RuntimeError(f"Image save failed: {e}")

        # Resize and adjust orientation
        image = change_orientation(image, self.device_config.get_config("orientation"))
        image = resize_image(image, self.device_config.get_resolution(), image_settings)
        if self.device_config.get_config("inverted_image"): image = image.rotate(180)
        image = apply_image_enhancement(image, self.device_config.get_config("image_settings"))

        # Pass to the concrete instance to render to the device.
        self.display.display_image(image, image_settings)