#!/usr/bin/env python3
"""
CSV Analyzer and Team Name Standardizer

This script analyzes CSV files in the csvs/ directory to:
1. Check column consistency across all files
2. Identify team names with special characters
3. Create standardized team name mappings
4. Clean and standardize team names
"""

import os
import pandas as pd
import re
from collections import defaultdict, Counter
import glob

class CSVAnalyzer:
    def __init__(self, csv_directory="csvs"):
        self.csv_directory = csv_directory
        self.csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))
        self.column_analysis = {}
        self.team_names = set()
        self.problematic_teams = {}
        
    def analyze_columns(self):
        """Analyze column structure across all CSV files"""
        print("=" * 60)
        print("COLUMN STRUCTURE ANALYSIS")
        print("=" * 60)
        
        all_columns = defaultdict(list)
        
        for csv_file in self.csv_files:
            filename = os.path.basename(csv_file)
            try:
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(csv_file, encoding=encoding, nrows=1)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"❌ Could not read {filename} with any encoding")
                    continue
                    
                columns = df.columns.tolist()
                self.column_analysis[filename] = columns
                
                for col in columns:
                    all_columns[col].append(filename)
                    
                print(f"📄 {filename}: {len(columns)} columns")
                
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        
        print(f"\n📊 Total files analyzed: {len(self.column_analysis)}")
        
        # Find common columns
        print(f"\n🔍 Column frequency analysis:")
        column_counts = {col: len(files) for col, files in all_columns.items()}
        
        for col, count in sorted(column_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.csv_files)) * 100
            print(f"  {col}: {count}/{len(self.csv_files)} files ({percentage:.1f}%)")
        
        # Find files with different column structures
        print(f"\n📋 Files with unique column patterns:")
        column_patterns = defaultdict(list)
        
        for filename, columns in self.column_analysis.items():
            pattern = tuple(sorted(columns))
            column_patterns[pattern].append(filename)
        
        for i, (pattern, files) in enumerate(column_patterns.items(), 1):
            print(f"\n  Pattern {i} ({len(files)} files): {', '.join(files)}")
            print(f"    Columns: {', '.join(pattern)}")
    
    def extract_team_names(self):
        """Extract all team names from CSV files"""
        print("\n" + "=" * 60)
        print("TEAM NAME EXTRACTION")
        print("=" * 60)
        
        for csv_file in self.csv_files:
            filename = os.path.basename(csv_file)
            
            try:
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(csv_file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"❌ Could not read {filename}")
                    continue
                
                # Look for team name columns
                team_columns = []
                for col in df.columns:
                    if any(keyword in col.lower() for keyword in ['home', 'away', 'team']):
                        team_columns.append(col)
                
                if not team_columns:
                    print(f"⚠️  No team columns found in {filename}")
                    continue
                
                # Extract team names
                teams_in_file = set()
                for col in team_columns:
                    unique_teams = df[col].dropna().unique()
                    teams_in_file.update(unique_teams)
                    self.team_names.update(unique_teams)
                
                print(f"📄 {filename}: {len(teams_in_file)} unique teams from columns {team_columns}")
                
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
        
        print(f"\n📊 Total unique team names found: {len(self.team_names)}")
    
    def identify_problematic_teams(self):
        """Identify team names with special characters that need cleaning"""
        print("\n" + "=" * 60)
        print("PROBLEMATIC TEAM NAMES ANALYSIS")
        print("=" * 60)
        
        patterns = {
            'slash': r'.*/.+',  # Teams with forward slash like "Bodo/Glimt"
            'space_number': r'.*\s+\d+',  # Teams with space + number like "Sarpsborg 08"
            'hyphen': r'.*-.*',  # Teams with hyphen
            'dot': r'.*\..*',  # Teams with dot
            'ampersand': r'.*&.*',  # Teams with ampersand
            'parentheses': r'.*\(.*\).*',  # Teams with parentheses
            'apostrophe': r".*'.*",  # Teams with apostrophe
        }
        
        for pattern_name, pattern in patterns.items():
            matching_teams = [team for team in self.team_names 
                            if isinstance(team, str) and re.match(pattern, team)]
            
            if matching_teams:
                self.problematic_teams[pattern_name] = matching_teams
                print(f"\n🔍 {pattern_name.upper()} pattern ({len(matching_teams)} teams):")
                for team in sorted(matching_teams)[:10]:  # Show first 10
                    print(f"  • {team}")
                if len(matching_teams) > 10:
                    print(f"  ... and {len(matching_teams) - 10} more")
    
    def suggest_team_name_fixes(self):
        """Suggest standardized team names"""
        print("\n" + "=" * 60)
        print("TEAM NAME STANDARDIZATION SUGGESTIONS")
        print("=" * 60)
        
        suggestions = {}
        
        for category, teams in self.problematic_teams.items():
            print(f"\n🔧 {category.upper()} fixes:")
            category_suggestions = {}
            
            for team in sorted(teams):
                if not isinstance(team, str):
                    continue
                    
                # Apply different cleaning rules based on category
                if category == 'slash':
                    # Replace / with space: "Bodo/Glimt" -> "Bodo Glimt"
                    cleaned = team.replace('/', ' ')
                elif category == 'space_number':
                    # Keep as is but could suggest removing space: "Sarpsborg 08" -> "Sarpsborg08"
                    cleaned = team.replace(' ', '')
                elif category == 'hyphen':
                    # Replace - with space: "Real-Madrid" -> "Real Madrid"
                    cleaned = team.replace('-', ' ')
                elif category == 'dot':
                    # Remove dots: "A.C. Milan" -> "AC Milan"
                    cleaned = team.replace('.', '')
                elif category == 'ampersand':
                    # Replace & with and: "Brighton & Hove" -> "Brighton and Hove"
                    cleaned = team.replace('&', 'and')
                elif category == 'parentheses':
                    # Remove parentheses: "Team (Reserve)" -> "Team Reserve"
                    cleaned = re.sub(r'[()]', '', team)
                elif category == 'apostrophe':
                    # Remove apostrophes: "St. Mary's" -> "St Marys"
                    cleaned = team.replace("'", "")
                else:
                    cleaned = team
                
                # Clean up extra spaces
                cleaned = ' '.join(cleaned.split())
                
                if cleaned != team:
                    category_suggestions[team] = cleaned
                    print(f"  {team} → {cleaned}")
            
            suggestions[category] = category_suggestions
        
        return suggestions
    
    def create_cleaning_script(self, suggestions):
        """Create a script to apply the cleaning suggestions"""
        print("\n" + "=" * 60)
        print("CREATING CLEANING SCRIPT")
        print("=" * 60)
        
        script_content = '''#!/usr/bin/env python3
"""
Team Name Cleaning Script
Auto-generated by csv_analyzer.py

This script applies team name standardization across all CSV files.
"""

import pandas as pd
import os
import glob
from datetime import datetime

def clean_team_names():
    """Apply team name cleaning to all CSV files"""
    
    # Team name mapping dictionary
    team_name_mapping = {
'''
        
        # Add all suggestions to the mapping
        for category, category_suggestions in suggestions.items():
            if category_suggestions:
                script_content += f"        # {category.upper()} fixes\n"
                for original, cleaned in category_suggestions.items():
                    script_content += f"        '{original}': '{cleaned}',\n"
                script_content += "\n"
        
        script_content += '''    }
    
    csv_files = glob.glob("csvs/*.csv")
    changes_made = {}
    
    print(f"🧹 Starting team name cleaning for {len(csv_files)} files...")
    
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        file_changes = 0
        
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"❌ Could not read {filename}")
                continue
            
            # Find team columns
            team_columns = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['home', 'away', 'team']):
                    team_columns.append(col)
            
            if not team_columns:
                continue
            
            # Apply cleaning to team columns
            for col in team_columns:
                for original, cleaned in team_name_mapping.items():
                    mask = df[col] == original
                    if mask.any():
                        df.loc[mask, col] = cleaned
                        count = mask.sum()
                        file_changes += count
                        print(f"  📝 {filename}: {col} '{original}' → '{cleaned}' ({count} occurrences)")
            
            # Save cleaned file if changes were made
            if file_changes > 0:
                # Create backup
                backup_file = csv_file + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                df_original = pd.read_csv(csv_file)
                df_original.to_csv(backup_file, index=False)
                
                # Save cleaned version
                df.to_csv(csv_file, index=False)
                changes_made[filename] = file_changes
                print(f"  ✅ {filename}: {file_changes} changes applied (backup created)")
        
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    print(f"\\n🎉 Cleaning complete!")
    print(f"📊 Files modified: {len(changes_made)}")
    print(f"📊 Total changes: {sum(changes_made.values())}")
    
    if changes_made:
        print("\\n📋 Summary of changes:")
        for filename, count in changes_made.items():
            print(f"  • {filename}: {count} changes")

if __name__ == "__main__":
    clean_team_names()
'''
        
        with open("clean_team_names.py", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print("✅ Created clean_team_names.py")
        print("   Run with: python clean_team_names.py")
    
    def run_full_analysis(self):
        """Run complete analysis"""
        print("🔍 Starting comprehensive CSV analysis...")
        
        if not self.csv_files:
            print("❌ No CSV files found in the csvs/ directory")
            return
        
        print(f"📁 Found {len(self.csv_files)} CSV files")
        
        # Run all analysis steps
        self.analyze_columns()
        self.extract_team_names()
        self.identify_problematic_teams()
        suggestions = self.suggest_team_name_fixes()
        self.create_cleaning_script(suggestions)
        
        print(f"\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print("✅ Column analysis completed")
        print("✅ Team name extraction completed")
        print("✅ Problematic team identification completed")
        print("✅ Cleaning script generated")
        print(f"\nNext steps:")
        print("1. Review the analysis results above")
        print("2. Run: python clean_team_names.py")
        print("3. Check the cleaned files")

def main():
    analyzer = CSVAnalyzer()
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
