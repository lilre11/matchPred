# 🏆 Quick Start Guide - Spor Toto Prediction System

## 🚀 1. Initial Setup (First Time Only)

### Option A: Using Setup Script (Recommended)
Double-click `setup.bat` or run:
```bash
python setup.py
```

### Option B: Manual Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. For web interface (optional):
```bash
pip install -r requirements_web.txt
```

3. Train models:
```bash
python main.py
```

## 🎮 2. Using the Prediction System

### 🌐 Web Interface (Easiest)
- Double-click `run_web.bat` or run:
```bash
streamlit run streamlit_app.py
```
- Open browser to `http://localhost:8501`
- Use the intuitive web interface

### 💻 Interactive Command Line
- Double-click `run_interactive.bat` or run:
```bash
python interactive_predictor.py
```

### 📝 Direct Script Usage
```python
from main import predict_new_matches

matches = [
    {
        'home_team': 'Galatasaray',
        'away_team': 'Fenerbahce',
        'league': 'T1',
        'current_odds': {'home': 2.1, 'draw': 3.2, 'away': 3.4}
    }
]

predictions = predict_new_matches(matches, risk_level='medium')
```

## 🎯 3. Understanding Predictions

### Spor Toto Format Examples:
- `m1(1)` = Strong home win
- `m2(X)` = Draw likely
- `m3(2)` = Away win expected
- `m4(1-X)` = Home win or draw
- `m5(1-2)` = Avoid draw (home or away win)
- `m6(X-2)` = Draw or away win

### Risk Levels:
- **Conservative**: High confidence (65%+), safer picks
- **Medium**: Balanced approach (55%+) 
- **Aggressive**: Higher risk/reward (45%+)

## 📊 4. Input Data Format

Your CSV files should contain:
- `Date`: DD/MM/YYYY format
- `HomeTeam`, `AwayTeam`: Team names
- `FTR`: Result (H/D/A)
- `FTHG`, `FTAG`: Goals scored
- `B365H`, `B365D`, `B365A`: Betting odds

## 🏆 5. Supported Leagues

| Code | League |
|------|--------|
| T1 | Turkish Super League |
| SP1 | Spanish La Liga |
| pl2425 | English Premier League |
| B1 | German Bundesliga |
| it2425 | Italian Serie A |
| F1 | French Ligue 1 |
| P1 | Portuguese Liga |
| N1 | Dutch Eredivisie |

## 💡 6. Tips for Best Results

1. **Use Recent Data**: Include latest season data for better accuracy
2. **Include Odds**: Betting odds improve prediction quality significantly
3. **Correct Team Names**: Ensure team names match between prediction and training data
4. **Multiple Leagues**: More diverse data improves model robustness
5. **Regular Updates**: Retrain models with new data periodically

## 🔧 7. Troubleshooting

### "No trained models found"
- Run `setup.bat` or `python main.py` to train models first

### "Could not parse match"
- Use format: "Team1 vs Team2" or "Team1 - Team2"

### "Error loading data"
- Check CSV files are in `csvs/` directory
- Verify CSV format matches requirements

### Web interface won't start
- Install web dependencies: `pip install -r requirements_web.txt`
- Check port 8501 is not in use

## 📈 8. Advanced Usage

### Batch Predictions from CSV:
```python
import pandas as pd
from main import predict_new_matches

# Load matches from CSV
df = pd.read_csv('upcoming_matches.csv')
matches = df.to_dict('records')

predictions = predict_new_matches(matches)
```

### Custom Risk Analysis:
```python
from spor_toto_predictor import SporTotoPredictor

# Initialize predictor
spor_toto = SporTotoPredictor(predictor, processor)

# Analyze value bets
value_analysis = spor_toto.analyze_value_and_risk(
    prediction_result, 
    current_odds, 
    risk_tolerance='aggressive'
)
```

## ⚠️ 9. Important Notes

- **Educational Purpose**: This system is for research and educational use
- **No Guarantees**: Past performance doesn't predict future results
- **Responsible Use**: Always bet responsibly and within your means
- **Data Quality**: Predictions are only as good as the input data

## 🆘 10. Getting Help

- Check `README.md` for detailed documentation
- Review example outputs in `predictions/` folder
- Ensure all dependencies are installed correctly
- Verify CSV data format matches requirements

## 📝 11. Quick Command Reference

| Action | Command |
|--------|---------|
| Initial Setup | `python setup.py` |
| Train Models | `python main.py` |
| Web Interface | `streamlit run streamlit_app.py` |
| Interactive CLI | `python interactive_predictor.py` |
| Example Prediction | `python -c "from main import predict_new_matches; print(predict_new_matches([{'home_team':'Galatasaray','away_team':'Fenerbahce','league':'T1'}]))"` |

---

🎉 **You're ready to start predicting football matches!** 

Start with the web interface for the easiest experience, then explore the command-line tools for more advanced usage.
