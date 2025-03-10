"""
Flask routes for VIN GUI application
"""
import os
import glob
import re
import tempfile
from flask import jsonify, request, send_file, send_from_directory, render_template, url_for
from PIL import Image, ImageOps, ImageEnhance

from vin_data import get_config, load_csv_data, extract_vin_from_filename

# Image processing cache
image_cache = {}

def setup_routes(app):
    """Setup all Flask routes"""

    @app.route('/')
    def index():
        """Serve the main HTML page"""
        return render_template('index.html')
    
    @app.route('/static/<path:path>')
    def static_files(path):
        """Serve static files"""
        return send_from_directory('static', path)

    @app.route('/api/config')
        def get_app_config():
            """Return the application configuration"""
            config = get_config()
            return jsonify({
                'raw_dir': config['raw_dir'],
                'processed_dir': config['processed_dir'],
                'prefix': config['prefix']
            })

    @app.route('/api/images')
    def get_images():
        """Get list of images in the raw directory"""
        config = get_config()
        
        if not config['raw_dir'] or not os.path.exists(config['raw_dir']):
            return jsonify({
                'images': [],
                'processed_count': 0
            })
            
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

        # Sort files to prioritize unprocessed ones (those not starting with "DONE_")
        image_files = sorted(image_files, key=lambda f: os.path.basename(f).startswith("DONE_"))

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

        # Check if we have this image in cache
        cache_key = f"{image_path}_{mode}"
        if cache_key in image_cache and os.path.exists(image_cache[cache_key]):
            return send_file(image_cache[cache_key])

        # Process image based on mode
        try:
            img = Image.open(image_path)
            
            if mode == 'original':
                output = img
            elif mode == 'inverted':
                # Create high contrast inverted image
                # Convert to grayscale
                output = img.convert('L')
                
                # Increase contrast
                enhancer = ImageEnhance.Contrast(output)
                output = enhancer.enhance(2.0)
                
                # Invert colors to help with embossed text
                output = ImageOps.invert(output)
            else:
                output = img
                
            # Create a temporary file to return
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                temp_path = tmp.name
                output.save(temp_path, format='JPEG')
                
            # Add to cache
            image_cache[cache_key] = temp_path
            
            return send_file(temp_path)
        except Exception as e:
            print(f"Error processing image: {e}")
            return send_file(image_path)

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
            # Save to processed directory
            original_image = Image.open(source_path)
            original_image.save(dest_path)
            
            # Rename the original file to mark it as processed
            raw_renamed = False
            raw_new_name = ""
            
            if not filename.startswith("DONE_"):
                raw_new_name = f"DONE_{vin}_{filename}"
                new_raw_path = os.path.join(config['raw_dir'], raw_new_name)
                os.rename(source_path, new_raw_path)
                raw_renamed = True

            # Check if this VIN is in our CSV data
            csv_data = load_csv_data()
            vin_updated = vin.upper() in csv_data['pending']

            return jsonify({
                'success': True,
                'message': f'Successfully saved as {new_filename}',
                'vin_updated': vin_updated,
                'raw_file_renamed': raw_renamed,
                'raw_file_new_name': raw_new_name
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
            raw_renamed = False
            raw_new_name = ""
            
            if choice == 'new':
                # Replace existing with new
                source_path = os.path.join(config['raw_dir'], new_file)
                dest_path = os.path.join(config['processed_dir'], existing_file)

                # Save the new image over the existing one
                original_image = Image.open(source_path)
                original_image.save(dest_path)
                
                # Rename the original file to mark it as processed
                if not new_file.startswith("DONE_"):
                    raw_new_name = f"DONE_{vin}_{new_file}"
                    new_raw_path = os.path.join(config['raw_dir'], raw_new_name)
                    os.rename(source_path, new_raw_path)
                    raw_renamed = True

                return jsonify({
                    'success': True, 
                    'message': 'Replaced existing file with new image',
                    'raw_file_renamed': raw_renamed,
                    'raw_file_new_name': raw_new_name
                })

            elif choice == 'existing':
                # Keep existing, but still mark the raw file as processed
                if not new_file.startswith("DONE_"):
                    source_path = os.path.join(config['raw_dir'], new_file)
                    raw_new_name = f"DONE_{vin}_{new_file}"
                    new_raw_path = os.path.join(config['raw_dir'], raw_new_name)
                    os.rename(source_path, new_raw_path)
                    raw_renamed = True
                
                return jsonify({
                    'success': True, 
                    'message': 'Kept existing file', 
                    'raw_file_renamed': raw_renamed,
                    'raw_file_new_name': raw_new_name
                })

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

    # Clean up image cache when app shuts down
    @app.teardown_appcontext
    def cleanup_image_cache(exception=None):
        """Clean up temporary image files"""
        try:
            for key in list(image_cache.keys()):
                if os.path.exists(image_cache[key]):
                    os.remove(image_cache[key])
            image_cache.clear()
        except Exception as e:
            print(f"Error cleaning image cache: {e}")