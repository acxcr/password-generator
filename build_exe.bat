@echo off
REM Windows Package Script - Password Generator

REM Switch to the directory where this script is located
cd /d "%~dp0"

echo ========================================
echo Random Password Generator - Build Script
echo ========================================
echo.
echo Working directory: %CD%
echo.

REM Check if source file exists
if not exist "password_generator.py" (
    echo ERROR: password_generator.py not found in current directory!
    echo Please make sure this .bat file is in the same folder as password_generator.py
    pause
    exit /b 1
)

REM Check Python installation
echo [1/4] Checking dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not detected. Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/4] Installing dependencies...
pip install PyQt6 Pillow pyinstaller

echo.
echo [3/4] Packaging application...
pyinstaller --onefile --windowed --name "PasswordGenerator" --icon=password_key_icon.ico password_generator.py

echo.
echo [4/4] Cleaning temporary files...
if exist "build" rmdir /s /q build
if exist "__pycache__" rmdir /s /q __pycache__
if exist "PasswordGenerator.spec" del /q PasswordGenerator.spec

echo.
echo ========================================
if exist "dist\PasswordGenerator.exe" (
    echo Build Complete!
    echo.
    echo Executable location: %CD%\dist\PasswordGenerator.exe
    echo.
    echo NEXT STEPS:
    echo 1. Right-click PasswordGenerator.exe and rename to your preferred Chinese name
    echo 2. If icon appears blurry, use ResourceHacker or similar tool to replace icon
) else (
    echo Build FAILED - .exe not found. Check errors above.
)
echo ========================================
echo.
pause
