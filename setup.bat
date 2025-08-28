@echo off
echo ========================================
echo Hand Tracking Media Controller v2.1
echo Project Setup Script
echo ========================================
echo.

REM Create necessary directories
echo Creating project directories...
if not exist "src" mkdir src
if not exist "src\hand_tracking" mkdir src\hand_tracking
if not exist "src\media_controllers" mkdir src\media_controllers
if not exist "src\utils" mkdir src\utils
if not exist "drivers" mkdir drivers
if not exist "logs" mkdir logs
if not exist "config" mkdir config

echo ✅ Directories created successfully
echo.

REM Create __init__.py files for Python packages
echo Creating Python package files...
echo. > src\__init__.py
echo. > src\hand_tracking\__init__.py
echo. > src\media_controllers\__init__.py
echo. > src\utils\__init__.py

echo ✅ Package files created successfully
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
) else (
    python --version
    echo ✅ Python is installed
)
echo.

REM Check if virtual environment exists
if exist "venv" (
    echo ✅ Virtual environment already exists
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    ) else (
        echo ✅ Virtual environment created successfully
    )
)
echo.

REM Activate virtual environment and install packages
echo Activating virtual environment and installing packages...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
if exist "requirements.txt" (
    echo Installing requirements from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install some packages
        echo Trying individual installations...
        pip install opencv-python
        pip install mediapipe
        pip install selenium
        pip install python-dotenv
        pip install requests
        pip install psutil
    ) else (
        echo ✅ All packages installed successfully
    )
) else (
    echo Installing core packages...
    pip install opencv-python mediapipe selenium python-dotenv requests psutil
)
echo.

REM Check Chrome installation
echo Checking Google Chrome installation...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo ✅ Google Chrome found in Program Files
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo ✅ Google Chrome found in Program Files (x86)
) else (
    echo ❌ Google Chrome not found
    echo Please install Google Chrome from https://www.google.com/chrome/
    echo.
)

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo To run the application:
echo 1. Double-click "run_media_controller.bat"
echo 2. Or run: python main.py
echo.
echo Note: Make sure to place all your source files in the correct directories:
echo - main.py in the root directory
echo - Controller files in src/media_controllers/
echo - Hand tracking files in src/hand_tracking/
echo - Utility files in src/utils/
echo.
pause