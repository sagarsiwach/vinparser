#!/usr/bin/env python3
"""
VIN OCR Processor - A terminal-based tool to extract VIN numbers from vehicle part images
using the vision capabilities of Granite vision model via Ollama.
"""
import os
import sys
import json
import base64
import tempfile
import glob
import shutil
import time
import argparse
from pathlib import Path
from datetime import datetime
import requests
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from pyfiglet import Figlet
from colorama import init, Fore, Style
from loguru import logger
from PIL import Image

# Configuration
OLLAMA_URL = "https://ollama.congzhoumachinery.com"
OLLAMA_MODEL = "granite3.2-vision:latest"  # Matches your model registry
APP_NAME = "VIN OCR Processor"
APP_VERSION = "1.0.0"
APP_COLOR = "blue"

# Default directories
RAW_IMAGES_DIR = "raw_images"
PROCESSED_IMAGES_DIR = "processed_images"

# Initialize components
init()
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>", level="DEBUG")
console = Console()

def setup_file_logger(log_file):
    """Setup file handler for logging if log_file is provided."""
    logger.add(log_file, rotation="10 MB", level="INFO")
    logger.info(f"Logging to file: {log_file}")

def display_banner():
    """Display the application banner."""
    f = Figlet(font='slant')
    banner = f.renderText(APP_NAME)
    console.print(f"[{APP_COLOR}]{banner}[/{APP_COLOR}]")
    console.print(f"[{APP_COLOR}]Version: {APP_VERSION}[/{APP_COLOR}]")
    console.print(f"[{APP_COLOR}]{'=' * 60}[/{APP_COLOR}]")

def encode_image_to_base64(image_path):
    """Convert an image to base64 encoding."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error converting file to base64: {e}")
        console.print(f"[red]Error converting file to base64: {e}[/red]")
        return None

def check_directories():
    """Ensure required directories exist."""
    try:
        os.makedirs(RAW_IMAGES_DIR, exist_ok=True)
        os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)
        logger.info(f"Raw images directory: {RAW_IMAGES_DIR}")
        logger.info(f"Processed images directory: {PROCESSED_IMAGES_DIR}")
        return True
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        console.print(f"[red]Error creating directories: {e}[/red]")
        return False

def navigate_directories():
    """Navigate directories to select a directory for processing."""
    current_dir = os.getcwd()
    chosen_dir = None
    while chosen_dir is None:
        try:
            dir_items = sorted([d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))])
            choices = [("📁 .. (Go up one directory)", "..")] + \
                      [(f"📁 {d}/ (Select this directory)", d) for d in dir_items]

            questions = [
                inquirer.List('choice',
                              message=f"Current directory: {current_dir}",
                              choices=choices,
                              carousel=True),
            ]
            answers = inquirer.prompt(questions)
            if not answers:
                console.print("[red]Selection cancelled. Exiting...[/red]")
                sys.exit(1)

            choice = answers['choice']
            if choice == "..":
                current_dir = os.path.dirname(current_dir)
            else:
                confirm_questions = [
                    inquirer.Confirm('confirm', message=f"Use '{choice}' as raw images directory?", default=True),
                ]
                confirm_answers = inquirer.prompt(confirm_questions)
                if confirm_answers and confirm_answers['confirm']:
                    chosen_dir = os.path.join(current_dir, choice)
                else:
                    current_dir = os.path.join(current_dir, choice)
        except Exception as e:
            logger.error(f"Directory navigation error: {e}")
            console.print(f"[red]Directory navigation error: {e}[/red]")
            current_dir = os.path.expanduser("~")  # Reset to home directory on error

    return chosen_dir

def get_vin_from_image(image_path):
    """Extract the last 6 characters of the VIN from the vehicle part image using Granite vision model."""
    if not os.path.isfile(image_path):
        logger.error(f"Image file not found: {image_path}")
        return None

    # Check file size in MB
    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    logger.info(f"Image size: {file_size_mb:.2f} MB")

    # If image is large, resize it
    working_image_path = image_path
    resized = False

    if file_size_mb > 3:
        logger.info("Image is large; resizing...")
        try:
            with Image.open(image_path) as img:
                img.thumbnail((1200, 1200))
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                    img.save(tmp_path, "JPEG", quality=85)
                    logger.info(f"Resized image saved as temporary file: {tmp_path}")
            resized = True
            working_image_path = tmp_path
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            # Continue with original image if resize fails

    # Get base64 image
    image_base64 = encode_image_to_base64(working_image_path)
    if not image_base64:
        if resized and os.path.exists(working_image_path):
            os.remove(working_image_path)
        return None

    # Create API request with refined prompt
    prompt = (
        "This image shows a vehicle part with a stamped VIN (Vehicle Identification Number). "
        "The full VIN is visible and follows a format like 'MD9310XA6EA583696'. "
        "Extract ONLY the last 6 characters of this VIN and provide them without any other text. "
        "For example, if the VIN is MD9310XA6EA583696, you should return ONLY: 583696"
    )

    try:
        # Prepare API request based on Ollama's multimodal API format
        api_request = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }

        logger.debug(f"Sending request to: {OLLAMA_URL}/api/generate")
        logger.debug(f"Using model: {OLLAMA_MODEL}")

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=api_request,
            timeout=120
        )

        if response.status_code != 200:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            if resized and os.path.exists(working_image_path):
                os.remove(working_image_path)
            return None

        # Process response
        response_json = response.json()
        logger.debug(f"Response received with keys: {list(response_json.keys())}")

        llm_response = response_json.get('response', '')
        logger.debug(f"Raw response: {llm_response}")

        # Clean up temporary file if used
        if resized and os.path.exists(working_image_path):
            os.remove(working_image_path)
            logger.info("Temporary resized image removed.")

        # Extract VIN from response - improved regex pattern
        # First, check if response contains exactly 6 alphanumeric characters
        import re

        # Clean the response (remove spaces, newlines, etc.)
        cleaned_response = llm_response.strip()

        # If the cleaned response is exactly 6 alphanumeric characters, use it directly
        if re.match(r'^[A-Z0-9]{6}$', cleaned_response, re.IGNORECASE):
            vin_last_6 = cleaned_response
            logger.info(f"Extracted VIN (exact match): {vin_last_6}")
            return vin_last_6

        # Otherwise, try to find a 6-character alphanumeric sequence that looks like a VIN
        # Look specifically for patterns commonly seen in VINs (with numbers and letters mixed)
        vin_patterns = [
            r'([A-Z0-9]{6})\b',  # Basic 6-char pattern with word boundary
            r'(\d{6})',          # 6 digits
            r'(\d{3}[A-Z0-9]{3})',  # 3 digits followed by 3 alphanumerics
            r'([A-Z0-9]{3}\d{3})'   # 3 alphanumerics followed by 3 digits
        ]

        for pattern in vin_patterns:
            matches = re.findall(pattern, llm_response, re.IGNORECASE)
            if matches:
                # Take the last match as it's more likely to be what we want
                # (avoiding matches on example text in the response)
                vin_last_6 = matches[-1]
                logger.info(f"Extracted VIN using pattern {pattern}: {vin_last_6}")
                return vin_last_6

        # If we get here, no matches were found
        logger.warning("No valid VIN found in response")
        return None

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        if resized and os.path.exists(working_image_path):
            os.remove(working_image_path)
        return None

def process_images(raw_dir, processed_dir, start_from=1, batch_size=None):
    """Process images in raw_dir for VIN OCR and save processed images with renamed VIN."""
    image_files = sorted(
        glob.glob(os.path.join(raw_dir, '*.jpg')) +
        glob.glob(os.path.join(raw_dir, '*.jpeg')) +
        glob.glob(os.path.join(raw_dir, '*.png'))
    )
    total_files = len(image_files)

    if total_files == 0:
        console.print(f"[yellow]No image files found in {raw_dir}[/yellow]")
        return False

    if start_from > 1 and start_from <= total_files:
        logger.info(f"Starting from image #{start_from}")
        image_files = image_files[start_from-1:]

    if batch_size and batch_size > 0:
        logger.info(f"Processing batch of {batch_size} images")
        image_files = image_files[:batch_size]

    total_to_process = len(image_files)
    logger.info(f"Found {total_to_process} images to process.")

    processed_count = 0
    renamed_count = 0
    skipped_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        overall_task = progress.add_task(f"[green]Processing images...", total=total_to_process)

        for idx, image_path in enumerate(image_files, 1):
            filename = os.path.basename(image_path)
            progress.update(overall_task, description=f"[cyan]Processing image {idx}/{total_to_process}: {filename}")

            try:
                vin_last_6 = get_vin_from_image(image_path)

                if vin_last_6:
                    file_ext = os.path.splitext(image_path)[1]
                    new_filename = f"VIN_{vin_last_6}{file_ext}"
                    new_path = os.path.join(processed_dir, new_filename)
                    shutil.copy2(image_path, new_path)
                    logger.info(f"Image saved as: {new_filename}")
                    renamed_count += 1
                else:
                    progress.stop()
                    console.print(f"[yellow]Could not extract VIN from {filename}[/yellow]")
                    manual_vin = input("Enter the last 6 digits of the VIN manually (or press Enter to skip): ").strip()
                    progress.start()

                    if manual_vin:
                        file_ext = os.path.splitext(image_path)[1]
                        new_filename = f"VIN_{manual_vin}{file_ext}"
                        new_path = os.path.join(processed_dir, new_filename)
                        shutil.copy2(image_path, new_path)
                        logger.info(f"Image saved as: {new_filename} (manual entry)")
                        renamed_count += 1
                    else:
                        skipped_count += 1
            except Exception as error:
                logger.error(f"Error processing {filename}: {str(error)}")
                skipped_count += 1

            processed_count += 1
            progress.update(overall_task, advance=1)

            # Add a small delay between requests
            time.sleep(1)

    console.print(f"[green]Summary: Processed {processed_count} images[/green]")
    console.print(f"[green]- Successfully renamed: {renamed_count}[/green]")
    console.print(f"[yellow]- Skipped: {skipped_count}[/yellow]")

    return True

def check_api_connectivity():
    """Check if Ollama API is available."""
    try:
        version_response = requests.get(f"{OLLAMA_URL}/api/version", timeout=5)
        version_info = version_response.json()
        console.print(f"[green]✓ Connected to Ollama API at {OLLAMA_URL}[/green]")
        console.print(f"[green]✓ Ollama version: {version_info.get('version', 'unknown')}[/green]")

        # Check if the model is available
        models_response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = models_response.json().get('models', [])
        model_names = [m.get('name') for m in models]

        if OLLAMA_MODEL.split(':')[0] in model_names or OLLAMA_MODEL in model_names:
            console.print(f"[green]✓ Model {OLLAMA_MODEL} is available[/green]")
            return True
        else:
            console.print(f"[yellow]⚠ Model {OLLAMA_MODEL} not found in available models. Available models: {', '.join(model_names)}[/yellow]")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"API connection failed: {e}")
        console.print(f"[red]✗ Could not connect to Ollama API: {e}[/red]")
        console.print(f"[yellow]Please ensure Ollama is running and accessible at {OLLAMA_URL}[/yellow]")
        return False

def main():
    """Main application entry point."""
    try:
        display_banner()
        console.print("[yellow]Extracting VIN numbers from vehicle part images using Granite Vision[/yellow]")
        console.print()

        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="VIN OCR Image Processor")
        parser.add_argument("--raw-dir", help="Directory containing raw images")
        parser.add_argument("--processed-dir", help="Directory for processed images")
        parser.add_argument("--log", default="vin_ocr_log.txt", help="Log file path")
        parser.add_argument("--start-from", type=int, default=1, help="Start processing from image #N")
        parser.add_argument("--batch", type=int, help="Process only this many images")

        args = parser.parse_args()

        # Setup logging
        setup_file_logger(args.log)
        logger.info("VIN OCR Processor started")

        # Use command line args or defaults
        global RAW_IMAGES_DIR, PROCESSED_IMAGES_DIR
        RAW_IMAGES_DIR = args.raw_dir if args.raw_dir else RAW_IMAGES_DIR
        PROCESSED_IMAGES_DIR = args.processed_dir if args.processed_dir else PROCESSED_IMAGES_DIR

        if not check_directories():
            console.print("[red]Failed to create required directories[/red]")
            return

        # Check API connectivity
        if not check_api_connectivity():
            console.print("[red]API connectivity issues detected[/red]")
            return

        # If raw_dir wasn't specified, ask user to select a directory
        if not args.raw_dir:
            console.print()
            console.print("[bold]Navigate and select a directory containing vehicle part images[/bold]")
            RAW_IMAGES_DIR = navigate_directories()
            console.print(f"[green]Selected directory: {RAW_IMAGES_DIR}[/green]")

        # Process images
        success = process_images(
            raw_dir=RAW_IMAGES_DIR,
            processed_dir=PROCESSED_IMAGES_DIR,
            start_from=args.start_from,
            batch_size=args.batch
        )

        if success:
            console.print()
            console.print("[green]Processing complete! Check the processed_images directory for results.[/green]")
        else:
            console.print()
            console.print("[yellow]Processing completed with issues. Check the log for details.[/yellow]")

        console.print()
        console.print("[green]Thank you for using VIN OCR Processor![/green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}")
        console.print(f"[red]Application error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)
