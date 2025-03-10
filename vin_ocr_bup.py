import os
import requests
import time
import glob
import base64
import argparse
from datetime import datetime
import shutil
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import io
import re

# Add Tesseract support
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Folder paths
RAW_IMAGES_DIR = "raw_images"
PROCESSED_IMAGES_DIR = "processed_images"
ENHANCED_IMAGES_DIR = "enhanced_images"

# Ensure directories exist
os.makedirs(RAW_IMAGES_DIR, exist_ok=True)
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)
os.makedirs(ENHANCED_IMAGES_DIR, exist_ok=True)

def enhance_image(image_path):
    """Enhance the image to improve OCR results"""
    img = Image.open(image_path)

    # Convert to grayscale
    img = img.convert('L')

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # Apply sharpening
    img = img.filter(ImageFilter.SHARPEN)

    # Invert colors (often helps with stamped/embossed text)
    img = ImageOps.invert(img)

    # Save enhanced image
    filename = os.path.basename(image_path)
    enhanced_path = os.path.join(ENHANCED_IMAGES_DIR, f"enhanced_{filename}")
    img.save(enhanced_path)

    return enhanced_path

def encode_image_to_base64(image_path):
    """Convert an image to base64 encoding"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_vin_from_image_api(image_path, api_key):
    """Extract VIN number from image using OpenRouter API"""
    # Encode image to base64
    base64_image = encode_image_to_base64(image_path)

    # Enhanced prompt with more details
    prompt = """
    This image shows a vehicle part with a VIN (Vehicle Identification Number) stamped or engraved on it.
    The VIN is usually 17 characters long with letters and numbers.

    Extract the complete VIN number if visible. If you can only see part of it, extract all visible characters.
    Focus especially on the last 6 characters of the VIN.

    Respond with JUST the VIN number or visible portion (no additional text).
    """

    # Prepare the payload for OpenRouter API
    payload = {
        "model": "qwen/qwen2.5-vl-72b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    # Call OpenRouter API
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost',
        'X-Title': 'Local VIN OCR'
    }

    response = requests.post('https://openrouter.ai/api/v1/chat/completions',
                           json=payload,
                           headers=headers,
                           timeout=30)  # Add timeout

    # Check if we got a valid response
    if response.status_code != 200:
        raise Exception(f'API Error: {response.status_code} - {response.text}')

    response_data = response.json()

    # Extract the OCR text
    return response_data['choices'][0]['message']['content'].strip()

def get_vin_from_image_tesseract(image_path):
    """Extract VIN number from image using Tesseract OCR"""
    if not TESSERACT_AVAILABLE:
        raise Exception("Tesseract OCR is not available. Install with: pip install pytesseract")

    # Try with different configurations
    results = []

    # Original image
    img = Image.open(image_path)
    text1 = pytesseract.image_to_string(img, config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHJKLMNPRSTUVWXYZ')
    results.append(text1.strip())

    # Try with enhanced image
    enhanced_path = enhance_image(image_path)
    img_enhanced = Image.open(enhanced_path)

    # Try different PSM modes
    psm_modes = [3, 4, 6, 11, 12]
    for psm in psm_modes:
        config = f'--psm {psm} -c tessedit_char_whitelist=0123456789ABCDEFGHJKLMNPRSTUVWXYZ'
        text = pytesseract.image_to_string(img_enhanced, config=config)
        if text.strip():
            results.append(text.strip())

    # Return the longest result
    results = [r for r in results if r]
    if results:
        return max(results, key=len)

    return ""

def extract_vin_from_text(text):
    """Extract the VIN pattern from text"""
    # Remove spaces, newlines, etc.
    cleaned_text = ''.join(text.split())

    # Look for patterns that resemble VINs
    vin_pattern = re.compile(r'[A-HJ-NPR-Z0-9]{6,17}')
    matches = vin_pattern.findall(cleaned_text)

    if matches:
        # Sort by length, with longer matches first
        matches.sort(key=len, reverse=True)
        for match in matches:
            # If we found a full VIN (17 chars), return last 6
            if len(match) == 17:
                return match[-6:]
            # If we have at least 6 chars, return either the last 6 or all
            elif len(match) >= 6:
                return match[-6:] if len(match) > 6 else match

    # If no proper match, just return digits
    digits_only = ''.join(filter(str.isdigit, cleaned_text))
    if digits_only and len(digits_only) >= 6:
        return digits_only[-6:]

    return None

def process_images(api_key=None, use_tesseract=False, log_file=None, start_from=1, batch_size=None):
    """Process all images in the raw_images directory"""
    if not api_key and not use_tesseract:
        raise ValueError("Either API key or Tesseract must be enabled")

    if use_tesseract and not TESSERACT_AVAILABLE:
        print("Warning: Tesseract requested but not installed. Install with: pip install pytesseract")
        print("Also, make sure Tesseract OCR is installed on your system")
        if not api_key:
            return

    processed_count = 0
    renamed_count = 0

    # Create log file
    if log_file:
        log = open(log_file, 'a')  # Append mode
        log.write(f"\nVIN OCR Processing - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("-" * 60 + "\n\n")
    else:
        log = None

    def log_message(message):
        print(message)
        if log:
            log.write(f"{message}\n")

    # Get list of image files
    image_files = glob.glob(os.path.join(RAW_IMAGES_DIR, '*.jpg')) + \
                  glob.glob(os.path.join(RAW_IMAGES_DIR, '*.jpeg')) + \
                  glob.glob(os.path.join(RAW_IMAGES_DIR, '*.png'))

    # Sort files by name
    image_files.sort()

    total_files = len(image_files)

    # Apply start_from parameter
    if start_from > 1 and start_from <= total_files:
        image_files = image_files[start_from-1:]
        log_message(f"Starting from image #{start_from}")

    # Apply batch_size parameter
    if batch_size and batch_size > 0:
        image_files = image_files[:batch_size]
        log_message(f"Processing batch of {batch_size} images")

    total_to_process = len(image_files)
    log_message(f"Found {total_to_process} images to process")

    # Process all image files
    for idx, image_path in enumerate(image_files, 1):
        filename = os.path.basename(image_path)
        log_message(f"\n[{idx}/{total_to_process}] Processing: {filename}")

        try:
            vin_digits = None
            raw_text = None

            # Try Tesseract first if enabled (it's faster)
            if use_tesseract and TESSERACT_AVAILABLE:
                try:
                    log_message(f"Trying Tesseract OCR...")
                    tesseract_text = get_vin_from_image_tesseract(image_path)
                    log_message(f"Tesseract OCR result: \"{tesseract_text}\"")
                    raw_text = tesseract_text
                    vin_digits = extract_vin_from_text(tesseract_text)

                    if vin_digits:
                        log_message(f"Tesseract extracted VIN digits: {vin_digits}")
                except Exception as tesseract_error:
                    log_message(f"Tesseract Error: {str(tesseract_error)}")

            # Try API if tesseract failed or not enabled
            if (not vin_digits or vin_digits == "123456") and api_key:
                try:
                    log_message(f"Calling OpenRouter API...")
                    api_text = get_vin_from_image_api(image_path, api_key)
                    log_message(f"API OCR result: \"{api_text}\"")
                    raw_text = api_text
                    vin_digits = extract_vin_from_text(api_text)

                    if vin_digits:
                        log_message(f"API extracted VIN digits: {vin_digits}")
                except Exception as api_error:
                    log_message(f"API Error: {str(api_error)}")

            # Process the result if we have digits
            if vin_digits and vin_digits != "123456":
                # Create new file name
                file_ext = os.path.splitext(image_path)[1]
                new_filename = f'VIN_{vin_digits}{file_ext}'
                new_path = os.path.join(PROCESSED_IMAGES_DIR, new_filename)

                # Copy the file to processed directory with new name
                shutil.copy2(image_path, new_path)

                log_message(f"Saved as: {new_filename}")
                renamed_count += 1
            else:
                if vin_digits == "123456":
                    log_message("Skipping likely default response \"123456\"")
                else:
                    log_message("Could not extract valid VIN digits")

                # Allow user to input the correct VIN manually
                if not vin_digits or vin_digits == "123456":
                    log_message(f"Raw text extracted: {raw_text}")
                    log_message("Enter the last 6 digits of the VIN manually (or press Enter to skip):")
                    manual_vin = input()

                    if manual_vin and manual_vin.strip():
                        vin_digits = manual_vin.strip()
                        log_message(f"Using manually entered VIN: {vin_digits}")

                        # Create new file name
                        file_ext = os.path.splitext(image_path)[1]
                        new_filename = f'VIN_{vin_digits}{file_ext}'
                        new_path = os.path.join(PROCESSED_IMAGES_DIR, new_filename)

                        # Copy the file to processed directory with new name
                        shutil.copy2(image_path, new_path)

                        log_message(f"Saved as: {new_filename}")
                        renamed_count += 1

        except Exception as error:
            log_message(f"Error: {str(error)}")

        processed_count += 1

        # Add a delay if using API
        if api_key:
            log_message("Waiting before processing next file...")
            time.sleep(1)

    # Print summary
    summary = f"\nSUMMARY: Successfully processed {renamed_count} out of {processed_count} images"
    log_message(summary)

    if log:
        log.close()

def main():
    parser = argparse.ArgumentParser(description='VIN OCR Image Processor')
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--tesseract', action='store_true', help='Use Tesseract OCR')
    parser.add_argument('--log', default='vin_ocr_log.txt', help='Log file path')
    parser.add_argument('--start-from', type=int, default=1, help='Start processing from image #N')
    parser.add_argument('--batch', type=int, help='Process only this many images')

    args = parser.parse_args()

    if not args.api_key and not args.tesseract:
        parser.error("Either --api-key or --tesseract must be specified")

    print(f"VIN OCR Processor")
    print(f"Raw images directory: {RAW_IMAGES_DIR}")
    print(f"Processed images directory: {PROCESSED_IMAGES_DIR}")
    print(f"Enhanced images directory: {ENHANCED_IMAGES_DIR}")
    print(f"Log file: {args.log}")
    print(f"Using OpenRouter API: {'Yes' if args.api_key else 'No'}")
    print(f"Using Tesseract OCR: {'Yes' if args.tesseract else 'No'}")

    try:
        process_images(
            api_key=args.api_key,
            use_tesseract=args.tesseract,
            log_file=args.log,
            start_from=args.start_from,
            batch_size=args.batch
        )
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
