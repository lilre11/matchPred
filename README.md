# 🏆 Football Match Prediction System for Turkey's Spor Toto

A comprehensive Python-based machine learning system that predicts football match outcomes (1-X-2) for Turkey's Spor Toto betting system. The system combines advanced ML algorithms with betting odds analysis to provide intelligent predictions.

## 🔍 Features

- **Machine Learning Models**: RandomForest + XGBoost ensemble predictions
- **Comprehensive Data Analysis**: Team form, head-to-head statistics, league strength
- **Betting Odds Integration**: Analyzes current odds for value betting opportunities  
- **Multiple Risk Levels**: Conservative, Medium, and Aggressive prediction strategies
- **Spor Toto Format**: Outputs predictions in the required format (m1(1-2), m2(X), etc.)
- **Expected Value Calculations**: Identifies profitable betting opportunities
- **Multi-League Support**: Turkish Super League, Premier League, La Liga, Bundesliga, etc.

## 📊 Input Data

The system processes CSV files containing:
- Match results (Home/Away teams, scores, outcomes)
- Betting odds from multiple bookmakers (B365, BWin, Pinnacle, etc.)
- Match statistics (shots, fouls, cards, etc.)
- League and date information

## 🧠 Machine Learning Pipeline

1. **Data Processing**: Loads and cleans match data from multiple leagues
2. **Feature Engineering**: Creates advanced features including:
   - Recent team form (wins/draws/losses)
   - Goal statistics and form trends
   - Head-to-head history between teams
   - League strength coefficients
   - Betting market implied probabilities
3. **Model Training**: Ensemble of RandomForest and XGBoost classifiers
4. **Prediction**: Combines ML probabilities with current betting odds
5. **Value Analysis**: Calculates expected value for betting decisions

## 🎯 Output Format

The system outputs predictions in Spor Toto format:
- `m1(1)`: Strong home win prediction
- `m2(X)`: Draw prediction  
- `m3(2)`: Away win prediction
- `m4(1-X)`: Home win or draw
- `m5(1-2)`: Avoid draw (home or away win)
- `m6(X-2)`: Draw or away win

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Usage

1. **Place your CSV data files in the `csvs/` folder**

2. **Run the main prediction system:**
```python
python main.py
```

3. **For quick predictions on new matches:**
```python
from main import predict_new_matches

upcoming_matches = [
    {
        'home_team': 'Galatasaray',
        'away_team': 'Fenerbahce', 
        'league': 'T1',
        'current_odds': {'home': 2.1, 'draw': 3.2, 'away': 3.4}
    }
]

predictions = predict_new_matches(upcoming_matches, risk_level='medium')
```

## 📁 Project Structure

```
matchBetCsv/
├── csvs/                      # CSV data files
├── models/                    # Saved ML models
├── predictions/               # Output predictions
├── data_processor.py          # Data loading and preprocessing
├── match_predictor.py         # ML models and training
├── spor_toto_predictor.py     # Spor Toto formatting and analysis
├── main.py                    # Main execution script
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## ⚙️ Configuration

### Risk Tolerance Levels

- **Conservative**: Higher confidence threshold (65%+), minimum 10% value edge
- **Medium**: Balanced approach (55%+), minimum 5% value edge  
- **Aggressive**: Lower threshold (45%+), minimum 2% value edge

### Supported Leagues

- `T1`: Turkish Super League
- `SP1`: Spanish La Liga
- `pl2425`: English Premier League
- `B1`: German Bundesliga
- `it2425`: Italian Serie A
- `F1`: French Ligue 1
- And more...

## 📈 Model Performance

The ensemble model typically achieves:
- **Accuracy**: 55-60% on test data
- **Value Detection**: Identifies positive expected value bets
- **Risk Management**: Adjustable confidence thresholds

## 🎲 Example Output

```
🔮 Spor Toto Predictions (Medium Risk)
============================================================
🏆 Galatasaray vs Fenerbahce
   Prediction: m1(1-X)
   Confidence: 67.3%
   Probabilities: 1:45.2% X:22.1% 2:32.7%
   💰 Value Bets: home_win

📋 WEEKLY SPOR TOTO SUMMARY
============================================================
🎫 COUPON FORMAT:
   m1(1-X)
   m2(2)
   m3(1-2)
   m4(X)
   m5(1)

📊 PREDICTION BREAKDOWN:
   Single outcomes: 2
   Double outcomes: 3
   Triple outcomes: 0
   Total combinations: 12
```

## 🔧 Advanced Usage

### Custom Feature Engineering
```python
processor = DataProcessor()
features_df = processor.create_features()
# Add custom features to features_df
```

### Model Hyperparameter Tuning
```python
predictor = MatchPredictor()
# Models automatically tune hyperparameters using GridSearchCV
results = predictor.train_models(features_df)
```

### Value Betting Analysis
```python
spor_toto = SporTotoPredictor(predictor, processor)
value_analysis = spor_toto.analyze_value_and_risk(
    prediction_result, 
    current_odds, 
    risk_tolerance='aggressive'
)
```

## 📊 Data Requirements

CSV files should contain these essential columns:
- `Date`: Match date (DD/MM/YYYY format)
- `HomeTeam`, `AwayTeam`: Team names
- `FTR`: Full-time result (H/D/A)
- `FTHG`, `FTAG`: Full-time goals
- `B365H`, `B365D`, `B365A`: Bet365 odds for Home/Draw/Away

## ⚠️ Disclaimer

This system is for educational and research purposes. Sports betting involves risk, and past performance does not guarantee future results. Always bet responsibly and within your means.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- New feature implementations
- Model improvements
- Bug fixes
- Documentation updates

## 📄 License

This project is open source and available under the MIT License.
