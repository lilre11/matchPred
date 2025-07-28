#!/usr/bin/env python3
"""
Build script to create executable for Spor Toto Predictor
"""

import os
import sys
import shutil
import subprocess

def build_executable():
    """Build the executable using PyInstaller"""
    
    print("🏗️ Building Spor Toto Predictor Executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous builds
    if os.path.exists("dist"):
        print("🧹 Cleaning previous builds...")
        shutil.rmtree("dist")
    
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    if os.path.exists("spor_toto_gui.spec"):
        os.remove("spor_toto_gui.spec")
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=SporTotoPredictor",     # Executable name
        "--icon=icon.ico",              # Icon (if exists)
        "--add-data=csvs;csvs",         # Include CSV data
        "--add-data=models;models",     # Include models (if they exist)
        "--hidden-import=sklearn.ensemble._forest", # Fix scikit-learn import
        "--hidden-import=sklearn.tree._tree",       # Fix scikit-learn import
        "--hidden-import=xgboost.sklearn",          # Fix XGBoost import
        "--hidden-import=pandas._libs.tslibs.base", # Fix pandas import
        "--collect-all=sklearn",        # Include all sklearn
        "--collect-all=xgboost",        # Include all xgboost
        "spor_toto_gui.py"
    ]
    
    # Remove icon if it doesn't exist
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
    
    print(f"🔨 Running: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = os.path.join("dist", "SporTotoPredictor.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📦 Executable created: {exe_path} ({size_mb:.1f} MB)")
            
            # Create a simple installer
            create_installer()
        else:
            print("❌ Executable not found!")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def create_installer():
    """Create a simple installer/launcher script"""
    
    installer_content = '''@echo off
echo.
echo ============================================
echo  Spor Toto Match Predictor v1.0
echo  AI-Powered Football Predictions
echo ============================================
echo.

echo Installing Spor Toto Predictor...
echo.

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\\SporTotoPredictor
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "SporTotoPredictor.exe" "%INSTALL_DIR%\\" >nul
if errorlevel 1 (
    echo Error: Could not copy executable!
    pause
    exit /b 1
)

REM Create desktop shortcut
set SHORTCUT_PATH=%USERPROFILE%\\Desktop\\Spor Toto Predictor.lnk
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SporTotoPredictor.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

REM Create start menu shortcut  
set STARTMENU_PATH=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Spor Toto Predictor.lnk
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_PATH%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SporTotoPredictor.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo ✅ Installation completed successfully!
echo.
echo 📍 Installed to: %INSTALL_DIR%
echo 🖥️  Desktop shortcut created
echo 📋 Start menu shortcut created
echo.
echo You can now run Spor Toto Predictor from:
echo - Desktop shortcut
echo - Start menu
echo - %INSTALL_DIR%\\SporTotoPredictor.exe
echo.

REM Ask to run now
set /p RUN_NOW="Would you like to run Spor Toto Predictor now? (y/n): "
if /i "%RUN_NOW%"=="y" (
    echo Starting Spor Toto Predictor...
    start "" "%INSTALL_DIR%\\SporTotoPredictor.exe"
)

echo.
echo Thank you for using Spor Toto Predictor!
pause
'''
    
    with open("dist/install.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    
    print("📦 Installer created: dist/install.bat")

def create_readme():
    """Create README for the executable"""
    
    readme_content = """# 🏆 Spor Toto Match Predictor

AI-Powered Football Match Predictions for Turkish Spor Toto

## 🚀 Quick Start

### Installation
1. Run `install.bat` to install the application
2. Launch from desktop shortcut or start menu

### Manual Installation
1. Copy `SporTotoPredictor.exe` to desired folder
2. Double-click to run

## 📝 How to Use

### Input Methods
1. **Manual Entry**: Enter matches one by one
2. **Paste All**: Copy all 15 matches and paste
3. **Load File**: Import from CSV, TXT, or JSON file

### Match Format
- Home Team vs Away Team
- Example: "Galatasaray vs Fenerbahce"

### Prediction Process
1. Enter 15 matches (required for Spor Toto)
2. Select risk level (Conservative/Medium/Aggressive)
3. Choose default league
4. Click "PREDICT ALL MATCHES"
5. Get predictions in Spor Toto format

### Output Formats
- **Spor Toto Coupon**: Ready to submit format
- **Detailed Analysis**: Probabilities and confidence
- **Export Options**: TXT, CSV, or copy to clipboard

## 🎯 Understanding Predictions

### Spor Toto Format
- `m1(1)`: Strong home win
- `m2(X)`: Draw prediction  
- `m3(2)`: Away win
- `m4(1-X)`: Home win or draw
- `m5(1-2)`: Avoid draw
- `m6(X-2)`: Draw or away win

### Confidence Levels
- 🟢 High (70%+): Single outcome
- 🟡 Medium (50-70%): Two outcomes
- 🔴 Low (<50%): Three outcomes

### Risk Levels
- **Conservative**: Higher confidence, safer picks
- **Medium**: Balanced approach
- **Aggressive**: Higher risk, higher reward

## 📊 Supported Leagues
- Turkish Super League
- Spanish La Liga
- English Premier League
- German Bundesliga
- Italian Serie A
- French Ligue 1
- Portuguese Liga
- Dutch Eredivisie
- Greek Super League
- And more...

## 💡 Tips
- Use real team names for better accuracy
- Mix different leagues for variety
- Check confidence levels before betting
- Export predictions for record keeping

## ⚠️ Disclaimer
- Predictions based on historical data
- Past performance doesn't guarantee future results
- Bet responsibly and within your means
- Use as guidance, not absolute truth

## 🔧 Technical Info
- Powered by machine learning models
- Uses XGBoost and Random Forest
- Analyzes historical match data
- Includes value betting analysis

## 📞 Support
For issues or questions, check the help section in the application.

---
Spor Toto Match Predictor v1.0
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📚 README created: dist/README.txt")

if __name__ == "__main__":
    print("🏗️ Spor Toto Predictor Build Script")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        "spor_toto_gui.py",
        "data_processor.py", 
        "match_predictor.py",
        "spor_toto_predictor.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        sys.exit(1)
    
    # Check if data directory exists
    if not os.path.exists("csvs"):
        print("❌ CSV data directory not found!")
        sys.exit(1)
    
    print("✅ All required files found")
    print()
    
    # Build executable
    if build_executable():
        create_readme()
        print()
        print("🎉 Build process completed!")
        print("📁 Check the 'dist' folder for your executable")
        print("🚀 Run 'install.bat' to install the application")
    else:
        print("❌ Build process failed!")
        sys.exit(1)
