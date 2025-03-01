# BG3 Dialogue Finder - File Copier

## Overview

This application allows you to search for Baldur's Gate 3 dialogue files using NoComply's BG3 Dialogue Finder database and copy the matching .wem files from a source directory to a destination directory for modding purposes.

## Features

- Search for dialogue files by dialogue text, character name, file type, or filename
- Combine up to three search criteria for more specific results
- View detailed search results in a table format
- Copy found .wem files from a source directory to a destination directory
- Real-time progress tracking during file operations
- Visual indicators for copied and missing files
- Sort results by clicking on any column header
- Select and copy individual cells, rows, or multiple rows
- View detailed information by double-clicking on a row
- User-friendly interface with status updates

## Installation

1. Download the latest release from the [Releases](https://github.com/yourusername/BG3DialogueFinder/releases) page
2. Extract the ZIP file to a location of your choice
3. Run `BG3DialogueFinder.exe`

## Usage

1. Enter your search criteria in one or more of the search fields
2. Select the appropriate search type for each field (dialogue, character, type, or filename)
3. Click "Search" to find matching files
4. Browse and select your source folder (where the original .wem files are located)
5. Browse and select your destination folder (where you want to copy the files)
6. Click "Copy Files" to copy the found files from source to destination

### File Status Indicators

After copying files, each file in the results will be marked with a status:

- **Copied** (green background): The file was found and successfully copied
- **Not Found** (red background): The file was not found in the source directory

### Sorting Results

- Click on any column header to sort the results by that column
- Click again to reverse the sort order
- The current sort column and direction are indicated by an arrow (↑ or ↓)

### Selecting and Copying Data

- **Copy Selected** button: Copies the currently selected row to the clipboard
- **Right-click menu**: Provides options to copy individual cells, the current row, or all selected rows
- **Double-click** on a row to view detailed information in a popup window
- **Multiple selection**: Hold Ctrl or Shift while clicking to select multiple rows

### Search Tips

- You can use multiple search boxes to execute more complex queries
- Searches work as 'AND' functions, not 'OR' functions
- For example, searching for 'Astarion' in Characters and 'tadpole' in Dialogue will return all instances of Astarion saying tadpole
- Leave a search field empty if you don't want to use that criterion

### File Types

The 'Type' field refers to the type of dialogue:

- Localization (Subtitled)
- Localization - Not In English.loca
- Various action types (Action_Attack, Action_BuffTarget, etc.)

## Building from Source

If you want to build the executable yourself:

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Build the executable:
   ```
   pyinstaller --onefile --windowed --icon=icon.ico bg3_dialogue_finder.py
   ```
4. The executable will be created in the `dist` directory

## Running Without Building

If you prefer to run the application without building an executable:

1. Make sure you have Python 3.8 or higher installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python bg3_dialogue_finder.py
   ```
   Or simply double-click the `run_app.bat` file

## Credits

- This application uses the [NoComply BG3 Dialogue Finder](https://nocomplydev.pythonanywhere.com/) API
- Original database and web application created by NoComply

## License

This project is licensed under the MIT License - see the LICENSE file for details.
