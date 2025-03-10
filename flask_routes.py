"""
Flask routes for VIN GUI application
"""
import os
import glob
import re
from flask import jsonify, request, send_file, send_from_directory
from PIL import Image

from vin_data import get_config, load_csv_data, extract_vin_from_filename
from image_processor import process_image
from templates import get_html_template

def setup_routes(app):
    """Setup all Flask routes"""

    @app.route('/')
    def index():
        """Serve the main HTML page"""
        return get_html_template()

    @app.route('/api/images')
    def get_images():
        """Get list of images in the raw directory"""
        config = get_config()
        image_files = sorted(
            glob.glob(os.path.join(config['raw_dir'], '*.jpg')) +
            glob.glob(os.path.join(config['raw_dir'], '*.jpeg')) +
            glob.glob(os.path.join(config['raw_dir'], '*.png'))
        )

        # Count processed files
        processed_count = 0
        if os.path.exists(config['processed_dir']):
            processed_count = len([f for f in os.listdir(config['processed_dir'])
                                  if f.lower().startswith(config['prefix'].lower()) and
                                  os.path.isfile(os.path.join(config['processed_dir'], f))])

        return jsonify({
            'images': [os.path.basename(f) for f in image_files],
            'processed_count': processed_count
        })

    @app.route('/api/vins')
    def get_vins():
        """Get VIN data"""
        return jsonify(load_csv_data())

    @app.route('/image/<path:filename>')
    def serve_image(filename):
        """Serve an image from the raw images directory with processing"""
        config = get_config()
        mode = request.args.get('mode', 'original')
        image_path = os.path.join(config['raw_dir'], filename)

        if not os.path.exists(image_path):
            return "Image not found", 404

        # Process image based on mode
        processed_path = process_image(image_path, mode)
        return send_file(processed_path)

    @app.route('/processed/<path:filename>')
    def serve_processed_image(filename):
        """Serve an image from the processed images directory"""
        config = get_config()
        return send_from_directory(config['processed_dir'], filename)

    @app.route('/api/rename', methods=['POST'])
    def rename_file():
        """Rename a file based on VIN input"""
        config = get_config()
        data = request.json
        filename = data.get('filename')
        vin = data.get('vin', '').strip().upper()

        if not vin or len(vin) != 6 or not filename:
            return jsonify({'success': False, 'message': 'Invalid VIN or filename'})

        # Validate VIN format (alphanumeric only)
        if not vin.isalnum():
            return jsonify({'success': False, 'message': 'VIN must contain only letters and numbers'})

        source_path = os.path.join(config['raw_dir'], filename)
        if not os.path.exists(source_path):
            return jsonify({'success': False, 'message': f'Source file not found: {filename}'})

        # Create destination directory if it doesn't exist
        os.makedirs(config['processed_dir'], exist_ok=True)

        # Create new filename with VIN
        file_ext = os.path.splitext(filename)[1]
        new_filename = f"{config['prefix']}{vin}{file_ext}"
        dest_path = os.path.join(config['processed_dir'], new_filename)

        # Check if a file with this VIN already exists
        existing_files = []
        if os.path.exists(config['processed_dir']):
            existing_files = [f for f in os.listdir(config['processed_dir'])
                             if f.lower().endswith(f"{vin.lower()}{file_ext.lower()}") and
                             os.path.isfile(os.path.join(config['processed_dir'], f))]

        if existing_files:
            return jsonify({
                'success': False,
                'duplicate': True,
                'existing_file': existing_files[0],
                'message': f'VIN {vin} already exists in processed files'
            })

        try:
            # Use original image mode for saving to processed directory
            original_image = Image.open(source_path)
            original_image.save(dest_path)

            # Check if this VIN is in our CSV data
            csv_data = load_csv_data()
            vin_updated = vin.upper() in csv_data['pending']

            return jsonify({
                'success': True,
                'message': f'Successfully renamed to {new_filename}',
                'vin_updated': vin_updated
            })
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error renaming file: {str(e)}'})

    @app.route('/api/resolve-duplicate', methods=['POST'])
    def resolve_duplicate():
        """Resolve duplicate VIN conflict"""
        config = get_config()
        data = request.json
        existing_file = data.get('existing_file')
        new_file = data.get('new_file')
        vin = data.get('vin', '').upper()
        choice = data.get('choice')

        if not existing_file or not new_file or not vin or not choice:
            return jsonify({'success': False, 'message': 'Missing required parameters'})

        try:
            if choice == 'new':
                # Replace existing with new
                source_path = os.path.join(config['raw_dir'], new_file)
                dest_path = os.path.join(config['processed_dir'], existing_file)

                # Use original image mode for saving to processed directory
                original_image = Image.open(source_path)
                original_image.save(dest_path)

                return jsonify({'success': True, 'message': 'Replaced existing file with new image'})

            elif choice == 'existing':
                # Keep existing, do nothing
                return jsonify({'success': True, 'message': 'Kept existing file'})

            else:
                return jsonify({'success': False, 'message': 'Invalid choice'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'Error resolving duplicate: {str(e)}'})

    @app.route('/api/delete', methods=['POST'])
    def delete_image():
        """Delete an image from the raw directory"""
        config = get_config()
        data = request.json
        filename = data.get('filename')

        if not filename:
            return jsonify({'success': False, 'message': 'No filename provided'})

        try:
            file_path = os.path.join(config['raw_dir'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({'success': True, 'message': f'Deleted {filename}'})
            else:
                return jsonify({'success': False, 'message': f'File not found: {filename}'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error deleting file: {str(e)}'})
