#!/usr/bin/env python3
"""
VIN Manual Entry - Main application entry point
"""
import os
import sys
import argparse
import webbrowser
import threading
import tkinter as tk
from tkinter import filedialog
from flask import Flask

from image_processor import setup_image_cache, cleanup_image_cache
from vin_data import initialize_config
from flask_routes import setup_routes

# Configuration
APP_NAME = "VIN Manual Entry"
APP_VERSION = "1.0.0"
SERVER_HOST = "localhost"
SERVER_PORT = 8080

def select_directories():
    """Open dialogs to select directories and CSV file"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Select raw images directory
    print("Please select the directory containing raw vehicle images...")
    raw_dir = filedialog.askdirectory(title="Select Raw Images Directory")
    if not raw_dir:
        print("No directory selected. Exiting.")
        return False

    # Select processed images directory
    print("Please select the directory where processed images will be saved...")
    processed_dir = filedialog.askdirectory(title="Select Processed Images Directory")
    if not processed_dir:
        print("No directory selected. Exiting.")
        return False

    # Update config
    initialize_config(raw_dir, processed_dir)

    print(f"Raw images directory: {raw_dir}")
    print(f"Processed images directory: {processed_dir}")

    return True

def start_browser(url):
    """Start the browser after a delay to ensure server is running"""
    def _open_browser():
        webbrowser.open(url)

    threading.Timer(1.0, _open_browser).start()

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="VIN Manual Entry - Web GUI")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Server port (default: {SERVER_PORT})")
    parser.add_argument("--host", default=SERVER_HOST, help=f"Server host (default: {SERVER_HOST})")
    parser.add_argument("--prefix", default="VIN-B1024-", help="Prefix for renamed files")
    parser.add_argument("--raw-dir", help="Directory containing raw images (skip dialog)")
    parser.add_argument("--processed-dir", help="Directory for processed images (skip dialog)")

    args = parser.parse_args()

    # Initialize config with CLI prefix
    initialize_config(None, None, args.prefix)

    if args.raw_dir and args.processed_dir:
        # Use command line arguments
        initialize_config(args.raw_dir, args.processed_dir)
        print(f"Raw images directory: {args.raw_dir}")
        print(f"Processed images directory: {args.processed_dir}")
    else:
        # Open file/directory selection dialogs
        if not select_directories():
            print("Directory selection cancelled. Exiting.")
            return

    print(f"Starting {APP_NAME} v{APP_VERSION}")

    # Setup and cleanup image cache
    setup_image_cache()

    # Create Flask app
    app = Flask(__name__, static_folder=None)

    # Setup routes
    setup_routes(app)

    # Start browser
    start_browser(f"http://{args.host}:{args.port}")

    try:
        # Start Flask server
        app.run(host=args.host, port=args.port, debug=False)
    finally:
        # Clean up any temporary files
        cleanup_image_cache()

if __name__ == "__main__":
    main()
