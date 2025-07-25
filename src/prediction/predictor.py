import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
import json
from datetime import datetime
import os

class SportTotoPredictor:
    """
    Main prediction engine for Spor Toto matches
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.models = {}
        self.feature_columns = []
        self.logger = logging.getLogger(__name__)
        
    def load_models(self):
        """Load pre-trained models"""
        from src.models.ml_models import MLModelTrainer
        
        trainer = MLModelTrainer(self.config)
        trainer.load_models()
        self.models = trainer.models
        
        # Load feature columns
        feature_path = os.path.join(self.config.get('models_dir', 'data/models'), 'feature_columns.json')
        if os.path.exists(feature_path):
            with open(feature_path, 'r') as f:
                self.feature_columns = json.load(f)
    
    def predict_single_match(self, match_data: Dict) -> Dict:
        """
        Predict outcome for a single match
        """
        # Prepare features
        features = self._prepare_match_features(match_data)
        
        # Get predictions from all models
        predictions = {}
        probabilities = {}
        
        for model_name, model in self.models.items():
            if model_name == 'neural_network':
                probs = model.predict(features.values.reshape(1, -1))[0]
                pred = np.argmax(probs)
            else:
                pred = model.predict(features.values.reshape(1, -1))[0]
                probs = model.predict_proba(features.values.reshape(1, -1))[0]
            
            predictions[model_name] = pred
            probabilities[model_name] = probs
        
        # Ensemble prediction
        ensemble_prob = self._calculate_ensemble_probability(probabilities)
        ensemble_pred = np.argmax(ensemble_prob)
        
        # Calculate confidence
        confidence = np.max(ensemble_prob)
        
        result = {
            'prediction': ensemble_pred,  # 0: Draw, 1: Home Win, 2: Away Win
            'prediction_text': self._get_prediction_text(ensemble_pred),
            'confidence': confidence,
            'probabilities': {
                'home_win': ensemble_prob[1],
                'draw': ensemble_prob[0],
                'away_win': ensemble_prob[2]
            },
            'individual_predictions': predictions,
            'match_info': match_data
        }
        
        return result
    
    def predict_weekly_matches(self, matches: List[Dict]) -> Dict:
        """
        Predict outcomes for weekly Spor Toto matches
        """
        self.logger.info(f"Predicting outcomes for {len(matches)} matches")
        
        predictions = []
        total_confidence = 0
        
        for i, match in enumerate(matches):
            pred = self.predict_single_match(match)
            predictions.append(pred)
            total_confidence += pred['confidence']
            
            self.logger.info(
                f"Match {i+1}: {match['home_team']} vs {match['away_team']} - "
                f"Prediction: {pred['prediction_text']} (Confidence: {pred['confidence']:.2f})"
            )
        
        # Calculate expected correct predictions
        expected_correct = sum(pred['confidence'] for pred in predictions)
        
        # Probability of getting at least 12 correct
        prob_12_plus = self._calculate_success_probability(predictions)
        
        result = {
            'predictions': predictions,
            'expected_correct_predictions': expected_correct,
            'average_confidence': total_confidence / len(matches),
            'probability_12_plus_correct': prob_12_plus,
            'recommendation': self._get_recommendation(expected_correct, prob_12_plus),
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _prepare_match_features(self, match_data: Dict) -> pd.Series:
        """
        Prepare features for a single match
        """
        from src.preprocessing.feature_engineering import FeatureEngineer
        
        # This would normally involve loading historical data
        # and calculating features. For now, we'll use dummy data
        # In a real implementation, you'd:
        # 1. Load historical data for both teams
        # 2. Calculate all features using FeatureEngineer
        # 3. Return the feature vector
        
        # Dummy feature vector (replace with real feature engineering)
        features = pd.Series(np.random.random(len(self.feature_columns)), 
                           index=self.feature_columns)
        
        return features
    
    def _calculate_ensemble_probability(self, probabilities: Dict) -> np.ndarray:
        """
        Calculate weighted ensemble probability
        """
        weights = self.config.get('ensemble_weights', {
            'random_forest': 0.3,
            'xgboost': 0.4,
            'neural_network': 0.3
        })
        
        ensemble_prob = np.zeros(3)  # 3 classes: Draw, Home Win, Away Win
        total_weight = 0
        
        for model_name, prob in probabilities.items():
            weight = weights.get(model_name, 0)
            ensemble_prob += weight * np.array(prob)
            total_weight += weight
        
        if total_weight > 0:
            ensemble_prob /= total_weight
        
        return ensemble_prob
    
    def _get_prediction_text(self, prediction: int) -> str:
        """Convert numerical prediction to text"""
        prediction_map = {
            0: 'Draw (X)',
            1: 'Home Win (1)',
            2: 'Away Win (2)'
        }
        return prediction_map.get(prediction, 'Unknown')
    
    def _calculate_success_probability(self, predictions: List[Dict]) -> float:
        """
        Calculate probability of getting at least 12 out of 15 predictions correct
        using binomial distribution approximation
        """
        from scipy.stats import binom
        
        # Use average confidence as success probability for each match
        avg_confidence = np.mean([pred['confidence'] for pred in predictions])
        
        # Calculate probability of 12, 13, 14, or 15 correct predictions
        prob_12_plus = sum(
            binom.pmf(k, 15, avg_confidence) for k in range(12, 16)
        )
        
        return prob_12_plus
    
    def _get_recommendation(self, expected_correct: float, prob_12_plus: float) -> str:
        """
        Provide recommendation based on predictions
        """
        if prob_12_plus > 0.25:
            return "STRONG BET - High probability of success"
        elif prob_12_plus > 0.15:
            return "MODERATE BET - Reasonable probability of success"
        elif prob_12_plus > 0.05:
            return "WEAK BET - Low probability of success"
        else:
            return "NO BET - Very low probability of success"
    
    def save_predictions(self, predictions: Dict, filename: str = None):
        """Save predictions to file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spor_toto_predictions_{timestamp}.json"
        
        output_dir = self.config.get('output_dir', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(predictions, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Predictions saved to {filepath}")
        return filepath
    
    def load_predictions(self, filepath: str) -> Dict:
        """Load predictions from file"""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            predictions = json.load(f)
        
        return predictions
    
    def analyze_performance(self, predictions_file: str, actual_results: List[int]) -> Dict:
        """
        Analyze prediction performance against actual results
        """
        predictions = self.load_predictions(predictions_file)
        
        predicted_outcomes = [pred['prediction'] for pred in predictions['predictions']]
        
        # Calculate accuracy
        correct_predictions = sum(
            1 for pred, actual in zip(predicted_outcomes, actual_results) 
            if pred == actual
        )
        
        accuracy = correct_predictions / len(actual_results)
        success = correct_predictions >= 12
        
        analysis = {
            'total_matches': len(actual_results),
            'correct_predictions': correct_predictions,
            'accuracy': accuracy,
            'target_achieved': success,
            'expected_correct': predictions['expected_correct_predictions'],
            'prediction_error': abs(correct_predictions - predictions['expected_correct_predictions']),
            'confidence_calibration': self._analyze_confidence_calibration(
                predictions['predictions'], actual_results
            )
        }
        
        return analysis
    
    def _analyze_confidence_calibration(self, predictions: List[Dict], 
                                      actual_results: List[int]) -> Dict:
        """Analyze how well-calibrated the confidence scores are"""
        
        confidence_ranges = [(0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]
        calibration = {}
        
        for low, high in confidence_ranges:
            range_predictions = [
                (pred, actual) for pred, actual in zip(predictions, actual_results)
                if low <= pred['confidence'] < high
            ]
            
            if range_predictions:
                correct = sum(
                    1 for pred, actual in range_predictions
                    if pred['prediction'] == actual
                )
                accuracy = correct / len(range_predictions)
                avg_confidence = np.mean([pred['confidence'] for pred, _ in range_predictions])
                
                calibration[f"{low}-{high}"] = {
                    'count': len(range_predictions),
                    'accuracy': accuracy,
                    'avg_confidence': avg_confidence,
                    'calibration_error': abs(accuracy - avg_confidence)
                }
        
        return calibration
