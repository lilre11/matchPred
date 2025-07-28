@echo off
echo 🌐 Starting Spor Toto Web Interface...
echo.

REM Check if models exist
if not exist "models\spor_toto_model_rf.joblib" (
    echo ❌ No trained models found!
    echo Please run setup.bat first to train the models
    pause
    exit /b 1
)

echo ✅ Models found
echo 🚀 Starting web interface...
echo.
echo Your browser will open automatically
echo If not, go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run streamlit_app.py

pause
