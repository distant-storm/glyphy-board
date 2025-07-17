#!/bin/bash

# Fix permissions for glyphy-board current_image.png file
# Run this script with sudo on your production server

echo 'Fixing glyphy-board file permissions...'

# Determine the user running the application (usually webdev or www-data)
APP_USER=$(ps aux | grep '[g]lyphy' | head -1 | awk '{print $1}')
if [ -z "$APP_USER" ]; then
    echo 'Could not determine application user, defaulting to webdev'
    APP_USER='webdev'
fi

echo "Application appears to be running as user: $APP_USER"

# Path to the glyphy-board project
PROJECT_PATH="/home/mattdrumm/glyphy-board"
STATIC_IMAGES_PATH="$PROJECT_PATH/src/static/images"
CURRENT_IMAGE_FILE="$STATIC_IMAGES_PATH/current_image.png"

echo "Project path: $PROJECT_PATH"
echo "Static images path: $STATIC_IMAGES_PATH"

# Create the directory if it doesn't exist
if [ ! -d "$STATIC_IMAGES_PATH" ]; then
    echo "Creating static images directory..."
    sudo mkdir -p "$STATIC_IMAGES_PATH"
fi

# Set correct ownership and permissions for the entire static/images directory
echo "Setting ownership to $APP_USER for static images directory..."
sudo chown -R "$APP_USER:$APP_USER" "$STATIC_IMAGES_PATH"

echo "Setting permissions for static images directory..."
sudo chmod 755 "$STATIC_IMAGES_PATH"

# If current_image.png exists, fix its permissions
if [ -f "$CURRENT_IMAGE_FILE" ]; then
    echo "Fixing current_image.png permissions..."
    sudo chown "$APP_USER:$APP_USER" "$CURRENT_IMAGE_FILE"
    sudo chmod 644 "$CURRENT_IMAGE_FILE"
else
    echo "Creating current_image.png with correct permissions..."
    sudo touch "$CURRENT_IMAGE_FILE"
    sudo chown "$APP_USER:$APP_USER" "$CURRENT_IMAGE_FILE"
    sudo chmod 644 "$CURRENT_IMAGE_FILE"
fi

# Also fix permissions for the plugins directory
PLUGINS_IMAGES_PATH="$STATIC_IMAGES_PATH/plugins"
if [ ! -d "$PLUGINS_IMAGES_PATH" ]; then
    echo "Creating plugins images directory..."
    sudo mkdir -p "$PLUGINS_IMAGES_PATH"
fi

echo "Setting permissions for plugins images directory..."
sudo chown -R "$APP_USER:$APP_USER" "$PLUGINS_IMAGES_PATH"
sudo chmod 755 "$PLUGINS_IMAGES_PATH"

# Verify the changes
echo ""
echo "Verification:"
echo "Static images directory:"
ls -la "$STATIC_IMAGES_PATH"
echo ""
echo "Current image file:"
ls -la "$CURRENT_IMAGE_FILE" 2>/dev/null || echo "current_image.png does not exist yet"

echo ""
echo "Permissions fix completed!"
echo "The application should now be able to write to the current_image.png file." 