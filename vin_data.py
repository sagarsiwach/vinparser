"""
VIN data handling module for VIN GUI application
"""
import os
import re
import csv
import requests
from io import StringIO

# Configuration
config = {
    "raw_dir": "",
    "processed_dir": "",
    "prefix": "VIN-B1024-"
}

# Embedded VIN data (default data if CSV download fails)
EMBEDDED_VIN_DATA = """MD9B10XF5CA583412
MD9B10XF5CA583430
MD9B10XF6CA583431
MD9B10XF8CA583432
MD9B10XF2CA583434
"""

# Google Sheets CSV URL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdaaAAREF9TFbxxwEKkUa6QOIdeOghd_scKCMXqVzHnAVlnH7v7zkTAPN72LpCwlpTmRE-QpilAXb8/pub?gid=1256257560&single=true&output=csv"

def initialize_config(raw_dir=None, processed_dir=None, prefix=None):
    """Initialize or update configuration"""
    global config
    if raw_dir:
        config["raw_dir"] = raw_dir
    if processed_dir:
        config["processed_dir"] = processed_dir
    if prefix:
        config["prefix"] = prefix
    return config

def get_config():
    """Get current configuration"""
    return config

def load_csv_data():
    """Load VIN data from CSV file or embedded data"""
    result = {
        'vins': [],
        'matched': [],
        'pending': []
    }

    try:
        # Try to download the CSV first
        csv_content = StringIO()
        try:
            response = requests.get(CSV_URL, timeout=5)
            if response.status_code == 200:
                csv_content = StringIO(response.text)
            else:
                # Fall back to embedded data
                csv_content = StringIO(EMBEDDED_VIN_DATA)
        except:
            # Fall back to embedded data
            csv_content = StringIO(EMBEDDED_VIN_DATA)

        # Parse the CSV content
        reader = csv.reader(csv_content)
        for row in reader:
            if not row:
                continue

            # Try to find a VIN in the row
            vin = None
            for cell in row:
                # Look for a 17-character VIN
                if re.search(r'[A-Z0-9]{17}', cell, re.IGNORECASE):
                    vin = re.search(r'[A-Z0-9]{17}', cell, re.IGNORECASE).group(0)
                    break
                # Look for anything that might be part of a VIN
                elif re.search(r'[A-Z0-9]{6,}', cell, re.IGNORECASE):
                    vin = re.search(r'[A-Z0-9]{6,}', cell, re.IGNORECASE).group(0)
                    if len(vin) >= 6:
                        break

            if vin:
                # Extract last 6 characters
                result['vins'].append(vin[-6:].upper())

        # Check which VINs are already processed
        if os.path.exists(config['processed_dir']):
            processed_files = os.listdir(config['processed_dir'])
            for vin in result['vins']:
                # Check if any processed file contains this VIN
                if any(vin in f for f in processed_files):
                    result['matched'].append(vin)
                else:
                    result['pending'].append(vin)
    except Exception as e:
        print(f"Error loading CSV: {e}")

    return result

def extract_vin_from_filename(filename):
    """Try to extract VIN from filename"""
    match = filename.upper().split('_')[-1] if '_' in filename else None
    if match and re.match(r'^[A-Z0-9]{6}', match):
        return match[:6]

    # Try to find any 6-digit alphanumeric sequence
    match = re.search(r'[A-Z0-9]{6}', filename.upper())
    return match.group(0) if match else None
