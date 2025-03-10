"""
Image processor module for VIN GUI application
"""
import os
import tempfile
from PIL import Image, ImageEnhance, ImageOps

def process_image(image_path, mode='original'):
    """Process image based on selected mode"""
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

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            temp_path = tmp.name
            output.save(temp_path, format='JPEG')

        return temp_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return image_path