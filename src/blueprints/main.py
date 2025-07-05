from flask import Blueprint, request, jsonify, current_app, render_template
import subprocess
import os
import logging

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)

@main_bp.route('/')
def main_page():
    device_config = current_app.config['DEVICE_CONFIG']
    return render_template('inky.html', config=device_config.get_config(), plugins=device_config.get_plugins())

@main_bp.route('/dashboard', methods=['POST'])
def dashboard():
    """Execute the dashboard.py script to display dashboard on the eink screen"""
    try:
        # Get the path to the dashboard script
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'boards', 'dashboard.py')
        
        # Execute the dashboard script
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