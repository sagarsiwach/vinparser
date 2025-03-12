VIN Manual Entry Application
A web-based application for manually entering and processing Vehicle Identification Numbers (VINs) from vehicle part images. This tool helps streamline the process of matching images to VIN numbers for inventory and affidavit purposes.
Features

Web interface for viewing and processing vehicle part images
Support for viewing images in original or high-contrast modes to better see embossed VINs
Automatic tracking of matched and pending VINs
Duplicate VIN detection and resolution
Progress tracking and reporting
Keyboard shortcuts for efficient workflow
Integration with CSV data source for VIN validation

Architecture
The application consists of:

Flask Backend: Handles image serving, processing, and file operations
Web Frontend: Responsive UI built with TailwindCSS
Data Management: CSV-based VIN tracking system
OCR Support: Optional integration with vision model for automatic VIN detection

Components
Backend

vin_gui.py: Main application entry point, initializes the Flask server
flask_routes.py: API endpoints for image processing and VIN operations
vin_data.py: Handles loading and processing VIN data from CSV
image_processor.py: Image manipulation functions (contrast enhancement, inversion)

Frontend

templates/index.html: Main application UI
templates/base.html: Base HTML template with common styling
static/js/main.js: Core UI functionality
static/js/modal.js: Handles duplicate VIN resolution

OCR Support

vin_ocr.py: Standalone script for batch OCR processing of images using Granite vision model

Installation

Install required dependencies:

bashCopypip install -r requirements.txt

Run the application:

bashCopypython vin_gui.py

Optional command-line arguments:

Copy--port PORT         Server port (default: 8080)
--host HOST         Server host (default: localhost)
--prefix PREFIX     Prefix for renamed files (default: VIN-B1024-)
--raw-dir DIR       Directory containing raw images (default: raw_images)
--processed-dir DIR Directory for processed images (default: processed_images)
Usage Instructions

Setup:

Place your vehicle part images in the raw_images directory
The application will automatically create processed_images directory if it doesn't exist


Processing Images:

Launch the application and open the web interface
Navigate through images using arrow keys or clicking images in the sidebar
Use view modes (1-2 keys) to better see embossed VINs
Enter the last 6 characters of the VIN and press Enter to save and move to next image
Use the Skip button to move to the next image without processing
Use the Delete button to remove low-quality or irrelevant images


Handling Duplicates:

If a VIN is already in the processed directory, you'll be prompted to choose between existing and new images
Use 1 or 2 keys to quickly select which image to keep


OCR Support (Optional):

For batch processing, use the separate OCR tool:

Copypython vin_ocr.py


Keyboard Shortcuts

Enter: Save VIN and go to next image
←: Previous image
→: Next image
1: Original view
2: High contrast inverted view
Delete: Delete current image

Data Integration
The application fetches VIN data from a Google Sheets document published as CSV. If the network connection fails, it falls back to embedded data.
Development Notes

The application uses a caching system for processed images to improve performance
All file operations are handled asynchronously to prevent UI freezing
The Flask server includes proper error handling and resource cleanup

System Requirements

Python 3.6+
Modern web browser
Internet connection (optional, for fetching latest VIN data)