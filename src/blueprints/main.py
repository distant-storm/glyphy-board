from flask import Blueprint, render_template, current_app, request, jsonify, send_from_directory
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)

@main_bp.route('/')
def main():
    device_config = current_app.config['DEVICE_CONFIG']
    plugins = device_config.get_plugins()
    return render_template('inky.html', plugins=plugins, config=device_config.get_config())

@main_bp.route('/dashboard', methods=['POST'])
def dashboard():
    """Execute the dashboard.py script to display dashboard on the eink screen"""
    try:
        # Get the path to the dashboard script
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'boards', 'dashboard', 'dashboard.py')
        
        # Execute the dashboard script
        import subprocess
        result = subprocess.run([script_path], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("Dashboard displayed successfully")
            return jsonify({"success": True, "message": "Dashboard displayed successfully!"})
        else:
            logger.error(f"Dashboard script failed: {result.stderr}")
            return jsonify({"error": f"Dashboard script failed: {result.stderr}"}), 500
            
    except subprocess.TimeoutExpired:
        logger.error("Dashboard script timed out")
        return jsonify({"error": "Dashboard script timed out"}), 500
    except Exception as e:
        logger.error(f"Error executing dashboard: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@main_bp.route('/photo-management')
def photo_management():
    """Photo management page for viewing and deleting photos in the album"""
    try:
        # Get the photo album directory path
        photo_album_dir = Path(__file__).parent.parent / "boards" / "photo-album" / "photos"
        
        if not photo_album_dir.exists():
            return render_template('photo_management.html', photos=[], error="Photo album directory not found")
        
        # Get all image files
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}
        photos = []
        
        for file_path in photo_album_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                # Get file stats
                stat = file_path.stat()
                photos.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
        
        # Sort by modification time (newest first)
        photos.sort(key=lambda x: x['modified'], reverse=True)
        
        return render_template('photo_management.html', photos=photos)
        
    except Exception as e:
        logger.error(f"Error loading photo management: {e}")
        return render_template('photo_management.html', photos=[], error=str(e))

@main_bp.route('/delete-photo', methods=['POST'])
def delete_photo():
    """Delete a photo from the album"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"error": "Filename is required"}), 400
        
        # Get the photo album directory path
        photo_album_dir = Path(__file__).parent.parent / "boards" / "photo-album" / "photos"
        file_path = photo_album_dir / filename
        
        # Security check: ensure the file is within the photos directory
        try:
            file_path.resolve().relative_to(photo_album_dir.resolve())
        except ValueError:
            return jsonify({"error": "Invalid file path"}), 400
        
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        # Delete the file
        file_path.unlink()
        
        return jsonify({"success": True, "message": f"Deleted {filename}"})
        
    except Exception as e:
        logger.error(f"Error deleting photo: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/photo-thumbnail/<path:filename>')
def photo_thumbnail(filename):
    """Serve photo thumbnails"""
    try:
        photo_album_dir = Path(__file__).parent.parent / "boards" / "photo-album" / "photos"
        file_path = photo_album_dir / filename
        
        # Security check: ensure the file is within the photos directory
        try:
            file_path.resolve().relative_to(photo_album_dir.resolve())
        except ValueError:
            return "Invalid file path", 400
        
        if not file_path.exists():
            return "File not found", 404
        
        return send_from_directory(photo_album_dir, filename)
        
    except Exception as e:
        logger.error(f"Error serving photo thumbnail: {e}")
        return "Error", 500