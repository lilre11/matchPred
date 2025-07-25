import os
from dotenv import load_dotenv

load_dotenv()

# Data Collection Settings
DATA_SOURCES = {
    'spor_toto_official': 'https://www.iddaa.com/spor-toto',
    'nesine': 'https://www.nesine.com/spor-toto',
    'mackolik': 'https://www.mackolik.com',
    'international_leagues': {
        'premier_league': 'https://www.premierleague.com/fixtures',
        'la_liga': 'https://www.laliga.com/en-GB/fixtures',
        'bundesliga': 'https://www.bundesliga.com/en/bundesliga/matchday',
        'serie_a': 'https://www.legaseriea.it/en/fixtures-and-results',
        'ligue_1': 'https://www.ligue1.com/matches'
    }
}

# Database Settings
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'spor_toto'),
    'username': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# ML Model Settings
MODEL_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'cross_validation_folds': 5,
    'models': {
        'random_forest': {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5
        },
        'xgboost': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 6
        },
        'neural_network': {
            'hidden_layers': [64, 32, 16],
            'epochs': 100,
            'batch_size': 32
        }
    }
}

# Feature Engineering Settings
FEATURE_CONFIG = {
    'lookback_matches': 10,  # Number of previous matches to consider
    'form_window': 5,        # Recent form window
    'head_to_head_matches': 5,
    'league_weights': {
        'Premier League': 1.0,
        'La Liga': 0.95,
        'Bundesliga': 0.90,
        'Serie A': 0.90,
        'Ligue 1': 0.85,
        'Primeira Liga': 0.75,
        'Eredivisie': 0.70,
        'Pro League': 0.65,
        'Super Lig': 0.60,
        'Scottish Premiership': 0.55,
        'Austrian Bundesliga': 0.50,
        'Swiss Super League': 0.45,
        'Greek Super League': 0.40,
        'Eliteserien': 0.35,
        'Allsvenskan': 0.35
    },
    'spor_toto_leagues': [
        'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1',
        'Super Lig', 'Eredivisie', 'Primeira Liga', 'Pro League', 'Scottish Premiership'
    ]
}

# Prediction Settings
PREDICTION_CONFIG = {
    'ensemble_weights': {
        'random_forest': 0.3,
        'xgboost': 0.4,
        'neural_network': 0.3
    },
    'confidence_threshold': 0.6,
    'spor_toto_matches': 15
}

# Paths
PATHS = {
    'data_raw': 'data/raw',
    'data_processed': 'data/processed',
    'models': 'data/models',
    'logs': 'logs',
    'output': 'output'
}

# Logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/spor_toto_bot.log'
}
