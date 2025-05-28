import os
import time
import logging
import shutil
import json
from pathlib import Path
from datetime import datetime
import send2trash
from concurrent.futures import ThreadPoolExecutor

# Define the path to the configuration file for easier changes in future
CONFIGURA_PATH = Path("F:/Full_Stack/Python/Python-file-automation/configuration.json")

# Checks if the configuration file exists
if not CONFIGURA_PATH.exists():
    raise FileNotFoundError(f"Configuration file not found: {CONFIGURA_PATH}")

# Load the configuration file
try:
    with open(CONFIGURA_PATH, "r") as config_file:
        config = json.load(config_file)
except json.JSONDecodeError as e:
    raise ValueError(f"Error decoding JSON in {CONFIGURA_PATH}: {e}")

# Extract paths from config
Main_Folder = Path(config.get("Main_folder", ""))
LOG_FILE = config.get("log_file", "")
extension_file = Path(config.get("file_extensions", ""))

# Logging Setup
logging.basicConfig(
    filename=LOG_FILE, 
    level=logging.INFO,
    # Logs the current date, time, message no.
    format="\n%(asctime)s - %(levelname)s - %(message)s",
)

# Ensure the extension file exists
if not extension_file.exists():
    raise FileNotFoundError(f"Extension file not found: {extension_file}")

# Load the extension mappings
try:
    with open(extension_file, "r") as ext_file:
        extension_map = json.load(ext_file)
except json.JSONDecodeError as e:
    raise ValueError(f"Error decoding JSON in {extension_file}: {e}")


# Function to Create Sub-directory
def create_subdir(directory):
    # sub-directory path
    dest_folder = Main_Folder / directory
    # if the dest_folder not exist in main folder
    if dest_folder not in Main_Folder.iterdir():
        try:
            # creates the dest_folder
            dest_folder.mkdir(exist_ok=True)
            logging.info(f"Ensured sub-directory exists: {dest_folder}")
        except Exception as e:
            logging.error(f"Error creating directory {dest_folder}: {e}")
    else:
        # if the dest_folder already exist
        pass

# Function to Handle Duplicate Files
def unique_filename(dest_folder, file_name):
    # separates file name & extension
    base, ext = os.path.splitext(file_name)
    counter = 1
    new_filename = file_name

    # checks whether the complete file path exists
    while (dest_folder / new_filename).exists():
        # if exists, duplicate file with "()" is created based on counter value
        new_filename = f"{base}({counter}){ext}"
        counter += 1
    return dest_folder / new_filename

# Function to Move Files
def move_file(file):
    try:
        if file.is_file():
            # extension of the file is assigned to extension with lowercase
            extension = file.suffix.lower()

            # if the extension is not found in extension_map dictionary, log a warning
            if not extension_map.get(extension):
                logging.warning(f"Skipping {file.name} - Unrecognized extension")
                return
            else:
                # value of extension in dictionary is assigned to category
                category = extension_map.get(extension)

                # Create destination folder
                create_subdir(category)
                # complete path without file name
                dest_folder = Main_Folder / category

                # Handle duplicate files
                dest_file = unique_filename(dest_folder, file.name)

                # Move the file
                shutil.move(str(file), str(dest_file))
                logging.info(f"Moved: {file.name} → {dest_file}")
        
        else:
            logging.warning(f"Skipping {file.name} - Not a file but a folder")
    
    except PermissionError:
        logging.error(f"Permission denied: {file}. Retrying in 5 seconds.")
        time.sleep(5)
        move_file(file)

    except Exception as e:
        logging.error(f"Error moving {file.name}: {e}")
        #send2trash.send2trash(str(file_path))  # Send problematic files to trash

# Main Function to Scan and Sort Files
def main():
    logging.info("Starting file sorting process...")

    # used for multi-tasking & faster execution
    with ThreadPoolExecutor() as executor:
        for item in Main_Folder.iterdir():
            # checks if the item is file or not
            if item.is_file():
                # executes the move_file(file_path=item) function
                executor.submit(move_file, item)

    logging.info("File sorting completed.")

# Run the Script
if __name__ == "__main__":
    main()


