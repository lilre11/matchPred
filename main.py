#!/usr/bin/env python3
"""
🏆 Football Match Prediction System for Turkey's Spor Toto
🔮 Predicts 1-X-2 outcomes using Machine Learning + Betting Odds Analysis

This is the main script that trains the ML models and generates predictions.
Run this script to train models on historical data and make predictions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from data_processor import DataProcessor
from match_predictor import MatchPredictor  
from spor_toto_predictor import SporTotoPredictor

def main():
    print("🏆 FOOTBALL MATCH PREDICTION SYSTEM")
    print("🎯 Spor Toto 1-X-2 Predictions")
    print("="*50)
    
    # Step 1: Load and process data
    print("\n📊 Step 1: Loading and Processing Data")
    print("-" * 40)
    
    processor = DataProcessor(data_path='csvs/')
    
    # Load all CSV files
    df = processor.load_data()
    
    # Clean the data
    df_clean = processor.clean_data()
    
    # Create features for ML
    features_df = processor.create_features()
    
    # Encode categorical features
    features_encoded = processor.encode_categorical_features(features_df)
    
    print(f"✅ Data processing complete!")
    print(f"   Total matches: {len(features_encoded)}")
    print(f"   Date range: {features_encoded['date'].min()} to {features_encoded['date'].max()}")
    print(f"   Leagues: {features_encoded['league'].unique()}")
    
    # Step 2: Train ML models
    print("\n🧠 Step 2: Training Machine Learning Models")
    print("-" * 40)
    
    predictor = MatchPredictor()
    
    # Train models (this will take a few minutes)
    results = predictor.train_models(features_encoded, test_size=0.2)
    
    print(f"\n✅ Model training complete!")
    print(f"   RandomForest Accuracy: {results['rf_accuracy']:.3f}")
    print(f"   XGBoost Accuracy: {results['xgb_accuracy']:.3f}")
    print(f"   Ensemble Accuracy: {results['ensemble_accuracy']:.3f}")
    
    # Save trained models
    predictor.save_models('models/spor_toto_model')
    
    # Step 3: Create Spor Toto predictor
    print("\n🎯 Step 3: Setting up Spor Toto Prediction System")
    print("-" * 40)
    
    spor_toto = SporTotoPredictor(predictor, processor)
    
    # Step 4: Example predictions for upcoming matches
    print("\n🔮 Step 4: Example Match Predictions")
    print("-" * 40)
    
    # Example upcoming matches (replace with real upcoming matches)
    upcoming_matches = [
        {
            'home_team': 'Galatasaray',
            'away_team': 'Fenerbahce',
            'league': 'T1',
            'current_odds': {'home': 2.1, 'draw': 3.2, 'away': 3.4},
            'date': '2024-12-01'
        },
        {
            'home_team': 'Besiktas', 
            'away_team': 'Trabzonspor',
            'league': 'T1',
            'current_odds': {'home': 1.8, 'draw': 3.5, 'away': 4.2},
            'date': '2024-12-01'
        },
        {
            'home_team': 'Samsunspor',
            'away_team': 'Konyaspor', 
            'league': 'T1',
            'current_odds': {'home': 2.3, 'draw': 3.1, 'away': 2.9},
            'date': '2024-12-01'
        },
        {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'league': 'SP1',
            'current_odds': {'home': 2.5, 'draw': 3.3, 'away': 2.7},
            'date': '2024-12-01'
        },
        {
            'home_team': 'Man United',
            'away_team': 'Arsenal',
            'league': 'pl2425',
            'current_odds': {'home': 3.1, 'draw': 3.4, 'away': 2.2},
            'date': '2024-12-01'
        }
    ]
    
    # Generate predictions with different risk tolerances
    print("\n🎲 CONSERVATIVE PREDICTIONS (Low Risk)")
    conservative_predictions = spor_toto.predict_matches(upcoming_matches, 'conservative')
    
    print("\n⚖️ MEDIUM RISK PREDICTIONS (Balanced)")
    medium_predictions = spor_toto.predict_matches(upcoming_matches, 'medium')
    
    print("\n🔥 AGGRESSIVE PREDICTIONS (High Risk)")
    aggressive_predictions = spor_toto.predict_matches(upcoming_matches, 'aggressive')
    
    # Generate weekly summary
    weekly_summary = spor_toto.generate_weekly_predictions(
        upcoming_matches, 
        output_file='predictions/weekly_predictions.txt'
    )
    
    print("\n🎉 PREDICTION SYSTEM READY!")
    print("="*50)
    print("📝 To use the system:")
    print("1. Update upcoming_matches list with real match data")
    print("2. Run this script to get predictions")  
    print("3. Check predictions/weekly_predictions.txt for formatted output")
    print("\n🔍 Key Features:")
    print("• Machine Learning predictions (RandomForest + XGBoost)")
    print("• Betting odds analysis and value detection")
    print("• Multiple risk tolerance levels")
    print("• Spor Toto format output (m1(1-2), m2(X), etc.)")
    print("• Expected value calculations")
    print("• Historical team form analysis")
    print("• Head-to-head statistics")

def predict_new_matches(matches_list, risk_level='medium'):
    """
    Convenience function to predict new matches after training
    
    Args:
        matches_list: List of match dictionaries
        risk_level: 'conservative', 'medium', or 'aggressive'
    """
    # Load pre-trained models
    processor = DataProcessor(data_path='csvs/')
    processor.load_data()
    processor.clean_data()
    
    predictor = MatchPredictor()
    predictor.load_models('models/spor_toto_model')
    
    spor_toto = SporTotoPredictor(predictor, processor)
    
    return spor_toto.predict_matches(matches_list, risk_level)

if __name__ == "__main__":
    # Create directories for output
    import os
    os.makedirs('models', exist_ok=True)
    os.makedirs('predictions', exist_ok=True)
    
    # Run main prediction system
    main()
