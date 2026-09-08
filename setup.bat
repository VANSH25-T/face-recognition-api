@echo off
REM Face Recognition API - Setup Script for Windows

echo.
echo ==========================================
echo Face Recognition API Setup (Windows)
echo ==========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
echo Virtual environment created

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo.
echo Creating directories...
if not exist known_faces mkdir known_faces
if not exist uploaded_images mkdir uploaded_images
echo Directories created

REM Copy .env file
if not exist .env (
    echo.
    echo Copying .env.example to .env...
    copy .env.example .env
    echo .env created (update with your settings)
)

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Activate virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Add known faces to: known_faces\ directory
echo    Structure:
echo    known_faces\
echo    - person1\
echo      - image1.jpg
echo      - image2.jpg
echo    - person2\
echo      - image1.jpg
echo.
echo 3. Run the API:
echo    python main.py
echo.
echo 4. Visit: http://localhost:8000/docs
echo ==========================================
echo.
pause
