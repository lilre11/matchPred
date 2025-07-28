import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SporTotoPredictor:
    """
    Spor Toto prediction system that combines ML predictions with betting odds analysis.
    Outputs in the required format: m1(1-2), m2(2), m3(1-x), etc.
    """
    
    def __init__(self, match_predictor, data_processor):
        self.predictor = match_predictor
        self.data_processor = data_processor
        
    def format_spor_toto_prediction(self, match_idx, prediction_result, confidence_threshold=60):
        """
        Format prediction in Spor Toto style
        - High confidence (>70%): single outcome e.g., m1(1), m2(X), m3(2)
        - Medium confidence (50-70%): two outcomes e.g., m1(1-X), m2(X-2)
        - Low confidence (<50%): broad prediction e.g., m1(1-X-2)
        """
        probabilities = prediction_result['probabilities']
        max_prob = max(probabilities.values())
        
        # Sort outcomes by probability
        sorted_outcomes = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        
        # Map outcome names to Spor Toto format
        outcome_map = {
            'home_win': '1',
            'draw': 'X', 
            'away_win': '2'
        }
        
        # Decision logic based on confidence and probability distribution
        if max_prob >= 70:
            # High confidence - single outcome
            best_outcome = sorted_outcomes[0][0]
            result = outcome_map[best_outcome]
        elif max_prob >= confidence_threshold:
            # Medium confidence - top 2 outcomes
            top_two = [outcome_map[outcome[0]] for outcome in sorted_outcomes[:2]]
            result = '-'.join(sorted(top_two))
        else:
            # Low confidence - check for clear patterns
            home_prob = probabilities['home_win']
            draw_prob = probabilities['draw']
            away_prob = probabilities['away_win']
            
            # If home and away are close, but draw is low
            if abs(home_prob - away_prob) < 10 and draw_prob < 25:
                result = '1-2'
            # If one team clearly favored over the other, but draw possible
            elif home_prob > away_prob + 15:
                result = '1-X'
            elif away_prob > home_prob + 15:
                result = 'X-2'
            else:
                # Very uncertain - all outcomes possible
                result = '1-X-2'
        
        return f"m{match_idx}({result})"
    
    def analyze_value_and_risk(self, prediction_result, current_odds, risk_tolerance='medium'):
        """
        Analyze betting value and adjust prediction based on risk tolerance
        """
        probabilities = prediction_result['probabilities']
        
        # Calculate implied probabilities from odds
        implied_home = 100 / current_odds['home']
        implied_draw = 100 / current_odds['draw']
        implied_away = 100 / current_odds['away']
        
        # Calculate value (our probability vs market probability)
        value_home = probabilities['home_win'] - implied_home
        value_draw = probabilities['draw'] - implied_draw
        value_away = probabilities['away_win'] - implied_away
        
        values = {
            'home_win': value_home,
            'draw': value_draw,
            'away_win': value_away
        }
        
        # Risk tolerance settings
        risk_settings = {
            'conservative': {'min_value': 10, 'min_confidence': 65},
            'medium': {'min_value': 5, 'min_confidence': 55},
            'aggressive': {'min_value': 2, 'min_confidence': 45}
        }
        
        settings = risk_settings[risk_tolerance]
        
        # Filter outcomes with positive value and sufficient confidence
        good_bets = []
        for outcome, value in values.items():
            confidence = probabilities[outcome]
            if value >= settings['min_value'] and confidence >= settings['min_confidence']:
                good_bets.append((outcome, value, confidence))
        
        return {
            'values': values,
            'good_bets': good_bets,
            'recommended_outcomes': [bet[0] for bet in good_bets]
        }
    
    def predict_matches(self, upcoming_matches, risk_tolerance='medium'):
        """
        Predict multiple matches with Spor Toto formatting
        
        upcoming_matches format:
        [
            {
                'home_team': 'Galatasaray',
                'away_team': 'Fenerbahce', 
                'league': 'T1',
                'current_odds': {'home': 2.1, 'draw': 3.2, 'away': 3.4},
                'date': '2024-12-01'  # optional
            },
            ...
        ]
        """
        predictions = []
        
        print(f"🔮 Spor Toto Predictions ({risk_tolerance.title()} Risk)")
        print("=" * 60)
        
        for idx, match in enumerate(upcoming_matches, 1):
            try:
                # Prepare match features
                match_features = self.prepare_match_features(match)
                
                # Get ML prediction
                prediction_result = self.predictor.predict_match(match_features)
                
                # Analyze value if odds provided
                value_analysis = None
                if 'current_odds' in match:
                    value_analysis = self.analyze_value_and_risk(
                        prediction_result, match['current_odds'], risk_tolerance
                    )
                    
                    # Adjust prediction based on value analysis
                    if value_analysis['recommended_outcomes']:
                        # Override with value-based recommendation
                        adjusted_probabilities = prediction_result['probabilities'].copy()
                        for outcome in value_analysis['recommended_outcomes']:
                            # Boost probability of value bets
                            adjusted_probabilities[outcome] *= 1.2
                        
                        # Renormalize
                        total = sum(adjusted_probabilities.values())
                        adjusted_probabilities = {k: v/total*100 for k, v in adjusted_probabilities.items()}
                        prediction_result['probabilities'] = adjusted_probabilities
                
                # Format Spor Toto prediction
                spor_toto_format = self.format_spor_toto_prediction(idx, prediction_result)
                
                # Create detailed result
                result = {
                    'match_number': idx,
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'spor_toto_prediction': spor_toto_format,
                    'ml_prediction': prediction_result,
                    'value_analysis': value_analysis
                }
                
                predictions.append(result)
                
                # Print formatted output
                print(f"🏆 {match['home_team']} vs {match['away_team']}")
                print(f"   Prediction: {spor_toto_format}")
                print(f"   Confidence: {prediction_result['confidence']:.1f}%")
                print(f"   Probabilities: 1:{prediction_result['probabilities']['home_win']:.1f}% "
                      f"X:{prediction_result['probabilities']['draw']:.1f}% "
                      f"2:{prediction_result['probabilities']['away_win']:.1f}%")
                
                if value_analysis and value_analysis['good_bets']:
                    print(f"   💰 Value Bets: {', '.join([bet[0] for bet in value_analysis['good_bets']])}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error predicting {match['home_team']} vs {match['away_team']}: {e}")
                continue
        
        return predictions
    
    def prepare_match_features(self, match_info):
        """Prepare features for a single upcoming match"""
        
        # Get current date or use provided date
        match_date = pd.to_datetime(match_info.get('date', datetime.now()))
        
        # Calculate team forms
        home_form = self.data_processor.calculate_team_form(
            match_info['home_team'], match_date
        )
        away_form = self.data_processor.calculate_team_form(
            match_info['away_team'], match_date
        )
        
        # Calculate head-to-head
        h2h = self.data_processor.calculate_head_to_head(
            match_info['home_team'], match_info['away_team'], match_date
        )
        
        # Base features
        features = {
            'home_team': match_info['home_team'],
            'away_team': match_info['away_team'],
            'league': match_info['league'],
            'date': match_date
        }
        
        # Add odds if provided
        if 'current_odds' in match_info:
            odds = match_info['current_odds']
            features.update({
                'home_odds': odds['home'],
                'draw_odds': odds['draw'],
                'away_odds': odds['away']
            })
            
            # Calculate implied probabilities
            total_prob = (1/odds['home']) + (1/odds['draw']) + (1/odds['away'])
            features.update({
                'home_prob': (1/odds['home']) / total_prob,
                'draw_prob': (1/odds['draw']) / total_prob,
                'away_prob': (1/odds['away']) / total_prob
            })
        else:
            # Use average odds if not provided
            features.update({
                'home_odds': 2.5, 'draw_odds': 3.2, 'away_odds': 2.8,
                'home_prob': 0.33, 'draw_prob': 0.33, 'away_prob': 0.33
            })
        
        # Add form features
        for key, value in home_form.items():
            features[f'home_{key}'] = value
        for key, value in away_form.items():
            features[f'away_{key}'] = value
            
        # Add h2h features
        features.update(h2h)
        
        # Add league strength
        features['league_strength'] = self.data_processor.get_league_strength(match_info['league'])
        
        # Add default values for missing statistical features
        features.update({
            'home_shots': 0, 'away_shots': 0,
            'home_shots_target': 0, 'away_shots_target': 0
        })
        
        return features
    
    def generate_weekly_predictions(self, matches, output_file=None):
        """Generate weekly Spor Toto predictions with summary"""
        
        # Predict all matches
        predictions = self.predict_matches(matches)
        
        # Generate summary
        print("\n" + "="*60)
        print("📋 WEEKLY SPOR TOTO SUMMARY")
        print("="*60)
        
        # Extract just the predictions for easy copying
        spor_toto_predictions = []
        for pred in predictions:
            spor_toto_predictions.append(pred['spor_toto_prediction'])
        
        # Print in coupon format
        print("🎫 COUPON FORMAT:")
        for prediction in spor_toto_predictions:
            print(f"   {prediction}")
        
        # Statistics
        single_predictions = sum(1 for p in spor_toto_predictions if '(' in p and '-' not in p.split('(')[1])
        double_predictions = sum(1 for p in spor_toto_predictions if p.count('-') == 1)
        triple_predictions = sum(1 for p in spor_toto_predictions if p.count('-') == 2)
        
        print(f"\n📊 PREDICTION BREAKDOWN:")
        print(f"   Single outcomes: {single_predictions}")
        print(f"   Double outcomes: {double_predictions}")
        print(f"   Triple outcomes: {triple_predictions}")
        print(f"   Total matches: {len(predictions)}")
        
        # Calculate theoretical combinations
        total_combinations = 1
        for pred in spor_toto_predictions:
            outcome_count = pred.split('(')[1].count('-') + 1
            total_combinations *= outcome_count
        
        print(f"   Total combinations: {total_combinations:,}")
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("SPOR TOTO PREDICTIONS\n")
                f.write("="*30 + "\n\n")
                
                for pred in predictions:
                    f.write(f"{pred['home_team']} vs {pred['away_team']}\n")
                    f.write(f"{pred['spor_toto_prediction']}\n")
                    f.write(f"Confidence: {pred['ml_prediction']['confidence']:.1f}%\n\n")
                
                f.write("\nCOUPON FORMAT:\n")
                for prediction in spor_toto_predictions:
                    f.write(f"{prediction}\n")
            
            print(f"\n💾 Predictions saved to: {output_file}")
        
        return {
            'predictions': predictions,
            'spor_toto_format': spor_toto_predictions,
            'statistics': {
                'single_predictions': single_predictions,
                'double_predictions': double_predictions,
                'triple_predictions': triple_predictions,
                'total_combinations': total_combinations
            }
        }
