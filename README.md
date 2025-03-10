# VIN OCR Image Processor

This tool processes vehicle images to extract and identify VIN numbers using OCR.

## Setup

1. Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
2. Install dependencies:
```pip install requests Pillow```
Copy
## Usage
1. Place your vehicle images in the `raw_images` folder
2. Run the script with your OpenRouter API key:
python vin_ocr.py --api-key "your-api-key-here"
3. Processed images will be saved in the `processed_images` folder with names
based on the detected VIN numbers (last 6 digits)
4. Check the log file for processing details
