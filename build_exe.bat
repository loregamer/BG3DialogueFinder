@echo off
echo Building BG3 Dialogue Finder executable...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed or not in PATH. Please install pip.
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

echo.
echo Building executable...
pyinstaller --onefile --windowed --icon=icon.ico bg3_dialogue_finder.py

echo.
if %errorlevel% equ 0 (
    echo Build successful! The executable is located in the 'dist' folder.
) else (
    echo Build failed. Please check the error messages above.
)

pause 