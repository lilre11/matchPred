#!/usr/bin/env python3
"""
🎮 Interactive Spor Toto Prediction Interface
Easy-to-use interface for making match predictions
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

from data_processor import DataProcessor
from match_predictor import MatchPredictor
from spor_toto_predictor import SporTotoPredictor

class PredictionInterface:
    def __init__(self):
        self.processor = None
        self.predictor = None
        self.spor_toto = None
        self.is_initialized = False
        
    def initialize(self):
        """Initialize the prediction system"""
        print("🚀 Initializing prediction system...")
        
        try:
            # Load data processor
            self.processor = DataProcessor(data_path='csvs/')
            self.processor.load_data()
            self.processor.clean_data()
            
            # Load trained models
            self.predictor = MatchPredictor()
            if os.path.exists('models/spor_toto_model_rf.joblib'):
                self.predictor.load_models('models/spor_toto_model')
                print("✅ Loaded pre-trained models")
            else:
                print("❌ No pre-trained models found. Please run main.py first.")
                return False
            
            # Initialize Spor Toto predictor
            self.spor_toto = SporTotoPredictor(self.predictor, self.processor)
            
            self.is_initialized = True
            print("✅ System initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing system: {e}")
            return False
    
    def predict_single_match(self, home_team, away_team, league='T1', odds=None):
        """Predict a single match"""
        if not self.is_initialized:
            if not self.initialize():
                return None
        
        match_info = {
            'home_team': home_team,
            'away_team': away_team,
            'league': league,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        if odds:
            match_info['current_odds'] = odds
        
        predictions = self.spor_toto.predict_matches([match_info])
        return predictions[0] if predictions else None
    
    def predict_from_text(self, match_text, league='T1', odds_text=None):
        """
        Predict from text input
        
        Examples:
        - "Galatasaray vs Fenerbahce"
        - "Real Madrid - Barcelona"
        """
        # Parse match text
        separators = [' vs ', ' - ', ' x ', ' v ']
        teams = None
        
        for sep in separators:
            if sep in match_text:
                teams = match_text.split(sep)
                break
        
        if not teams or len(teams) != 2:
            print("❌ Could not parse match. Use format: 'Team1 vs Team2'")
            return None
        
        home_team = teams[0].strip()
        away_team = teams[1].strip()
        
        # Parse odds if provided
        odds = None
        if odds_text:
            try:
                # Format: "2.1,3.2,3.4" (home,draw,away)
                odds_values = [float(x.strip()) for x in odds_text.split(',')]
                if len(odds_values) == 3:
                    odds = {
                        'home': odds_values[0],
                        'draw': odds_values[1], 
                        'away': odds_values[2]
                    }
            except:
                print("⚠️ Could not parse odds. Using default values.")
        
        return self.predict_single_match(home_team, away_team, league, odds)
    
    def interactive_mode(self):
        """Interactive command-line interface"""
        if not self.initialize():
            return
        
        print("\n🎮 INTERACTIVE SPOR TOTO PREDICTOR")
        print("=" * 50)
        print("Commands:")
        print("  predict <match>     - Predict a match")
        print("  odds <h,d,a>        - Set odds for next prediction")
        print("  league <code>       - Set league (T1, SP1, pl2425, etc.)")
        print("  batch               - Predict multiple matches")
        print("  help                - Show this help")
        print("  quit                - Exit")
        print("\nExamples:")
        print("  predict Galatasaray vs Fenerbahce")
        print("  odds 2.1,3.2,3.4")
        print("  league SP1")
        print()
        
        current_league = 'T1'
        current_odds = None
        
        while True:
            try:
                command = input("⚽ Enter command: ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif command.lower() in ['help', 'h']:
                    print("\n📖 HELP:")
                    print("predict <team1> vs <team2>  - Get match prediction")
                    print("odds <home>,<draw>,<away>    - Set betting odds")
                    print("league <code>               - Set league code")
                    print("batch                       - Enter multiple matches")
                    print("clear                       - Clear current odds")
                    print()
                
                elif command.lower().startswith('predict '):
                    match_text = command[8:].strip()
                    
                    print(f"\n🔮 Predicting: {match_text}")
                    print(f"   League: {current_league}")
                    if current_odds:
                        print(f"   Odds: {current_odds}")
                    print()
                    
                    prediction = self.predict_from_text(
                        match_text, current_league, 
                        f"{current_odds['home']},{current_odds['draw']},{current_odds['away']}" 
                        if current_odds else None
                    )
                    
                    if prediction:
                        self.print_prediction_summary(prediction)
                    
                    # Clear odds after use
                    current_odds = None
                
                elif command.lower().startswith('odds '):
                    odds_text = command[5:].strip()
                    try:
                        odds_values = [float(x.strip()) for x in odds_text.split(',')]
                        if len(odds_values) == 3:
                            current_odds = {
                                'home': odds_values[0],
                                'draw': odds_values[1],
                                'away': odds_values[2]
                            }
                            print(f"✅ Odds set: Home={current_odds['home']}, Draw={current_odds['draw']}, Away={current_odds['away']}")
                        else:
                            print("❌ Please provide 3 odds values: home,draw,away")
                    except:
                        print("❌ Invalid odds format. Use: 2.1,3.2,3.4")
                
                elif command.lower().startswith('league '):
                    league_code = command[7:].strip().upper()
                    current_league = league_code
                    print(f"✅ League set to: {current_league}")
                
                elif command.lower() == 'clear':
                    current_odds = None
                    print("✅ Odds cleared")
                
                elif command.lower() == 'batch':
                    self.batch_prediction_mode(current_league)
                
                elif command.strip() == '':
                    continue
                
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def batch_prediction_mode(self, default_league='T1'):
        """Batch prediction mode for multiple matches"""
        print("\n📝 BATCH PREDICTION MODE")
        print("-" * 30)
        print("Enter matches one per line in format:")
        print("Team1 vs Team2 [league] [odds:h,d,a]")
        print("Examples:")
        print("  Galatasaray vs Fenerbahce")
        print("  Real Madrid vs Barcelona SP1 odds:2.5,3.3,2.7")
        print("  Man United vs Arsenal pl2425")
        print("Enter empty line to finish.")
        print()
        
        matches = []
        while True:
            line = input(f"Match {len(matches)+1}: ").strip()
            if not line:
                break
            
            # Parse line
            parts = line.split()
            match_part = []
            league = default_league
            odds = None
            
            for part in parts:
                if part.startswith('odds:'):
                    try:
                        odds_str = part[5:]
                        odds_values = [float(x) for x in odds_str.split(',')]
                        if len(odds_values) == 3:
                            odds = {'home': odds_values[0], 'draw': odds_values[1], 'away': odds_values[2]}
                    except:
                        print(f"⚠️ Invalid odds format in line: {line}")
                elif part.upper() in ['T1', 'SP1', 'PL2425', 'B1', 'IT2425', 'F1']:
                    league = part.upper()
                else:
                    match_part.append(part)
            
            # Reconstruct match text
            match_text = ' '.join(match_part)
            
            # Parse teams
            separators = [' vs ', ' - ', ' x ', ' v ']
            teams = None
            for sep in separators:
                if sep in match_text:
                    teams = match_text.split(sep)
                    break
            
            if teams and len(teams) == 2:
                match_info = {
                    'home_team': teams[0].strip(),
                    'away_team': teams[1].strip(),
                    'league': league,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
                if odds:
                    match_info['current_odds'] = odds
                
                matches.append(match_info)
                print(f"✅ Added: {match_info['home_team']} vs {match_info['away_team']} ({league})")
            else:
                print(f"❌ Could not parse: {line}")
        
        if matches:
            print(f"\n🔮 Predicting {len(matches)} matches...")
            predictions = self.spor_toto.predict_matches(matches)
            
            # Generate summary
            self.spor_toto.generate_weekly_predictions(matches, 'predictions/batch_predictions.txt')
        else:
            print("No valid matches entered.")
    
    def print_prediction_summary(self, prediction):
        """Print a formatted prediction summary"""
        print(f"🎯 {prediction['spor_toto_prediction']}")
        print(f"   Confidence: {prediction['ml_prediction']['confidence']:.1f}%")
        
        probs = prediction['ml_prediction']['probabilities']
        print(f"   Probabilities: 1:{probs['home_win']:.1f}% X:{probs['draw']:.1f}% 2:{probs['away_win']:.1f}%")
        
        if prediction['value_analysis'] and prediction['value_analysis']['good_bets']:
            value_bets = [bet[0].replace('_win', '').replace('home', '1').replace('away', '2').replace('draw', 'X') 
                         for bet in prediction['value_analysis']['good_bets']]
            print(f"   💰 Value Bets: {', '.join(value_bets)}")
        
        print()

def main():
    """Main function for interactive interface"""
    interface = PredictionInterface()
    
    print("🏆 SPOR TOTO PREDICTION INTERFACE")
    print("=" * 50)
    
    # Quick prediction mode
    print("\n🚀 Quick Start Options:")
    print("1. Interactive mode (recommended)")
    print("2. Single prediction")
    print("3. Exit")
    
    try:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            interface.interactive_mode()
        
        elif choice == '2':
            match = input("Enter match (Team1 vs Team2): ").strip()
            league = input("Enter league code (T1, SP1, pl2425, etc.) [T1]: ").strip() or 'T1'
            odds_input = input("Enter odds (home,draw,away) [optional]: ").strip()
            
            odds = None
            if odds_input:
                try:
                    odds_values = [float(x.strip()) for x in odds_input.split(',')]
                    if len(odds_values) == 3:
                        odds = {'home': odds_values[0], 'draw': odds_values[1], 'away': odds_values[2]}
                except:
                    print("⚠️ Invalid odds format, using defaults")
            
            prediction = interface.predict_from_text(match, league.upper(), 
                                                   f"{odds['home']},{odds['draw']},{odds['away']}" if odds else None)
            if prediction:
                interface.print_prediction_summary(prediction)
        
        elif choice == '3':
            print("👋 Goodbye!")
        
        else:
            print("❌ Invalid option")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
