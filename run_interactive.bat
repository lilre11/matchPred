@echo off
echo 💻 Starting Interactive Predictor...
echo.

REM Check if models exist
if not exist "models\spor_toto_model_rf.joblib" (
    echo ❌ No trained models found!
    echo Please run setup.bat first to train the models
    pause
    exit /b 1
)

echo ✅ Models found
echo 🚀 Starting interactive predictor...
echo.

python interactive_predictor.py

pause
