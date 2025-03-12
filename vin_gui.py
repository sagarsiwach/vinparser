#!/usr/bin/env python3
"""
VIN Manual Entry - Main application entry point
"""
import os
import sys
import argparse
import webbrowser
import threading
from flask import Flask, render_template
import tkinter as tk
from tkinter import filedialog

from vin_data import initialize_config
from flask_routes import setup_routes

# Configuration
APP_NAME = "VIN Manual Entry"
APP_VERSION = "1.0.0"
SERVER_HOST = "localhost"
SERVER_PORT = 8080

def start_browser(url):
    """Start the browser after a delay to ensure server is running"""
    def _open_browser():
        webbrowser.open(url)

    threading.Timer(1.0, _open_browser).start()

def select_directory(title):
    """Open a directory selection dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory(title=title)
    root.destroy()
    return directory if directory else None

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="VIN Manual Entry - Web GUI")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Server port (default: {SERVER_PORT})")
    parser.add_argument("--host", default=SERVER_HOST, help=f"Server host (default: {SERVER_HOST})")
    parser.add_argument("--prefix", default="VIN-B1024-", help="Prefix for renamed files")
    parser.add_argument("--raw-dir", default="", help="Directory containing raw images")
    parser.add_argument("--processed-dir", default="", help="Directory for processed images")
    parser.add_argument("--no-prompt", action="store_true", help="Don't prompt for directories")

    args = parser.parse_args()

    print(f"Starting {APP_NAME} v{APP_VERSION}")
    
    # Prompt for directories if not provided via command line
    raw_dir = args.raw_dir
    processed_dir = args.processed_dir
    
    if not args.no_prompt:
        # Prompt for raw images directory if not provided
        if not raw_dir:
            print("Please select the directory containing raw images:")
            selected_dir = select_directory("Select Raw Images Directory")
            if selected_dir:
                raw_dir = selected_dir
            else:
                raw_dir = "raw_images"  # Default if cancelled
                print(f"Using default raw images directory: {raw_dir}")
        
        # Prompt for processed images directory if not provided
        if not processed_dir:
            print("Please select the directory for processed images:")
            selected_dir = select_directory("Select Processed Images Directory")
            if selected_dir:
                processed_dir = selected_dir
            else:
                processed_dir = "processed_images"  # Default if cancelled
                print(f"Using default processed images directory: {processed_dir}")
    
    # Use defaults if still empty
    if not raw_dir:
        raw_dir = "raw_images"
    if not processed_dir:
        processed_dir = "processed_images"
    
    # Convert to absolute paths
    raw_dir = os.path.abspath(raw_dir)
    processed_dir = os.path.abspath(processed_dir)
    
    # Create directories if they don't exist
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    print(f"Raw images directory: {raw_dir}")
    print(f"Processed images directory: {processed_dir}")
    
    # Initialize config
    initialize_config(raw_dir, processed_dir, args.prefix)
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), "templates"),
                static_folder=os.path.join(os.path.dirname(__file__), "static"))

    # Setup routes
    setup_routes(app)

    # Start browser
    start_browser(f"http://{args.host}:{args.port}")

    try:
        # Start Flask server
        app.run(host=args.host, port=args.port, debug=False)
    finally:
        print("Shutting down...")

if __name__ == "__main__":
    main()