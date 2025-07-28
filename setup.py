#!/usr/bin/env python3
"""
🚀 Setup Script for Spor Toto Prediction System
This script helps set up the environment and run initial training
"""

import os
import sys
import subprocess
import argparse

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Basic requirements installed successfully!")
        
        # Ask about web interface
        web_install = input("\n🌐 Do you want to install web interface dependencies (Streamlit)? (y/n): ").lower()
        if web_install == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"])
            print("✅ Web interface dependencies installed!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ['models', 'predictions', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}/")

def check_data():
    """Check if CSV data files exist"""
    print("📊 Checking data files...")
    
    csvs_dir = 'csvs/'
    if not os.path.exists(csvs_dir):
        print(f"❌ CSV data directory '{csvs_dir}' not found!")
        print("Please ensure your CSV files are in the 'csvs/' directory")
        return False
    
    csv_files = [f for f in os.listdir(csvs_dir) if f.endswith('.csv')]
    if not csv_files:
        print(f"❌ No CSV files found in '{csvs_dir}'!")
        print("Please add your football match data CSV files to the 'csvs/' directory")
        return False
    
    print(f"✅ Found {len(csv_files)} CSV files:")
    for file in csv_files[:5]:  # Show first 5 files
        print(f"   • {file}")
    if len(csv_files) > 5:
        print(f"   ... and {len(csv_files) - 5} more files")
    
    return True

def train_models():
    """Train the machine learning models"""
    print("\n🧠 Training machine learning models...")
    print("This may take several minutes depending on your data size...")
    
    try:
        # Run main training script
        subprocess.check_call([sys.executable, "main.py"])
        print("✅ Model training completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during model training: {e}")
        return False

def run_interface_choice():
    """Let user choose which interface to run"""
    print("\n🎮 Choose how to run the prediction system:")
    print("1. 🌐 Web Interface (Streamlit) - Recommended for beginners")
    print("2. 💻 Interactive Command Line")
    print("3. 📝 Single Prediction Example")
    print("4. ❌ Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            print("🌐 Starting web interface...")
            try:
                subprocess.check_call([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
            except subprocess.CalledProcessError:
                print("❌ Error starting web interface. Make sure Streamlit is installed.")
            break
            
        elif choice == '2':
            print("💻 Starting interactive command line...")
            try:
                subprocess.check_call([sys.executable, "interactive_predictor.py"])
            except subprocess.CalledProcessError:
                print("❌ Error starting interactive predictor.")
            break
            
        elif choice == '3':
            print("📝 Running single prediction example...")
            run_example_prediction()
            break
            
        elif choice == '4':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-4.")

def run_example_prediction():
    """Run a simple example prediction"""
    print("\n🔮 Example Prediction")
    print("-" * 30)
    
    try:
        from data_processor import DataProcessor
        from match_predictor import MatchPredictor
        from spor_toto_predictor import SporTotoPredictor
        
        # Load system
        print("Loading prediction system...")
        processor = DataProcessor()
        processor.load_data()
        processor.clean_data()
        
        predictor = MatchPredictor()
        predictor.load_models('models/spor_toto_model')
        
        spor_toto = SporTotoPredictor(predictor, processor)
        
        # Example prediction
        example_match = {
            'home_team': 'Galatasaray',
            'away_team': 'Fenerbahce',
            'league': 'T1',
            'current_odds': {'home': 2.1, 'draw': 3.2, 'away': 3.4}
        }
        
        print("\n🏆 Predicting: Galatasaray vs Fenerbahce")
        predictions = spor_toto.predict_matches([example_match])
        
        if predictions:
            pred = predictions[0]
            print(f"🎯 Prediction: {pred['spor_toto_prediction']}")
            print(f"📊 Confidence: {pred['ml_prediction']['confidence']:.1f}%")
            probs = pred['ml_prediction']['probabilities']
            print(f"📈 Probabilities: 1:{probs['home_win']:.1f}% X:{probs['draw']:.1f}% 2:{probs['away_win']:.1f}%")
            
            if pred['value_analysis'] and pred['value_analysis']['good_bets']:
                print(f"💰 Value Bets: {', '.join([bet[0] for bet in pred['value_analysis']['good_bets']])}")
        
    except Exception as e:
        print(f"❌ Error running example: {e}")

def main():
    parser = argparse.ArgumentParser(description="Setup Spor Toto Prediction System")
    parser.add_argument("--skip-install", action="store_true", help="Skip package installation")
    parser.add_argument("--skip-training", action="store_true", help="Skip model training")
    parser.add_argument("--train-only", action="store_true", help="Only train models, don't run interface")
    
    args = parser.parse_args()
    
    print("🏆 SPOR TOTO PREDICTION SYSTEM SETUP")
    print("=" * 50)
    
    # Step 1: Install packages
    if not args.skip_install:
        if not install_requirements():
            print("❌ Setup failed during package installation")
            return
    else:
        print("⏭️ Skipping package installation")
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Check data
    if not check_data():
        print("\n❌ Setup cannot continue without data files")
        print("Please add your CSV files to the 'csvs/' directory and run setup again")
        return
    
    # Step 4: Train models
    if not args.skip_training:
        if not os.path.exists('models/spor_toto_model_rf.joblib'):
            print("\n🧠 No trained models found. Training new models...")
            if not train_models():
                print("❌ Setup failed during model training")
                return
        else:
            retrain = input("\n🔄 Trained models already exist. Retrain? (y/n): ").lower()
            if retrain == 'y':
                if not train_models():
                    print("❌ Setup failed during model training")
                    return
            else:
                print("✅ Using existing trained models")
    else:
        print("⏭️ Skipping model training")
    
    # Step 5: Run interface (unless train-only)
    if not args.train_only:
        print("\n🎉 Setup completed successfully!")
        run_interface_choice()
    else:
        print("\n🎉 Training completed successfully!")
        print("Run 'python setup.py' without --train-only to use the prediction system")

if __name__ == "__main__":
    main()
