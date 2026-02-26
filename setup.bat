@echo off
echo ==================================================
echo    SETUP SPK DIAGNOSIS PENYAKIT CABAI
echo ==================================================

:: Check Python version
echo [1/5] Checking Python version...
python --version
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Create virtual environment
echo [2/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment!
    pause
    exit /b 1
)

:: Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo [4/5] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

:: Create necessary directories
echo [5/5] Creating project structure...
if not exist templates\admin mkdir templates\admin
if not exist templates\errors mkdir templates\errors
if not exist static\css mkdir static\css
if not exist static\js mkdir static\js

echo ==================================================
echo    SETUP COMPLETED SUCCESSFULLY!
echo ==================================================
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python app.py
echo 3. Open browser: http://localhost:5000
echo.
echo Demo credentials:
echo    Admin:  username='admin', password='admin123'
echo    Petani: username='petani', password='petani123'
echo.
pause