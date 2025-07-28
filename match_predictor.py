import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import joblib
import warnings
warnings.filterwarnings('ignore')

class MatchPredictor:
    """
    Machine Learning model for predicting football match outcomes (1-X-2).
    Uses RandomForest and XGBoost with ensemble predictions.
    """
    
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
        self.feature_importance = None
        
    def prepare_features(self, df):
        """Prepare features for machine learning"""
        # Select numeric features for training
        feature_columns = [
            'home_odds', 'draw_odds', 'away_odds',
            'home_prob', 'draw_prob', 'away_prob',
            'home_form_points', 'home_wins', 'home_draws', 'home_losses',
            'home_goals_for', 'home_goals_against', 'home_matches_played',
            'away_form_points', 'away_wins', 'away_draws', 'away_losses',
            'away_goals_for', 'away_goals_against', 'away_matches_played',
            'h2h_home_wins', 'h2h_draws', 'h2h_away_wins', 'h2h_matches', 'h2h_avg_goals',
            'home_shots', 'away_shots', 'home_shots_target', 'away_shots_target',
            'league_strength'
        ]
        
        # Filter existing columns
        available_features = [col for col in feature_columns if col in df.columns]
        
        # Add derived features
        df_features = df[available_features].copy()
        
        # Goal difference features
        if 'home_goals_for' in df.columns and 'home_goals_against' in df.columns:
            df_features['home_goal_diff'] = df['home_goals_for'] - df['home_goals_against']
            df_features['away_goal_diff'] = df['away_goals_for'] - df['away_goals_against']
        
        # Form comparison
        if 'home_form_points' in df.columns and 'away_form_points' in df.columns:
            df_features['form_difference'] = df['home_form_points'] - df['away_form_points']
        
        # Odds-based features
        if all(col in df.columns for col in ['home_odds', 'draw_odds', 'away_odds']):
            df_features['favorite'] = np.where(df['home_odds'] < df['away_odds'], 1, 
                                             np.where(df['home_odds'] > df['away_odds'], -1, 0))
            df_features['odds_variance'] = df[['home_odds', 'draw_odds', 'away_odds']].var(axis=1)
        
        # H2H win percentage
        if 'h2h_matches' in df.columns and df['h2h_matches'].max() > 0:
            df_features['h2h_home_win_pct'] = df['h2h_home_wins'] / np.maximum(df['h2h_matches'], 1)
            df_features['h2h_away_win_pct'] = df['h2h_away_wins'] / np.maximum(df['h2h_matches'], 1)
        
        # Fill NaN values
        df_features = df_features.fillna(0)
        
        return df_features
    
    def train_models(self, features_df, test_size=0.2, random_state=42):
        """Train both RandomForest and XGBoost models"""
        print("Preparing training data...")
        
        # Prepare features and target
        X = self.prepare_features(features_df)
        y = features_df['result_encoded']
        
        # Remove rows where we couldn't calculate proper features
        mask = y.notna() & (X.sum(axis=1) != 0)
        X = X[mask]
        y = y[mask]
        
        print(f"Training on {len(X)} samples with {len(X.columns)} features")
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("Training RandomForest model...")
        # Train RandomForest with hyperparameter tuning
        rf_params = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        rf_grid = GridSearchCV(
            RandomForestClassifier(random_state=random_state, class_weight='balanced'),
            rf_params, cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )
        rf_grid.fit(X_train, y_train)
        self.rf_model = rf_grid.best_estimator_
        
        print(f"Best RF parameters: {rf_grid.best_params_}")
        
        print("Training XGBoost model...")
        # Train XGBoost with hyperparameter tuning
        xgb_params = {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 6, 9],
            'learning_rate': [0.01, 0.1, 0.2],
            'subsample': [0.8, 0.9, 1.0]
        }
        
        xgb_grid = GridSearchCV(
            xgb.XGBClassifier(random_state=random_state, eval_metric='mlogloss'),
            xgb_params, cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )
        xgb_grid.fit(X_train_scaled, y_train)
        self.xgb_model = xgb_grid.best_estimator_
        
        print(f"Best XGB parameters: {xgb_grid.best_params_}")
        
        # Evaluate models
        print("\nEvaluating models...")
        
        # RandomForest evaluation
        rf_pred = self.rf_model.predict(X_test)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        print(f"RandomForest Test Accuracy: {rf_accuracy:.4f}")
        
        # XGBoost evaluation
        xgb_pred = self.xgb_model.predict(X_test_scaled)
        xgb_accuracy = accuracy_score(y_test, xgb_pred)
        print(f"XGBoost Test Accuracy: {xgb_accuracy:.4f}")
        
        # Ensemble prediction
        rf_proba = self.rf_model.predict_proba(X_test)
        xgb_proba = self.xgb_model.predict_proba(X_test_scaled)
        ensemble_proba = (rf_proba + xgb_proba) / 2
        ensemble_pred = np.argmax(ensemble_proba, axis=1)
        ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
        print(f"Ensemble Test Accuracy: {ensemble_accuracy:.4f}")
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'rf_importance': self.rf_model.feature_importances_,
            'xgb_importance': self.xgb_model.feature_importances_
        })
        self.feature_importance['avg_importance'] = (
            self.feature_importance['rf_importance'] + self.feature_importance['xgb_importance']
        ) / 2
        self.feature_importance = self.feature_importance.sort_values('avg_importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(self.feature_importance.head(10)[['feature', 'avg_importance']])
        
        # Detailed classification report
        print("\nDetailed Classification Report (Ensemble):")
        target_names = ['Home Win (1)', 'Draw (X)', 'Away Win (2)']
        print(classification_report(y_test, ensemble_pred, target_names=target_names))
        
        # Confusion Matrix
        print("\nConfusion Matrix (Ensemble):")
        cm = confusion_matrix(y_test, ensemble_pred)
        print("Predicted:  H    D    A")
        for i, (actual, row) in enumerate(zip(target_names, cm)):
            print(f"Actual {actual[0]}: {row[0]:4d} {row[1]:4d} {row[2]:4d}")
        
        self.is_trained = True
        return {
            'rf_accuracy': rf_accuracy,
            'xgb_accuracy': xgb_accuracy,
            'ensemble_accuracy': ensemble_accuracy,
            'feature_importance': self.feature_importance
        }
    
    def predict_match(self, match_features):
        """Predict single match outcome with probabilities"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_models() first.")
        
        # Prepare features
        X = self.prepare_features(pd.DataFrame([match_features]))
        
        if len(X.columns) != len(self.feature_names):
            # Align features with training features
            for feature in self.feature_names:
                if feature not in X.columns:
                    X[feature] = 0
            X = X[self.feature_names]
        
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from both models
        rf_proba = self.rf_model.predict_proba(X)[0]
        xgb_proba = self.xgb_model.predict_proba(X_scaled)[0]
        
        # Ensemble prediction
        ensemble_proba = (rf_proba + xgb_proba) / 2
        
        # Convert to percentages
        probabilities = {
            'home_win': ensemble_proba[0] * 100,
            'draw': ensemble_proba[1] * 100,
            'away_win': ensemble_proba[2] * 100
        }
        
        # Determine prediction
        max_prob_idx = np.argmax(ensemble_proba)
        outcomes = ['1', 'X', '2']
        predicted_outcome = outcomes[max_prob_idx]
        confidence = ensemble_proba[max_prob_idx] * 100
        
        return {
            'prediction': predicted_outcome,
            'confidence': confidence,
            'probabilities': probabilities,
            'rf_probabilities': {
                'home_win': rf_proba[0] * 100,
                'draw': rf_proba[1] * 100,
                'away_win': rf_proba[2] * 100
            },
            'xgb_probabilities': {
                'home_win': xgb_proba[0] * 100,
                'draw': xgb_proba[1] * 100,
                'away_win': xgb_proba[2] * 100
            }
        }
    
    def calculate_value_bets(self, match_features, current_odds):
        """Calculate expected value for each outcome"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_models() first.")
        
        prediction = self.predict_match(match_features)
        probabilities = prediction['probabilities']
        
        # Calculate expected value for each outcome
        ev_home = (probabilities['home_win'] / 100) * current_odds['home'] - 1
        ev_draw = (probabilities['draw'] / 100) * current_odds['draw'] - 1
        ev_away = (probabilities['away_win'] / 100) * current_odds['away'] - 1
        
        expected_values = {
            'home': ev_home,
            'draw': ev_draw,
            'away': ev_away
        }
        
        # Find value bets (positive expected value)
        value_bets = {k: v for k, v in expected_values.items() if v > 0}
        
        return {
            'expected_values': expected_values,
            'value_bets': value_bets,
            'prediction': prediction
        }
    
    def save_models(self, filepath_prefix='model'):
        """Save trained models"""
        if not self.is_trained:
            raise ValueError("No trained models to save.")
        
        joblib.dump(self.rf_model, f'{filepath_prefix}_rf.joblib')
        joblib.dump(self.xgb_model, f'{filepath_prefix}_xgb.joblib')
        joblib.dump(self.scaler, f'{filepath_prefix}_scaler.joblib')
        joblib.dump(self.feature_names, f'{filepath_prefix}_features.joblib')
        
        print(f"Models saved with prefix: {filepath_prefix}")
    
    def load_models(self, filepath_prefix='model'):
        """Load pre-trained models"""
        try:
            self.rf_model = joblib.load(f'{filepath_prefix}_rf.joblib')
            self.xgb_model = joblib.load(f'{filepath_prefix}_xgb.joblib')
            self.scaler = joblib.load(f'{filepath_prefix}_scaler.joblib')
            self.feature_names = joblib.load(f'{filepath_prefix}_features.joblib')
            self.is_trained = True
            print(f"Models loaded successfully from: {filepath_prefix}")
        except FileNotFoundError as e:
            print(f"Error loading models: {e}")
            raise
