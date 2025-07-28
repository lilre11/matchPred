@echo off
echo 🏆 Setting up Spor Toto Prediction System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run setup script
python setup.py

echo.
echo Setup complete! Press any key to exit...
pause >nul
