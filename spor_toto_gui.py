#!/usr/bin/env python3
"""
Spor Toto Match Predictor - Desktop GUI Application
Standalone executable for predicting 15 matches for Turkish Spor Toto
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import threading
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from data_processor import DataProcessor
    from match_predictor import MatchPredictor
    from spor_toto_predictor import SporTotoPredictor
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required files are in the same directory")

class SporTotoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏆 Spor Toto Match Predictor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize prediction system
        self.processor = None
        self.predictor = None
        self.spor_toto = None
        self.system_loaded = False
        
        # Store match entries
        self.match_entries = []
        
        # League mapping
        self.league_mapping = {
            "🇹🇷 Turkish Super League": "T1",
            "🇪🇸 Spanish La Liga": "SP1", 
            "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League": "pl2425",
            "🇩🇪 German Bundesliga": "bundes2425",
            "🇮🇹 Italian Serie A": "it2425",
            "🇫🇷 French Ligue 1": "F1",
            "🇵🇹 Portuguese Liga": "P1",
            "🇳🇱 Dutch Eredivisie": "N1",
            "🇬🇷 Greek Super League": "G1",
            "🇧🇪 Belgian League": "B1",
            "🇨🇭 Swiss League": "SWZ",
            "🇳🇴 Norwegian League": "NOR"
        }
        
        self.setup_ui()
        
        # Load system in background
        self.load_system_async()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2196F3', height=80)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🏆 Spor Toto Match Predictor",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#2196F3'
        )
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(
            title_frame,
            text="AI-Powered Football Match Predictions for Turkish Spor Toto",
            font=('Arial', 12),
            fg='white',
            bg='#2196F3'
        )
        subtitle_label.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Match input
        left_frame = tk.LabelFrame(main_frame, text="📝 Match Input", font=('Arial', 14, 'bold'), bg='#f0f0f0')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.setup_match_input(left_frame)
        
        # Right panel - Results and controls
        right_frame = tk.LabelFrame(main_frame, text="🎯 Predictions & Controls", font=('Arial', 14, 'bold'), bg='#f0f0f0')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.setup_controls_and_results(right_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Loading prediction system...")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg='#e0e0e0')
        status_bar.pack(side='bottom', fill='x')
    
    def setup_match_input(self, parent):
        """Setup match input section"""
        
        # Instructions
        instruction_label = tk.Label(
            parent,
            text="Enter 15 matches for Spor Toto prediction:",
            font=('Arial', 12),
            bg='#f0f0f0'
        )
        instruction_label.pack(pady=5)
        
        # Input method selection
        input_frame = tk.Frame(parent, bg='#f0f0f0')
        input_frame.pack(fill='x', pady=5)
        
        self.input_method = tk.StringVar(value="manual")
        
        manual_radio = tk.Radiobutton(
            input_frame,
            text="✏️ Manual Entry",
            variable=self.input_method,
            value="manual",
            command=self.toggle_input_method,
            bg='#f0f0f0',
            font=('Arial', 10)
        )
        manual_radio.pack(side='left', padx=10)
        
        paste_radio = tk.Radiobutton(
            input_frame,
            text="📋 Paste All",
            variable=self.input_method,
            value="paste",
            command=self.toggle_input_method,
            bg='#f0f0f0',
            font=('Arial', 10)
        )
        paste_radio.pack(side='left', padx=10)
        
        file_radio = tk.Radiobutton(
            input_frame,
            text="📁 Load File",
            variable=self.input_method,
            value="file",
            command=self.toggle_input_method,
            bg='#f0f0f0',
            font=('Arial', 10)
        )
        file_radio.pack(side='left', padx=10)
        
        # Container for different input methods
        self.input_container = tk.Frame(parent, bg='#f0f0f0')
        self.input_container.pack(fill='both', expand=True, pady=5)
        
        self.setup_manual_input()
        self.setup_paste_input()
        self.setup_file_input()
        
        # Initially show manual input
        self.toggle_input_method()
    
    def setup_manual_input(self):
        """Setup manual match entry"""
        self.manual_frame = tk.Frame(self.input_container, bg='#f0f0f0')
        
        # Scrollable frame for matches
        canvas = tk.Canvas(self.manual_frame, bg='#f0f0f0', height=400)
        scrollbar = ttk.Scrollbar(self.manual_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create 15 match entry rows
        self.match_entries = []
        for i in range(15):
            self.create_match_entry_row(i)
        
        # Quick fill buttons
        button_frame = tk.Frame(self.manual_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear All",
            command=self.clear_all_matches,
            bg='#f44336',
            fg='white',
            font=('Arial', 10)
        )
        clear_btn.pack(side='left', padx=5)
        
        sample_btn = tk.Button(
            button_frame,
            text="📝 Fill Sample",
            command=self.fill_sample_matches,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10)
        )
        sample_btn.pack(side='left', padx=5)
    
    def setup_paste_input(self):
        """Setup paste all matches input"""
        self.paste_frame = tk.Frame(self.input_container, bg='#f0f0f0')
        
        paste_label = tk.Label(
            self.paste_frame,
            text="Paste all 15 matches (one per line):\nFormat: Home Team vs Away Team",
            font=('Arial', 10),
            bg='#f0f0f0',
            justify='left'
        )
        paste_label.pack(anchor='w', pady=5)
        
        self.paste_text = scrolledtext.ScrolledText(
            self.paste_frame,
            height=20,
            width=50,
            font=('Consolas', 10)
        )
        self.paste_text.pack(fill='both', expand=True, pady=5)
        
        paste_button_frame = tk.Frame(self.paste_frame, bg='#f0f0f0')
        paste_button_frame.pack(fill='x', pady=5)
        
        parse_btn = tk.Button(
            paste_button_frame,
            text="📋 Parse Matches",
            command=self.parse_pasted_matches,
            bg='#2196F3',
            fg='white',
            font=('Arial', 10)
        )
        parse_btn.pack(side='left', padx=5)
        
        clear_paste_btn = tk.Button(
            paste_button_frame,
            text="🗑️ Clear",
            command=lambda: self.paste_text.delete(1.0, tk.END),
            bg='#f44336',
            fg='white',
            font=('Arial', 10)
        )
        clear_paste_btn.pack(side='left', padx=5)
    
    def setup_file_input(self):
        """Setup file input"""
        self.file_frame = tk.Frame(self.input_container, bg='#f0f0f0')
        
        file_label = tk.Label(
            self.file_frame,
            text="Load matches from file (CSV, TXT, or JSON):",
            font=('Arial', 10),
            bg='#f0f0f0'
        )
        file_label.pack(anchor='w', pady=5)
        
        file_button_frame = tk.Frame(self.file_frame, bg='#f0f0f0')
        file_button_frame.pack(fill='x', pady=10)
        
        load_file_btn = tk.Button(
            file_button_frame,
            text="📁 Load File",
            command=self.load_matches_from_file,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12)
        )
        load_file_btn.pack(pady=10)
        
        # File info display
        self.file_info_text = scrolledtext.ScrolledText(
            self.file_frame,
            height=15,
            width=50,
            font=('Consolas', 9),
            state='disabled'
        )
        self.file_info_text.pack(fill='both', expand=True, pady=5)
    
    def setup_controls_and_results(self, parent):
        """Setup controls and results section"""
        
        # Controls
        controls_frame = tk.LabelFrame(parent, text="🎮 Settings", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        controls_frame.pack(fill='x', pady=5)
        
        # Risk level
        risk_frame = tk.Frame(controls_frame, bg='#f0f0f0')
        risk_frame.pack(fill='x', pady=5)
        
        tk.Label(risk_frame, text="🎲 Risk Level:", font=('Arial', 10), bg='#f0f0f0').pack(side='left', padx=5)
        
        self.risk_level = tk.StringVar(value="medium")
        risk_combo = ttk.Combobox(
            risk_frame,
            textvariable=self.risk_level,
            values=["conservative", "medium", "aggressive"],
            state="readonly",
            width=15
        )
        risk_combo.pack(side='left', padx=5)
        
        # Default league
        league_frame = tk.Frame(controls_frame, bg='#f0f0f0')
        league_frame.pack(fill='x', pady=5)
        
        tk.Label(league_frame, text="🏆 Default League:", font=('Arial', 10), bg='#f0f0f0').pack(side='left', padx=5)
        
        self.default_league = tk.StringVar(value="🇹🇷 Turkish Super League")
        league_combo = ttk.Combobox(
            league_frame,
            textvariable=self.default_league,
            values=list(self.league_mapping.keys()),
            state="readonly",
            width=20
        )
        league_combo.pack(side='left', padx=5)
        
        # Predict button
        predict_frame = tk.Frame(controls_frame, bg='#f0f0f0')
        predict_frame.pack(fill='x', pady=10)
        
        self.predict_btn = tk.Button(
            predict_frame,
            text="🎯 PREDICT ALL MATCHES",
            command=self.predict_matches,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 14, 'bold'),
            height=2,
            state='disabled'
        )
        self.predict_btn.pack(fill='x', padx=10)
        
        # Results area
        results_frame = tk.LabelFrame(parent, text="📊 Predictions", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        results_frame.pack(fill='both', expand=True, pady=5)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=20,
            width=60,
            font=('Consolas', 10),
            state='disabled'
        )
        self.results_text.pack(fill='both', expand=True, pady=5)
        
        # Export buttons
        export_frame = tk.Frame(results_frame, bg='#f0f0f0')
        export_frame.pack(fill='x', pady=5)
        
        export_txt_btn = tk.Button(
            export_frame,
            text="💾 Save TXT",
            command=self.export_predictions_txt,
            bg='#2196F3',
            fg='white',
            font=('Arial', 10)
        )
        export_txt_btn.pack(side='left', padx=5)
        
        export_csv_btn = tk.Button(
            export_frame,
            text="📊 Save CSV",
            command=self.export_predictions_csv,
            bg='#FF9800',
            fg='white',
            font=('Arial', 10)
        )
        export_csv_btn.pack(side='left', padx=5)
        
        copy_btn = tk.Button(
            export_frame,
            text="📋 Copy Coupon",
            command=self.copy_coupon_to_clipboard,
            bg='#9C27B0',
            fg='white',
            font=('Arial', 10)
        )
        copy_btn.pack(side='left', padx=5)
    
    def create_match_entry_row(self, index):
        """Create a single match entry row"""
        row_frame = tk.Frame(self.scrollable_frame, bg='#ffffff', relief='ridge', bd=1)
        row_frame.pack(fill='x', pady=2, padx=5)
        
        # Match number
        match_label = tk.Label(
            row_frame,
            text=f"m{index+1}:",
            font=('Arial', 10, 'bold'),
            bg='#ffffff',
            width=3
        )
        match_label.pack(side='left', padx=5, pady=5)
        
        # Home team
        home_entry = tk.Entry(row_frame, font=('Arial', 10), width=15)
        home_entry.pack(side='left', padx=2, pady=5)
        
        vs_label = tk.Label(row_frame, text="vs", font=('Arial', 10), bg='#ffffff')
        vs_label.pack(side='left', padx=2)
        
        # Away team
        away_entry = tk.Entry(row_frame, font=('Arial', 10), width=15)
        away_entry.pack(side='left', padx=2, pady=5)
        
        # League (optional)
        league_var = tk.StringVar(value="Auto")
        league_combo = ttk.Combobox(
            row_frame,
            textvariable=league_var,
            values=["Auto"] + list(self.league_mapping.keys()),
            state="readonly",
            width=12,
            font=('Arial', 9)
        )
        league_combo.pack(side='left', padx=2, pady=5)
        
        self.match_entries.append({
            'home': home_entry,
            'away': away_entry,
            'league': league_var
        })
    
    def toggle_input_method(self):
        """Toggle between input methods"""
        # Hide all frames
        self.manual_frame.pack_forget()
        self.paste_frame.pack_forget()
        self.file_frame.pack_forget()
        
        # Show selected frame
        method = self.input_method.get()
        if method == "manual":
            self.manual_frame.pack(fill='both', expand=True)
        elif method == "paste":
            self.paste_frame.pack(fill='both', expand=True)
        elif method == "file":
            self.file_frame.pack(fill='both', expand=True)
    
    def clear_all_matches(self):
        """Clear all match entries"""
        for entry in self.match_entries:
            entry['home'].delete(0, tk.END)
            entry['away'].delete(0, tk.END)
            entry['league'].set("Auto")
    
    def fill_sample_matches(self):
        """Fill with sample matches for testing"""
        sample_matches = [
            ("Galatasaray", "Fenerbahce", "🇹🇷 Turkish Super League"),
            ("Besiktas", "Trabzonspor", "🇹🇷 Turkish Super League"),
            ("Real Madrid", "Barcelona", "🇪🇸 Spanish La Liga"),
            ("Man United", "Arsenal", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League"),
            ("Bayern Munich", "Dortmund", "🇩🇪 German Bundesliga"),
            ("Juventus", "Inter Milan", "🇮🇹 Italian Serie A"),
            ("PSG", "Marseille", "🇫🇷 French Ligue 1"),
            ("Ajax", "PSV", "🇳🇱 Dutch Eredivisie"),
            ("Porto", "Benfica", "🇵🇹 Portuguese Liga"),
            ("Olympiacos", "Panathinaikos", "🇬🇷 Greek Super League"),
            ("Samsunspor", "Konyaspor", "🇹🇷 Turkish Super League"),
            ("Atletico Madrid", "Sevilla", "🇪🇸 Spanish La Liga"),
            ("Chelsea", "Liverpool", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League"),
            ("AC Milan", "Napoli", "🇮🇹 Italian Serie A"),
            ("Lyon", "Monaco", "🇫🇷 French Ligue 1")
        ]
        
        for i, (home, away, league) in enumerate(sample_matches):
            if i < len(self.match_entries):
                self.match_entries[i]['home'].delete(0, tk.END)
                self.match_entries[i]['home'].insert(0, home)
                self.match_entries[i]['away'].delete(0, tk.END)
                self.match_entries[i]['away'].insert(0, away)
                self.match_entries[i]['league'].set(league)
    
    def parse_pasted_matches(self):
        """Parse pasted matches and fill entries"""
        text = self.paste_text.get(1.0, tk.END).strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            messagebox.showwarning("Warning", "No matches found in pasted text!")
            return
        
        if len(lines) > 15:
            messagebox.showwarning("Warning", f"Found {len(lines)} matches, using first 15.")
            lines = lines[:15]
        
        self.clear_all_matches()
        
        for i, line in enumerate(lines):
            if i >= len(self.match_entries):
                break
                
            # Try to parse different formats
            home, away = self.parse_match_line(line)
            
            if home and away:
                self.match_entries[i]['home'].insert(0, home)
                self.match_entries[i]['away'].insert(0, away)
                self.match_entries[i]['league'].set("Auto")
        
        messagebox.showinfo("Success", f"Parsed {min(len(lines), 15)} matches!")
    
    def parse_match_line(self, line):
        """Parse a single match line"""
        # Try different separators
        separators = [' vs ', ' v ', ' - ', ' x ', ' VS ', ' V ', ' X ']
        
        for sep in separators:
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
        
        # If no separator found, try to split by whitespace and find "vs" pattern
        words = line.split()
        for i, word in enumerate(words):
            if word.lower() in ['vs', 'v', 'x', '-']:
                if i > 0 and i < len(words) - 1:
                    home = ' '.join(words[:i])
                    away = ' '.join(words[i+1:])
                    return home.strip(), away.strip()
        
        return None, None
    
    def load_matches_from_file(self):
        """Load matches from file"""
        file_path = filedialog.askopenfilename(
            title="Select matches file",
            filetypes=[
                ("All supported", "*.csv;*.txt;*.json"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            matches = []
            
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    home = row.get('home_team', row.get('home', ''))
                    away = row.get('away_team', row.get('away', ''))
                    league = row.get('league', 'Auto')
                    if home and away:
                        matches.append((home, away, league))
            
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                home = item.get('home_team', item.get('home', ''))
                                away = item.get('away_team', item.get('away', ''))
                                league = item.get('league', 'Auto')
                                if home and away:
                                    matches.append((home, away, league))
            
            else:  # Text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line:
                            home, away = self.parse_match_line(line)
                            if home and away:
                                matches.append((home, away, 'Auto'))
            
            if matches:
                self.clear_all_matches()
                
                # Display file info
                self.file_info_text.config(state='normal')
                self.file_info_text.delete(1.0, tk.END)
                self.file_info_text.insert(tk.END, f"Loaded from: {os.path.basename(file_path)}\n\n")
                self.file_info_text.insert(tk.END, f"Found {len(matches)} matches:\n\n")
                
                for i, (home, away, league) in enumerate(matches[:15]):
                    if i < len(self.match_entries):
                        self.match_entries[i]['home'].delete(0, tk.END)
                        self.match_entries[i]['home'].insert(0, home)
                        self.match_entries[i]['away'].delete(0, tk.END)
                        self.match_entries[i]['away'].insert(0, away)
                        if league != 'Auto' and league in self.league_mapping:
                            self.match_entries[i]['league'].set(league)
                        else:
                            self.match_entries[i]['league'].set("Auto")
                    
                    self.file_info_text.insert(tk.END, f"{i+1:2d}. {home} vs {away}\n")
                
                self.file_info_text.config(state='disabled')
                
                messagebox.showinfo("Success", f"Loaded {min(len(matches), 15)} matches from file!")
            else:
                messagebox.showerror("Error", "No valid matches found in file!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def load_system_async(self):
        """Load prediction system in background thread"""
        def load_system():
            try:
                self.status_var.set("Loading data files...")
                self.processor = DataProcessor(data_path='csvs/')
                self.processor.load_data()
                self.processor.clean_data()
                
                self.status_var.set("Loading ML models...")
                self.predictor = MatchPredictor()
                
                if os.path.exists('models/spor_toto_model_rf.joblib'):
                    self.predictor.load_models('models/spor_toto_model')
                else:
                    self.status_var.set("Training ML models (this may take a while)...")
                    features_df = self.processor.create_features()
                    self.predictor.train_models(features_df)
                    self.predictor.save_models('models/spor_toto_model')
                
                self.spor_toto = SporTotoPredictor(self.predictor, self.processor)
                
                self.system_loaded = True
                self.status_var.set("✅ Prediction system ready!")
                
                # Enable predict button
                self.predict_btn.config(state='normal')
                
            except Exception as e:
                self.status_var.set(f"❌ Error loading system: {str(e)}")
                messagebox.showerror("Error", f"Failed to load prediction system:\n{str(e)}")
        
        thread = threading.Thread(target=load_system, daemon=True)
        thread.start()
    
    def get_matches_from_entries(self):
        """Get matches from current entries"""
        matches = []
        
        for i, entry in enumerate(self.match_entries):
            home = entry['home'].get().strip()
            away = entry['away'].get().strip()
            league = entry['league'].get()
            
            if home and away:
                # Determine league
                if league == "Auto" or league not in self.league_mapping:
                    league_code = self.league_mapping[self.default_league.get()]
                else:
                    league_code = self.league_mapping[league]
                
                match_info = {
                    'home_team': home,
                    'away_team': away,
                    'league': league_code,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
                
                matches.append(match_info)
        
        return matches
    
    def predict_matches(self):
        """Predict all matches"""
        if not self.system_loaded:
            messagebox.showerror("Error", "Prediction system not ready yet. Please wait...")
            return
        
        matches = self.get_matches_from_entries()
        
        if len(matches) == 0:
            messagebox.showwarning("Warning", "No matches entered!")
            return
        
        if len(matches) < 15:
            response = messagebox.askyesno(
                "Confirm", 
                f"Only {len(matches)} matches entered. Spor Toto requires 15 matches.\nContinue anyway?"
            )
            if not response:
                return
        
        try:
            self.status_var.set("🔮 Predicting matches...")
            self.predict_btn.config(state='disabled')
            
            # Get predictions
            risk_level = self.risk_level.get()
            predictions = self.spor_toto.predict_matches(matches, risk_level)
            
            if predictions:
                self.display_predictions(predictions)
                self.status_var.set(f"✅ Predicted {len(predictions)} matches!")
            else:
                messagebox.showerror("Error", "Failed to generate predictions!")
                self.status_var.set("❌ Prediction failed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {str(e)}")
            self.status_var.set("❌ Prediction failed")
        
        finally:
            self.predict_btn.config(state='normal')
    
    def display_predictions(self, predictions):
        """Display predictions in results area"""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, "🏆 SPOR TOTO MATCH PREDICTIONS\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Match predictions
        self.results_text.insert(tk.END, "📋 MATCH PREDICTIONS:\n")
        self.results_text.insert(tk.END, "-" * 40 + "\n")
        
        for i, pred in enumerate(predictions):
            home = pred['home_team']
            away = pred['away_team']
            prediction = pred['spor_toto_prediction']
            confidence = pred['ml_prediction']['confidence']
            probs = pred['ml_prediction']['probabilities']
            
            self.results_text.insert(tk.END, f"m{i+1:2d}: {home} vs {away}\n")
            self.results_text.insert(tk.END, f"     Prediction: {prediction}\n")
            self.results_text.insert(tk.END, f"     Confidence: {confidence:.1f}%\n")
            self.results_text.insert(tk.END, f"     Probs: 1:{probs['home_win']:.1f}% X:{probs['draw']:.1f}% 2:{probs['away_win']:.1f}%\n")
            
            # Value bets
            if pred.get('value_analysis') and pred['value_analysis'].get('good_bets'):
                self.results_text.insert(tk.END, f"     💰 Value: {', '.join([bet[0].replace('_win', '').replace('_', ' ') for bet in pred['value_analysis']['good_bets']])}\n")
            
            self.results_text.insert(tk.END, "\n")
        
        # Coupon format
        self.results_text.insert(tk.END, "\n🎫 SPOR TOTO COUPON FORMAT:\n")
        self.results_text.insert(tk.END, "-" * 40 + "\n")
        
        for i, pred in enumerate(predictions):
            prediction = pred['spor_toto_prediction']
            self.results_text.insert(tk.END, f"{prediction}\n")
        
        # Statistics
        self.results_text.insert(tk.END, f"\n📊 PREDICTION STATISTICS:\n")
        self.results_text.insert(tk.END, "-" * 40 + "\n")
        
        single_count = sum(1 for pred in predictions if '(' in pred['spor_toto_prediction'] and '-' not in pred['spor_toto_prediction'].split('(')[1])
        double_count = sum(1 for pred in predictions if pred['spor_toto_prediction'].count('-') == 1)
        triple_count = sum(1 for pred in predictions if pred['spor_toto_prediction'].count('-') == 2)
        
        # Calculate total combinations
        total_combinations = 1
        for pred in predictions:
            outcome_count = pred['spor_toto_prediction'].split('(')[1].count('-') + 1
            total_combinations *= outcome_count
        
        self.results_text.insert(tk.END, f"Total Matches: {len(predictions)}\n")
        self.results_text.insert(tk.END, f"Single Outcomes: {single_count}\n")
        self.results_text.insert(tk.END, f"Double Outcomes: {double_count}\n") 
        self.results_text.insert(tk.END, f"Triple Outcomes: {triple_count}\n")
        self.results_text.insert(tk.END, f"Total Combinations: {total_combinations:,}\n")
        
        avg_confidence = sum(pred['ml_prediction']['confidence'] for pred in predictions) / len(predictions)
        self.results_text.insert(tk.END, f"Average Confidence: {avg_confidence:.1f}%\n")
        
        self.results_text.insert(tk.END, f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.results_text.insert(tk.END, f"Risk Level: {self.risk_level.get().title()}\n")
        
        self.results_text.config(state='disabled')
        
        # Store predictions for export
        self.current_predictions = predictions
    
    def export_predictions_txt(self):
        """Export predictions to text file"""
        if not hasattr(self, 'current_predictions'):
            messagebox.showwarning("Warning", "No predictions to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save predictions as text",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                content = self.results_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Predictions saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def export_predictions_csv(self):
        """Export predictions to CSV file"""
        if not hasattr(self, 'current_predictions'):
            messagebox.showwarning("Warning", "No predictions to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save predictions as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                data = []
                for i, pred in enumerate(self.current_predictions):
                    data.append({
                        'Match': f"m{i+1}",
                        'Home_Team': pred['home_team'],
                        'Away_Team': pred['away_team'],
                        'Prediction': pred['spor_toto_prediction'],
                        'Confidence': pred['ml_prediction']['confidence'],
                        'Home_Win_Prob': pred['ml_prediction']['probabilities']['home_win'],
                        'Draw_Prob': pred['ml_prediction']['probabilities']['draw'],
                        'Away_Win_Prob': pred['ml_prediction']['probabilities']['away_win'],
                        'League': pred.get('league', ''),
                        'Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Predictions saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save CSV: {str(e)}")
    
    def copy_coupon_to_clipboard(self):
        """Copy coupon format to clipboard"""
        if not hasattr(self, 'current_predictions'):
            messagebox.showwarning("Warning", "No predictions to copy!")
            return
        
        try:
            coupon_text = "\n".join([pred['spor_toto_prediction'] for pred in self.current_predictions])
            self.root.clipboard_clear()
            self.root.clipboard_append(coupon_text)
            messagebox.showinfo("Success", "Coupon copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")

def main():
    root = tk.Tk()
    app = SporTotoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
