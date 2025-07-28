import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """
    Data processing class for football match prediction.
    Handles loading, cleaning, and preprocessing of match data from CSV files.
    """
    
    def __init__(self, data_path='csvs/'):
        self.data_path = data_path
        self.df = None
        self.team_stats = {}
        
    def load_data(self):
        """Load all CSV files from the data directory"""
        csv_files = glob.glob(os.path.join(self.data_path, "*.csv"))
        dataframes = []
        
        print(f"Loading {len(csv_files)} CSV files...")
        
        for file in csv_files:
            try:
                # Try different encodings
                df = None
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    print(f"✗ Could not read {file} with any encoding")
                    continue
                
                # Standardize column names for different formats
                column_mapping = {
                    'Home': 'HomeTeam',
                    'Away': 'AwayTeam',
                    'HG': 'FTHG',
                    'AG': 'FTAG',
                    'Res': 'FTR'
                }
                
                df = df.rename(columns=column_mapping)
                
                league = os.path.basename(file).replace('.csv', '')
                df['League'] = league
                dataframes.append(df)
                print(f"✓ Loaded {file}: {len(df)} matches")
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")
        
        if dataframes:
            self.df = pd.concat(dataframes, ignore_index=True, sort=False)
            print(f"\nTotal matches loaded: {len(self.df)}")
            return self.df
        else:
            raise ValueError("No data files could be loaded")
    
    def clean_data(self):
        """Clean and standardize the data"""
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        print("Cleaning data...")
        
        # Convert date column
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d/%m/%Y', errors='coerce')
        
        # Remove matches without essential data
        initial_rows = len(self.df)
        self.df = self.df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTR'])
        
        # Remove matches without betting odds
        odds_columns = ['B365H', 'B365D', 'B365A']
        self.df = self.df.dropna(subset=odds_columns)
        
        print(f"Removed {initial_rows - len(self.df)} incomplete matches")
        
        # Standardize team names (remove extra spaces, standardize case)
        self.df['HomeTeam'] = self.df['HomeTeam'].str.strip()
        self.df['AwayTeam'] = self.df['AwayTeam'].str.strip()
        
        # Sort by date
        self.df = self.df.sort_values('Date').reset_index(drop=True)
        
        print(f"✓ Data cleaned. Final dataset: {len(self.df)} matches")
        return self.df
    
    def calculate_team_form(self, team, date, matches=5):
        """Calculate team form (last N matches before given date)"""
        team_matches = self.df[
            ((self.df['HomeTeam'] == team) | (self.df['AwayTeam'] == team)) &
            (self.df['Date'] < date)
        ].tail(matches)
        
        if len(team_matches) == 0:
            return {'form_points': 0, 'wins': 0, 'draws': 0, 'losses': 0, 
                   'goals_for': 0, 'goals_against': 0, 'matches_played': 0}
        
        points = 0
        wins, draws, losses = 0, 0, 0
        goals_for, goals_against = 0, 0
        
        for _, match in team_matches.iterrows():
            if match['HomeTeam'] == team:
                gf, ga = match['FTHG'], match['FTAG']
                if match['FTR'] == 'H':
                    points += 3
                    wins += 1
                elif match['FTR'] == 'D':
                    points += 1
                    draws += 1
                else:
                    losses += 1
            else:  # Away team
                gf, ga = match['FTAG'], match['FTHG']
                if match['FTR'] == 'A':
                    points += 3
                    wins += 1
                elif match['FTR'] == 'D':
                    points += 1
                    draws += 1
                else:
                    losses += 1
            
            goals_for += gf
            goals_against += ga
        
        return {
            'form_points': points,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'matches_played': len(team_matches)
        }
    
    def calculate_head_to_head(self, home_team, away_team, date, matches=10):
        """Calculate head-to-head statistics between two teams"""
        h2h_matches = self.df[
            (((self.df['HomeTeam'] == home_team) & (self.df['AwayTeam'] == away_team)) |
             ((self.df['HomeTeam'] == away_team) & (self.df['AwayTeam'] == home_team))) &
            (self.df['Date'] < date)
        ].tail(matches)
        
        if len(h2h_matches) == 0:
            return {'h2h_home_wins': 0, 'h2h_draws': 0, 'h2h_away_wins': 0, 
                   'h2h_matches': 0, 'h2h_avg_goals': 0}
        
        home_wins = draws = away_wins = 0
        total_goals = 0
        
        for _, match in h2h_matches.iterrows():
            total_goals += match['FTHG'] + match['FTAG']
            
            if match['HomeTeam'] == home_team:
                if match['FTR'] == 'H':
                    home_wins += 1
                elif match['FTR'] == 'D':
                    draws += 1
                else:
                    away_wins += 1
            else:  # Teams are swapped
                if match['FTR'] == 'A':
                    home_wins += 1
                elif match['FTR'] == 'D':
                    draws += 1
                else:
                    away_wins += 1
        
        return {
            'h2h_home_wins': home_wins,
            'h2h_draws': draws,
            'h2h_away_wins': away_wins,
            'h2h_matches': len(h2h_matches),
            'h2h_avg_goals': total_goals / len(h2h_matches) if len(h2h_matches) > 0 else 0
        }
    
    def create_features(self):
        """Create features for machine learning"""
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() and clean_data() first.")
        
        print("Creating features...")
        features = []
        
        for idx, row in self.df.iterrows():
            if idx % 1000 == 0:
                print(f"Processing match {idx+1}/{len(self.df)}")
            
            # Basic match info
            feature_row = {
                'home_team': row['HomeTeam'],
                'away_team': row['AwayTeam'],
                'date': row['Date'],
                'league': row['League'],
                'result': row['FTR']
            }
            
            # Betting odds features
            feature_row['home_odds'] = row['B365H']
            feature_row['draw_odds'] = row['B365D'] 
            feature_row['away_odds'] = row['B365A']
            
            # Implied probabilities from odds
            total_prob = (1/row['B365H']) + (1/row['B365D']) + (1/row['B365A'])
            feature_row['home_prob'] = (1/row['B365H']) / total_prob
            feature_row['draw_prob'] = (1/row['B365D']) / total_prob
            feature_row['away_prob'] = (1/row['B365A']) / total_prob
            
            # Team form features
            home_form = self.calculate_team_form(row['HomeTeam'], row['Date'])
            away_form = self.calculate_team_form(row['AwayTeam'], row['Date'])
            
            # Add form features with prefix
            for key, value in home_form.items():
                feature_row[f'home_{key}'] = value
            for key, value in away_form.items():
                feature_row[f'away_{key}'] = value
            
            # Head-to-head features
            h2h = self.calculate_head_to_head(row['HomeTeam'], row['AwayTeam'], row['Date'])
            feature_row.update(h2h)
            
            # Additional match statistics if available
            if pd.notna(row.get('HS', np.nan)):
                feature_row['home_shots'] = row['HS']
                feature_row['away_shots'] = row['AS']
                feature_row['home_shots_target'] = row.get('HST', 0)
                feature_row['away_shots_target'] = row.get('AST', 0)
            else:
                feature_row['home_shots'] = 0
                feature_row['away_shots'] = 0
                feature_row['home_shots_target'] = 0
                feature_row['away_shots_target'] = 0
            
            features.append(feature_row)
        
        features_df = pd.DataFrame(features)
        print(f"✓ Created {len(features_df)} feature rows with {len(features_df.columns)} columns")
        
        return features_df
    
    def get_league_strength(self, league):
        """Get relative strength coefficient for different leagues"""
        league_strength = {
            'T1': 1.0,  # Turkish Super League (baseline)
            'SP1': 1.15,  # La Liga
            'pl2425': 1.20,  # Premier League
            'B1': 1.10,  # Bundesliga
            'it2425': 1.12,  # Serie A
            'F1': 1.13,  # Ligue 1
            'P1': 0.95,  # Liga Portugal
            'N1': 0.90,  # Eredivisie
            'G1': 0.85,  # Greek League
        }
        return league_strength.get(league, 1.0)
    
    def encode_categorical_features(self, df):
        """Encode categorical features for ML models"""
        df_encoded = df.copy()
        
        # Target encoding
        if 'result' in df_encoded.columns:
            result_mapping = {'H': 0, 'D': 1, 'A': 2}
            df_encoded['result_encoded'] = df_encoded['result'].map(result_mapping)
        
        # League encoding
        if 'league' in df_encoded.columns:
            df_encoded['league_strength'] = df_encoded['league'].apply(self.get_league_strength)
        
        return df_encoded
