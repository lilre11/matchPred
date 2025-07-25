@echo off
echo Setting up Spor Toto Prediction Bot...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found!

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To run the bot:
echo 1. Activate environment: venv\Scripts\activate.bat
echo 2. Collect data: python main.py --collect-data
echo 3. Train models: python main.py --train
echo 4. Make predictions: python main.py --predict
echo.
echo For full pipeline: python main.py --full-pipeline
echo.
echo For Jupyter analysis: jupyter notebook notebooks/spor_toto_analysis.ipynb
echo.
pause
