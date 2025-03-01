# BG3 Dialogue Finder - Installation Guide

## Pre-built Executable (Recommended)

1. Download the latest release from the [Releases](https://github.com/yourusername/BG3DialogueFinder/releases) page
2. Extract the ZIP file to a location of your choice
3. Run `BG3DialogueFinder.exe`

## Building from Source

If you prefer to build the executable yourself, follow these steps:

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. Clone or download this repository
2. Open a command prompt in the repository directory
3. Run the `build_exe.bat` script by double-clicking it or running it from the command prompt

   OR

   Manually build the executable with these commands:

   ```
   pip install -r requirements.txt
   pyinstaller --onefile --windowed --icon=icon.ico bg3_dialogue_finder.py
   ```

4. Once the build is complete, the executable will be located in the `dist` folder
5. Run `dist/BG3DialogueFinder.exe`

## Troubleshooting

### Missing Icon

If you're building from source and don't have an icon file:

1. Either create or download an icon file named `icon.ico`
2. Place it in the same directory as the Python script
3. Or remove the `--icon=icon.ico` parameter from the PyInstaller command

### API Connection Issues

If you're having trouble connecting to the API:

1. Make sure you have an active internet connection
2. Run the `test_api.py` script to verify the API connection
3. If the test fails, the NoComply BG3 Dialogue Finder website might be down or experiencing issues

### File Copying Issues

If files aren't being copied correctly:

1. Make sure the source folder contains the .wem files you're looking for
2. Ensure you have write permissions for the destination folder
3. Check that the filenames in the search results match the actual filenames in your source folder

## Support

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/yourusername/BG3DialogueFinder/issues).
