# Spor Toto Prediction Bot

A machine learning-based prediction system for Turkish Spor Toto matches. This bot analyzes historical match data and team statistics to predict match outcomes (1-X-2).

## Features

- **Data Collection**: Scrapes match data from Turkish football leagues
- **Feature Engineering**: Creates meaningful features from team statistics
- **ML Models**: Multiple models (Random Forest, XGBoost, Neural Network)
- **Ensemble Prediction**: Combines multiple models for better accuracy
- **Spor Toto Integration**: Specifically designed for 15-match predictions
- **Performance Tracking**: Monitors prediction accuracy over time

## Project Structure

```
matchBet/
├── data/                  # Data storage
│   ├── raw/              # Raw scraped data
│   ├── processed/        # Cleaned and processed data
│   └── models/           # Saved ML models
├── src/                  # Source code
│   ├── data_collection/  # Data scraping modules
│   ├── preprocessing/    # Data cleaning and feature engineering
│   ├── models/          # ML model implementations
│   ├── prediction/      # Prediction logic
│   └── utils/           # Utility functions
├── notebooks/           # Jupyter notebooks for analysis
├── config/             # Configuration files
└── tests/              # Unit tests
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API keys in `config/settings.py`
4. Run data collection: `python src/data_collection/scraper.py`
5. Train models: `python src/models/train_models.py`
6. Make predictions: `python src/prediction/predict.py`

## Usage

```python
from src.prediction.predictor import SportTotoPredictor

predictor = SportTotoPredictor()
predictions = predictor.predict_weekly_matches()
print(f"Predicted outcomes: {predictions}")
```

## Accuracy Target

- Target: Predict at least 12 out of 15 matches correctly
- Current best model accuracy: ~65-70% per match
- Probability of 12+ correct: ~15-25% (varies by week)

## Legal Notice

This tool is for educational and research purposes only. Gambling can be addictive. Please bet responsibly.
