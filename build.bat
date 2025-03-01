@echo off
REM Clean up previous build artifacts
rmdir /S /Q build
rmdir /S /Q dist
del /Q *.spec

echo Building the executable...
pyinstaller --onefile --windowed bg3_dialogue_finder.py

echo Build complete! Press any key to exit.
pause
