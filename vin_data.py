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

# Google Sheets CSV URL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdaaAAREF9TFbxxwEKkUa6QOIdeOghd_scKCMXqVzHnAVlnH7v7zkTAPN72LpCwlpTmRE-QpilAXb8/pub?gid=1256257560&single=true&output=csv"

# Embedded VIN data (default data if CSV download fails)
EMBEDDED_VIN_DATA = """MD9B10XF5CA583412,MD9B10XF5CA583430,MD9B10XF6CA583431,MD9B10XF8CA583432,MD9B10XF2CA583434,MD9B10XF3CA583453"""

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
        try:
            response = requests.get(CSV_URL, timeout=5)
            if response.status_code == 200:
                csv_data = response.text
            else:
                # Fall back to embedded data
                csv_data = EMBEDDED_VIN_DATA
        except:
            # Fall back to embedded data
            csv_data = EMBEDDED_VIN_DATA
        
        # Parse the CSV content
        for line in csv_data.splitlines():
            vins = line.split(',')
            for vin in vins:
                if re.search(r'[A-Z0-9]{17}', vin, re.IGNORECASE):
                    # Extract last 6 characters
                    result['vins'].append(vin[-6:].upper())
                elif len(vin.strip()) == 6 and vin.strip().isalnum():
                    # It's already just the 6 characters we need
                    result['vins'].append(vin.strip().upper())

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
    # Try matching our VIN format first
    match = re.search(r'VIN[_-]([A-Z0-9]{6})', filename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
        
    # Check for DONE_ prefix with VIN
    match = re.search(r'DONE_([A-Z0-9]{6})_', filename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # Try to find any 6-digit alphanumeric sequence
    match = re.search(r'[A-Z0-9]{6}', filename.upper())
    return match.group(0) if match else None