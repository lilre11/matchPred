#!/usr/bin/env python3
"""
Spor Toto Prediction Bot - Main Application
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import (
    MODEL_CONFIG, FEATURE_CONFIG, PREDICTION_CONFIG, 
    PATHS, LOGGING_CONFIG
)

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['file']),
            logging.StreamHandler(sys.stdout)
        ]
    )

def create_directories():
    """Create necessary directories"""
    for path in PATHS.values():
        os.makedirs(path, exist_ok=True)

def collect_data():
    """Collect and update data"""
    from src.data_collection.scraper import TurkishFootballScraper
    
    logger = logging.getLogger(__name__)
    logger.info("Starting data collection")
    
    scraper = TurkishFootballScraper({'data_raw_dir': PATHS['data_raw']})
    results = scraper.update_data()
    
    logger.info(f"Data collection completed: {results}")
    return results

def train_models():
    """Train ML models"""
    import pandas as pd
    from src.preprocessing.feature_engineering import FeatureEngineer
    from src.models.ml_models import MLModelTrainer
    
    logger = logging.getLogger(__name__)
    logger.info("Starting model training")
    
    # Load historical data
    data_file = os.path.join(PATHS['data_raw'], 'historical_matches.csv')
    if not os.path.exists(data_file):
        logger.error(f"Historical data file not found: {data_file}")
        return None
    
    df = pd.read_csv(data_file)
    logger.info(f"Loaded {len(df)} historical matches")
    
    # Feature engineering
    feature_engineer = FeatureEngineer(
        lookback_matches=FEATURE_CONFIG['lookback_matches'],
        form_window=FEATURE_CONFIG['form_window']
    )
    
    df_features = feature_engineer.create_features(df)
    
    # Prepare training data
    feature_columns = [col for col in df_features.columns 
                      if col not in ['target', 'match_id', 'home_team', 'away_team', 'date']]
    
    X = df_features[feature_columns].fillna(0)
    y = df_features['target']
    
    # Save feature columns for later use
    feature_file = os.path.join(PATHS['models'], 'feature_columns.json')
    with open(feature_file, 'w') as f:
        json.dump(feature_columns, f)
    
    # Train models
    config = MODEL_CONFIG.copy()
    config['models_dir'] = PATHS['models']
    
    trainer = MLModelTrainer(config)
    results = trainer.train_models(X, y)
    
    logger.info(f"Model training completed: {results}")
    return results

def make_predictions():
    """Make predictions for current Spor Toto matches"""
    import pandas as pd
    from src.prediction.predictor import SportTotoPredictor
    
    logger = logging.getLogger(__name__)
    logger.info("Making Spor Toto predictions")
    
    # Load current matches
    matches_file = os.path.join(PATHS['data_raw'], 'current_spor_toto_matches.json')
    if not os.path.exists(matches_file):
        logger.error(f"Current matches file not found: {matches_file}")
        return None
    
    with open(matches_file, 'r') as f:
        matches = json.load(f)
    
    # Initialize predictor
    config = PREDICTION_CONFIG.copy()
    config['models_dir'] = PATHS['models']
    config['output_dir'] = PATHS['output']
    
    predictor = SportTotoPredictor(config)
    
    try:
        predictor.load_models()
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        logger.info("Please train models first using: python main.py --train")
        return None
    
    # Make predictions
    predictions = predictor.predict_weekly_matches(matches)
    
    # Save predictions
    predictions_file = predictor.save_predictions(predictions)
    
    # Display results
    print("\\n" + "="*60)
    print("SPOR TOTO PREDICTIONS")
    print("="*60)
    
    for i, pred in enumerate(predictions['predictions'], 1):
        match = pred['match_info']
        print(f"\\nMatch {i:2d}: {match['home_team']} vs {match['away_team']}")
        print(f"League: {match['league']}")
        print(f"Prediction: {pred['prediction_text']}")
        print(f"Confidence: {pred['confidence']:.2f}")
        print(f"Probabilities: 1:{pred['probabilities']['home_win']:.2f} "
              f"X:{pred['probabilities']['draw']:.2f} "
              f"2:{pred['probabilities']['away_win']:.2f}")
    
    print("\\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Expected correct predictions: {predictions['expected_correct_predictions']:.1f}/15")
    print(f"Average confidence: {predictions['average_confidence']:.2f}")
    print(f"Probability of 12+ correct: {predictions['probability_12_plus_correct']:.1%}")
    print(f"Recommendation: {predictions['recommendation']}")
    print(f"\\nPredictions saved to: {predictions_file}")
    
    return predictions

def analyze_performance():
    """Analyze prediction performance"""
    # This would analyze past predictions against actual results
    # For now, just log that it's not implemented
    logger = logging.getLogger(__name__)
    logger.info("Performance analysis not yet implemented")
    print("Performance analysis feature coming soon!")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Spor Toto Prediction Bot')
    parser.add_argument('--collect-data', action='store_true', 
                       help='Collect and update data')
    parser.add_argument('--train', action='store_true',
                       help='Train ML models')
    parser.add_argument('--predict', action='store_true',
                       help='Make predictions for current matches')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze prediction performance')
    parser.add_argument('--full-pipeline', action='store_true',
                       help='Run full pipeline (collect data, train, predict)')
    
    args = parser.parse_args()
    
    # Setup
    setup_logging()
    create_directories()
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Spor Toto Prediction Bot")
    
    try:
        if args.full_pipeline:
            logger.info("Running full pipeline")
            collect_data()
            train_models()
            make_predictions()
        elif args.collect_data:
            collect_data()
        elif args.train:
            train_models()
        elif args.predict:
            make_predictions()
        elif args.analyze:
            analyze_performance()
        else:
            # Default: just make predictions if models exist
            print("Spor Toto Prediction Bot")
            print("Use --help for available options")
            print("\\nTrying to make predictions with existing models...")
            make_predictions()
    
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1
    
    logger.info("Application completed successfully")
    return 0

if __name__ == '__main__':
    sys.exit(main())
