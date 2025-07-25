import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional

class FeatureEngineer:
    """
    Feature engineering class for creating meaningful features from raw match data
    """
    
    def __init__(self, lookback_matches: int = 10, form_window: int = 5):
        self.lookback_matches = lookback_matches
        self.form_window = form_window
        self.logger = logging.getLogger(__name__)
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create comprehensive features for match prediction
        """
        self.logger.info("Starting feature engineering process")
        
        # Sort by date to ensure proper time series order
        df = df.sort_values('date').reset_index(drop=True)
        
        # Create basic features
        df = self._create_basic_features(df)
        
        # Create team statistics
        df = self._create_team_statistics(df)
        
        # Create head-to-head features
        df = self._create_head_to_head_features(df)
        
        # Create recent form features
        df = self._create_form_features(df)
        
        # Create league and season features
        df = self._create_league_features(df)
        
        # Create betting odds features (if available)
        df = self._create_odds_features(df)
        
        # Create time-based features
        df = self._create_time_features(df)
        
        self.logger.info(f"Feature engineering completed. Created {len(df.columns)} features")
        return df
    
    def _create_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create basic match features"""
        
        # Home/Away advantage
        df['is_home'] = 1
        df['is_away'] = 0
        
        # Create target variable (1: Home win, 0: Draw, 2: Away win)
        df['target'] = df.apply(lambda x: 1 if x['home_score'] > x['away_score'] 
                               else (0 if x['home_score'] == x['away_score'] else 2), axis=1)
        
        # Goal difference
        df['goal_difference'] = df['home_score'] - df['away_score']
        df['total_goals'] = df['home_score'] + df['away_score']
        
        return df
    
    def _create_team_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create rolling team statistics"""
        
        features = []
        
        for team_col, opponent_col, score_col, opp_score_col in [
            ('home_team', 'away_team', 'home_score', 'away_score'),
            ('away_team', 'home_team', 'away_score', 'home_score')
        ]:
            
            team_stats = []
            
            for idx, row in df.iterrows():
                team = row[team_col]
                
                # Get previous matches for this team
                prev_matches = df[
                    (df.index < idx) & 
                    ((df['home_team'] == team) | (df['away_team'] == team))
                ].tail(self.lookback_matches)
                
                if len(prev_matches) == 0:
                    stats = self._get_default_stats()
                else:
                    stats = self._calculate_team_stats(prev_matches, team)
                
                team_stats.append(stats)
            
            # Add prefix for home/away
            prefix = 'home_' if team_col == 'home_team' else 'away_'
            team_df = pd.DataFrame(team_stats)
            team_df.columns = [f"{prefix}{col}" for col in team_df.columns]
            
            features.append(team_df)
        
        # Combine all features
        for feature_df in features:
            df = pd.concat([df, feature_df], axis=1)
        
        return df
    
    def _calculate_team_stats(self, matches: pd.DataFrame, team: str) -> Dict:
        """Calculate statistics for a specific team"""
        
        stats = {}
        
        # Separate home and away matches
        home_matches = matches[matches['home_team'] == team]
        away_matches = matches[matches['away_team'] == team]
        
        # Goals scored and conceded
        goals_scored = (
            home_matches['home_score'].sum() + 
            away_matches['away_score'].sum()
        )
        goals_conceded = (
            home_matches['away_score'].sum() + 
            away_matches['home_score'].sum()
        )
        
        total_matches = len(matches)
        
        stats['avg_goals_scored'] = goals_scored / max(total_matches, 1)
        stats['avg_goals_conceded'] = goals_conceded / max(total_matches, 1)
        stats['goal_difference'] = goals_scored - goals_conceded
        
        # Win/Draw/Loss record
        wins = len(home_matches[home_matches['home_score'] > home_matches['away_score']]) + \
               len(away_matches[away_matches['away_score'] > away_matches['home_score']])
        
        draws = len(home_matches[home_matches['home_score'] == home_matches['away_score']]) + \
                len(away_matches[away_matches['away_score'] == away_matches['home_score']])
        
        losses = total_matches - wins - draws
        
        stats['win_rate'] = wins / max(total_matches, 1)
        stats['draw_rate'] = draws / max(total_matches, 1)
        stats['loss_rate'] = losses / max(total_matches, 1)
        
        # Points (3 for win, 1 for draw, 0 for loss)
        stats['avg_points'] = (wins * 3 + draws * 1) / max(total_matches, 1)
        
        # Clean sheets and failures to score
        clean_sheets = len(home_matches[home_matches['away_score'] == 0]) + \
                      len(away_matches[away_matches['home_score'] == 0])
        
        failed_to_score = len(home_matches[home_matches['home_score'] == 0]) + \
                         len(away_matches[away_matches['away_score'] == 0])
        
        stats['clean_sheet_rate'] = clean_sheets / max(total_matches, 1)
        stats['failed_to_score_rate'] = failed_to_score / max(total_matches, 1)
        
        return stats
    
    def _get_default_stats(self) -> Dict:
        """Return default statistics for teams with no previous matches"""
        return {
            'avg_goals_scored': 1.5,
            'avg_goals_conceded': 1.5,
            'goal_difference': 0,
            'win_rate': 0.33,
            'draw_rate': 0.33,
            'loss_rate': 0.33,
            'avg_points': 1.0,
            'clean_sheet_rate': 0.2,
            'failed_to_score_rate': 0.2
        }
    
    def _create_head_to_head_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create head-to-head features between teams"""
        
        h2h_features = []
        
        for idx, row in df.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            
            # Get previous matches between these teams
            h2h_matches = df[
                (df.index < idx) & 
                (((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
                 ((df['home_team'] == away_team) & (df['away_team'] == home_team)))
            ].tail(5)
            
            if len(h2h_matches) == 0:
                h2h_stats = {
                    'h2h_home_wins': 0,
                    'h2h_draws': 0,
                    'h2h_away_wins': 0,
                    'h2h_avg_total_goals': 2.5,
                    'h2h_matches_played': 0
                }
            else:
                h2h_stats = self._calculate_h2h_stats(h2h_matches, home_team, away_team)
            
            h2h_features.append(h2h_stats)
        
        h2h_df = pd.DataFrame(h2h_features)
        return pd.concat([df, h2h_df], axis=1)
    
    def _calculate_h2h_stats(self, matches: pd.DataFrame, home_team: str, away_team: str) -> Dict:
        """Calculate head-to-head statistics"""
        
        home_wins = 0
        draws = 0
        away_wins = 0
        total_goals = 0
        
        for _, match in matches.iterrows():
            if match['home_team'] == home_team:
                if match['home_score'] > match['away_score']:
                    home_wins += 1
                elif match['home_score'] == match['away_score']:
                    draws += 1
                else:
                    away_wins += 1
            else:  # home_team is playing away in this historical match
                if match['away_score'] > match['home_score']:
                    home_wins += 1
                elif match['away_score'] == match['home_score']:
                    draws += 1
                else:
                    away_wins += 1
            
            total_goals += match['home_score'] + match['away_score']
        
        return {
            'h2h_home_wins': home_wins,
            'h2h_draws': draws,
            'h2h_away_wins': away_wins,
            'h2h_avg_total_goals': total_goals / len(matches),
            'h2h_matches_played': len(matches)
        }
    
    def _create_form_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create recent form features"""
        
        form_features = []
        
        for idx, row in df.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            
            # Get recent form for both teams
            home_form = self._get_team_form(df, idx, home_team)
            away_form = self._get_team_form(df, idx, away_team)
            
            form_stats = {
                'home_recent_points': home_form['points'],
                'home_recent_goals_scored': home_form['goals_scored'],
                'home_recent_goals_conceded': home_form['goals_conceded'],
                'away_recent_points': away_form['points'],
                'away_recent_goals_scored': away_form['goals_scored'],
                'away_recent_goals_conceded': away_form['goals_conceded']
            }
            
            form_features.append(form_stats)
        
        form_df = pd.DataFrame(form_features)
        return pd.concat([df, form_df], axis=1)
    
    def _get_team_form(self, df: pd.DataFrame, current_idx: int, team: str) -> Dict:
        """Get recent form for a team"""
        
        recent_matches = df[
            (df.index < current_idx) & 
            ((df['home_team'] == team) | (df['away_team'] == team))
        ].tail(self.form_window)
        
        if len(recent_matches) == 0:
            return {'points': 0, 'goals_scored': 0, 'goals_conceded': 0}
        
        points = 0
        goals_scored = 0
        goals_conceded = 0
        
        for _, match in recent_matches.iterrows():
            if match['home_team'] == team:
                goals_scored += match['home_score']
                goals_conceded += match['away_score']
                if match['home_score'] > match['away_score']:
                    points += 3
                elif match['home_score'] == match['away_score']:
                    points += 1
            else:
                goals_scored += match['away_score']
                goals_conceded += match['home_score']
                if match['away_score'] > match['home_score']:
                    points += 3
                elif match['away_score'] == match['home_score']:
                    points += 1
        
        return {
            'points': points,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded
        }
    
    def _create_league_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create league and season-based features"""
        
        # League encoding
        df['league_encoded'] = pd.Categorical(df['league']).codes
        
        # Season progress (if season info available)
        if 'season' in df.columns:
            df['season_encoded'] = pd.Categorical(df['season']).codes
        
        return df
    
    def _create_odds_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features from betting odds if available"""
        
        odds_columns = ['home_odds', 'draw_odds', 'away_odds']
        
        if all(col in df.columns for col in odds_columns):
            # Implied probabilities
            df['home_prob'] = 1 / df['home_odds']
            df['draw_prob'] = 1 / df['draw_odds']
            df['away_prob'] = 1 / df['away_odds']
            
            # Normalize probabilities
            total_prob = df['home_prob'] + df['draw_prob'] + df['away_prob']
            df['home_prob_norm'] = df['home_prob'] / total_prob
            df['draw_prob_norm'] = df['draw_prob'] / total_prob
            df['away_prob_norm'] = df['away_prob'] / total_prob
            
            # Bookmaker margin
            df['bookmaker_margin'] = total_prob - 1
        
        return df
    
    def _create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['day_of_week'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        return df
