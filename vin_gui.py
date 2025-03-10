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

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="VIN Manual Entry - Web GUI")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Server port (default: {SERVER_PORT})")
    parser.add_argument("--host", default=SERVER_HOST, help=f"Server host (default: {SERVER_HOST})")
    parser.add_argument("--prefix", default="VIN-B1024-", help="Prefix for renamed files")
    parser.add_argument("--raw-dir", default="raw_images", help="Directory containing raw images")
    parser.add_argument("--processed-dir", default="processed_images", help="Directory for processed images")

    args = parser.parse_args()

    print(f"Starting {APP_NAME} v{APP_VERSION}")
    
    # Create directories if they don't exist
    raw_dir = os.path.abspath(args.raw_dir)
    processed_dir = os.path.abspath(args.processed_dir)
    
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