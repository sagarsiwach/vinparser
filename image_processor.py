"""
Image processor module for VIN GUI application
"""
import os
import tempfile
from PIL import Image, ImageEnhance, ImageOps

# Image processing cache
image_cache = {}

def setup_image_cache():
    """Initialize the image cache"""
    global image_cache
    image_cache = {}

def cleanup_image_cache():
    """Clean up temporary image files"""
    try:
        for key in list(image_cache.keys()):
            if os.path.exists(image_cache[key]):
                os.remove(image_cache[key])
        image_cache.clear()
    except Exception as e:
        print(f"Error cleaning image cache: {e}")

def process_image(image_path, mode='original'):
    """Process image based on selected mode"""
    # Check if we have this image in cache
    cache_key = f"{image_path}_{mode}"
    if cache_key in image_cache:
        return image_cache[cache_key]

    try:
        img = Image.open(image_path)

        if mode == 'original':
            output = img
        elif mode == 'bw':
            output = ImageOps.grayscale(img)
        elif mode == 'contrast':
            enhancer = ImageEnhance.Contrast(img)
            output = enhancer.enhance(2.0)  # Increase contrast by factor of 2
        elif mode == 'sharp':
            enhancer = ImageEnhance.Sharpness(img)
            output = enhancer.enhance(2.0)  # Increase sharpness by factor of 2
        else:
            output = img

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            temp_path = tmp.name
            output.save(temp_path, format='JPEG')

        # Store in cache
        image_cache[cache_key] = temp_path
        return temp_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return image_path
