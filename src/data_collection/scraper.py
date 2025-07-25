import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from typing import Dict, List, Optional
import json
import os
from datetime import datetime, timedelta
import re

class TurkishFootballScraper:
    """
    Data scraper for Turkish football matches and statistics
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self.request_delay = 1  # seconds between requests
        
    def scrape_spor_toto_matches(self) -> List[Dict]:
        """
        Scrape current week's Spor Toto matches from multiple leagues
        """
        self.logger.info("Scraping current Spor Toto matches")
        
        # This would scrape from iddaa.com or nesine.com
        # For demo purposes, we'll return sample data from multiple leagues
        
        # Define leagues that commonly appear in Spor Toto
        spor_toto_leagues = [
            'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1',
            'Super Lig', 'Eredivisie', 'Primeira Liga', 'Pro League', 'Scottish Premiership'
        ]
        
        import random
        
        sample_matches = []
        match_counter = 1
        
        # Generate 15 matches from different leagues
        for i in range(15):
            # Randomly select a league for this match
            league = random.choice(spor_toto_leagues)
            teams = self._get_league_teams(league)
            
            if len(teams) >= 2:
                # Select two random teams from the league
                selected_teams = random.sample(teams, 2)
                home_team = selected_teams[0]
                away_team = selected_teams[1]
                
                # Generate match date (next 7 days)
                match_date = datetime.now() + timedelta(days=random.randint(0, 6))
                
                # Generate realistic odds based on team strength
                base_odds = self._generate_realistic_odds(home_team, away_team, league)
                
                match = {
                    'match_id': f'ST2025W{datetime.now().isocalendar()[1]:02d}M{match_counter:02d}',
                    'home_team': home_team,
                    'away_team': away_team,
                    'league': league,
                    'date': match_date.strftime('%Y-%m-%d'),
                    'time': random.choice(['14:00', '16:30', '19:00', '21:45']),
                    'home_odds': base_odds['home'],
                    'draw_odds': base_odds['draw'],
                    'away_odds': base_odds['away'],
                    'country': self._get_league_country(league)
                }
                
                sample_matches.append(match)
                match_counter += 1
        
        return sample_matches
    
    def _generate_realistic_odds(self, home_team: str, away_team: str, league: str) -> Dict:
        """Generate realistic betting odds based on team strength"""
        import random
        
        # Define team strength tiers (simplified)
        elite_teams = [
            'Manchester City', 'Liverpool', 'Arsenal', 'Real Madrid', 'Barcelona', 
            'Bayern Munich', 'PSG', 'Inter Milan', 'Juventus', 'AC Milan',
            'Galatasaray', 'Fenerbahçe', 'Beşiktaş'
        ]
        
        strong_teams = [
            'Manchester United', 'Chelsea', 'Tottenham', 'Atletico Madrid',
            'Borussia Dortmund', 'Napoli', 'AS Roma', 'Marseille', 'Porto',
            'Benfica', 'Ajax', 'Trabzonspor'
        ]
        
        # Determine team strengths
        home_strength = 3 if home_team in elite_teams else (2 if home_team in strong_teams else 1)
        away_strength = 3 if away_team in elite_teams else (2 if away_team in strong_teams else 1)
        
        # Home advantage
        home_advantage = 0.3
        
        # Calculate base probabilities
        strength_diff = (home_strength - away_strength) + home_advantage
        
        if strength_diff > 1:
            # Strong home team
            home_prob = random.uniform(0.55, 0.70)
            draw_prob = random.uniform(0.20, 0.25)
            away_prob = 1 - home_prob - draw_prob
        elif strength_diff < -1:
            # Strong away team
            away_prob = random.uniform(0.45, 0.60)
            draw_prob = random.uniform(0.22, 0.28)
            home_prob = 1 - away_prob - draw_prob
        else:
            # Balanced match
            home_prob = random.uniform(0.35, 0.45)
            draw_prob = random.uniform(0.25, 0.35)
            away_prob = 1 - home_prob - draw_prob
        
        # Convert probabilities to odds (with bookmaker margin)
        margin = 0.05  # 5% bookmaker margin
        total_prob = home_prob + draw_prob + away_prob + margin
        
        home_odds = round(total_prob / home_prob, 2)
        draw_odds = round(total_prob / draw_prob, 2)
        away_odds = round(total_prob / away_prob, 2)
        
        return {
            'home': max(1.1, home_odds),
            'draw': max(2.5, draw_odds),
            'away': max(1.1, away_odds)
        }
    
    def _get_league_country(self, league: str) -> str:
        """Get country for a given league"""
        league_countries = {
            'Premier League': 'England',
            'La Liga': 'Spain',
            'Bundesliga': 'Germany',
            'Serie A': 'Italy',
            'Ligue 1': 'France',
            'Super Lig': 'Turkey',
            'Primeira Liga': 'Portugal',
            'Eredivisie': 'Netherlands',
            'Pro League': 'Belgium',
            'Scottish Premiership': 'Scotland',
            'Austrian Bundesliga': 'Austria',
            'Swiss Super League': 'Switzerland',
            'Greek Super League': 'Greece',
            'Eliteserien': 'Norway',
            'Allsvenskan': 'Sweden'
        }
        return league_countries.get(league, 'Unknown')
    
    def get_spor_toto_data_sources(self) -> Dict:
        """Get data source URLs for different leagues"""
        return {
            'turkish_leagues': {
                'spor_toto_official': 'https://www.iddaa.com/spor-toto',
                'nesine': 'https://www.nesine.com/spor-toto',
                'mackolik': 'https://www.mackolik.com'
            },
            'international_sources': {
                'premier_league': 'https://www.premierleague.com/fixtures',
                'la_liga': 'https://www.laliga.com/en-GB/fixtures',
                'bundesliga': 'https://www.bundesliga.com/en/bundesliga/matchday',
                'serie_a': 'https://www.legaseriea.it/en/fixtures-and-results',
                'ligue_1': 'https://www.ligue1.com/matches',
                'eredivisie': 'https://www.eredivisie.nl/wedstrijden',
                'primeira_liga': 'https://www.ligaportugal.pt/en/matches'
            },
            'odds_providers': {
                'bet365': 'https://www.bet365.com',
                'betfair': 'https://www.betfair.com',
                'pinnacle': 'https://www.pinnacle.com'
            }
        }
    
    def scrape_real_spor_toto_matches(self) -> List[Dict]:
        """
        Scrape real Spor Toto matches from official sources
        Note: This would need to be implemented with actual web scraping
        """
        self.logger.info("Scraping real Spor Toto matches from official sources")
        
        # In a real implementation, this would:
        # 1. Scrape from iddaa.com spor toto page
        # 2. Parse HTML to extract match information
        # 3. Validate and clean the data
        # 4. Return structured match data
        
        # For now, return simulated data but with more realistic structure
        return self.scrape_spor_toto_matches()  # Use our enhanced sample data
    
    def get_league_quality_weights(self) -> Dict:
        """Get quality weights for different leagues (for ML features)"""
        return {
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
        }
    
    def scrape_historical_matches(self, season: str, leagues: List[str]) -> pd.DataFrame:
        """
        Scrape historical match data for specified leagues and season
        """
        self.logger.info(f"Scraping historical matches for {season} season")
        
        all_matches = []
        
        for league in leagues:
            self.logger.info(f"Scraping {league} matches")
            
            # In a real implementation, this would scrape from mackolik.com or similar
            league_matches = self._scrape_league_matches(league, season)
            all_matches.extend(league_matches)
            
            time.sleep(self.request_delay)
        
        df = pd.DataFrame(all_matches)
        return df
    
    def _scrape_league_matches(self, league: str, season: str) -> List[Dict]:
        """
        Scrape matches for a specific league and season
        """
        # This is a placeholder - in reality you'd scrape from websites
        # Here we generate sample data that mimics real match data
        
        teams = self._get_league_teams(league)
        matches = []
        
        # Generate sample matches for the season
        start_date = datetime(2024, 8, 1)  # Season start
        current_date = start_date
        
        for week in range(1, 35):  # 34 weeks in a season
            week_matches = self._generate_week_matches(teams, current_date, week, league)
            matches.extend(week_matches)
            current_date += timedelta(days=7)
        
        return matches
    
    def _get_league_teams(self, league: str) -> List[str]:
        """Get teams for a specific league - Top 15 European leagues"""
        
        teams_dict = {
            # Turkish Leagues
            'Super Lig': [
                'Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'Trabzonspor',
                'Başakşehir', 'Konyaspor', 'Sivasspor', 'Alanyaspor',
                'Antalyaspor', 'Kasımpaşa', 'Kayserispor', 'Rizespor',
                'Hatayspor', 'Fatih Karagümrük', 'Gaziantep FK', 'Ankaragücü',
                'Giresunspor', 'Ümraniyespor'
            ],
            
            # English Premier League
            'Premier League': [
                'Manchester City', 'Arsenal', 'Liverpool', 'Manchester United',
                'Newcastle United', 'Brighton', 'Tottenham', 'Chelsea',
                'Aston Villa', 'West Ham', 'Crystal Palace', 'Bournemouth',
                'Wolves', 'Fulham', 'Everton', 'Brentford', 'Nottingham Forest',
                'Luton Town', 'Burnley', 'Sheffield United'
            ],
            
            # Spanish La Liga
            'La Liga': [
                'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Athletic Bilbao',
                'Real Sociedad', 'Real Betis', 'Villarreal', 'Valencia',
                'Sevilla', 'Getafe', 'Osasuna', 'Las Palmas', 'Rayo Vallecano',
                'Girona', 'Mallorca', 'Cadiz', 'Celta Vigo', 'Granada',
                'Alaves', 'Almeria'
            ],
            
            # German Bundesliga
            'Bundesliga': [
                'Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Union Berlin',
                'SC Freiburg', 'Bayer Leverkusen', 'Eintracht Frankfurt', 'Wolfsburg',
                'Mainz', 'Borussia Monchengladbach', 'FC Koln', 'Werder Bremen',
                'VfB Stuttgart', 'FC Augsburg', 'Hoffenheim', 'VfL Bochum',
                'FC Heidenheim', 'SV Darmstadt'
            ],
            
            # Italian Serie A
            'Serie A': [
                'Inter Milan', 'AC Milan', 'Juventus', 'Atalanta', 'AS Roma',
                'Lazio', 'Napoli', 'Fiorentina', 'Bologna', 'Torino',
                'Genoa', 'Monza', 'Verona', 'Lecce', 'Udinese',
                'Cagliari', 'Frosinone', 'Empoli', 'Sassuolo', 'Salernitana'
            ],
            
            # French Ligue 1
            'Ligue 1': [
                'Paris Saint-Germain', 'AS Monaco', 'Lille', 'Nice',
                'Lens', 'Marseille', 'Rennes', 'Lyon', 'Montpellier',
                'Toulouse', 'Strasbourg', 'Nantes', 'Brest', 'Reims',
                'Le Havre', 'Metz', 'Lorient', 'Clermont'
            ],
            
            # Portuguese Primeira Liga
            'Primeira Liga': [
                'Benfica', 'Porto', 'Sporting CP', 'Braga', 'Guimaraes',
                'Casa Pia', 'Gil Vicente', 'Famalicao', 'Estrela Amadora',
                'Rio Ave', 'Moreirense', 'Estoril', 'Boavista', 'Arouca',
                'Vizela', 'Farense', 'Portimonense', 'Chaves'
            ],
            
            # Dutch Eredivisie
            'Eredivisie': [
                'PSV Eindhoven', 'Feyenoord', 'Ajax', 'AZ Alkmaar',
                'FC Twente', 'Go Ahead Eagles', 'Fortuna Sittard', 'NEC Nijmegen',
                'FC Utrecht', 'Sparta Rotterdam', 'Heerenveen', 'PEC Zwolle',
                'Almere City', 'RKC Waalwijk', 'Excelsior', 'FC Volendam',
                'Vitesse', 'NAC Breda'
            ],
            
            # Belgian Pro League
            'Pro League': [
                'Club Brugge', 'Royal Antwerp', 'Union Saint-Gilloise', 'Genk',
                'Standard Liege', 'Anderlecht', 'Gent', 'Mechelen',
                'Cercle Brugge', 'Sint-Truiden', 'Westerlo', 'Charleroi',
                'Kortrijk', 'OH Leuven', 'Eupen', 'Seraing'
            ],
            
            # Scottish Premiership
            'Scottish Premiership': [
                'Celtic', 'Rangers', 'Hearts', 'Aberdeen', 'Hibernian',
                'St. Mirren', 'Kilmarnock', 'Motherwell', 'Dundee',
                'St. Johnstone', 'Ross County', 'Livingston'
            ],
            
            # Austrian Bundesliga
            'Austrian Bundesliga': [
                'Red Bull Salzburg', 'Sturm Graz', 'LASK', 'Austria Vienna',
                'Rapid Vienna', 'Wolfsberger AC', 'TSV Hartberg', 'WSG Tirol',
                'Austria Klagenfurt', 'SCR Altach', 'Rheindorf Altach', 'Admira'
            ],
            
            # Swiss Super League
            'Swiss Super League': [
                'Young Boys', 'Basel', 'Servette', 'Lugano', 'St. Gallen',
                'Zurich', 'Lucerne', 'Sion', 'Winterthur', 'Yverdon',
                'Grasshoppers', 'Lausanne'
            ],
            
            # Greek Super League
            'Greek Super League': [
                'Panathinaikos', 'PAOK', 'AEK Athens', 'Olympiacos',
                'Aris', 'Atromitos', 'Volos', 'Lamia', 'OFI Crete',
                'Panserraikos', 'Asteras Tripolis', 'Kifisia', 'PAS Giannina', 'Levadiakos'
            ],
            
            # Norwegian Eliteserien
            'Eliteserien': [
                'Bodø/Glimt', 'Molde', 'Viking', 'Rosenborg', 'Brann',
                'Lillestrøm', 'Odd', 'Tromsø', 'Haugesund', 'Sarpsborg',
                'Sandefjord', 'Strømsgodset', 'Kristiansund', 'HamKam',
                'Aalesund', 'Fredrikstad'
            ],
            
            # Swedish Allsvenskan
            'Allsvenskan': [
                'Malmö FF', 'AIK', 'Djurgården', 'Hammarby', 'IFK Göteborg',
                'Real Sociedad', 'BK Häcken', 'IF Elfsborg', 'IFK Norrköping',
                'Kalmar FF', 'Degerfors', 'Varbergs BoIS', 'Sirius',
                'GIF Sundsvall', 'Mjällby', 'Värnamo'
            ]
        }
        
        return teams_dict.get(league, [])
    
    def _generate_week_matches(self, teams: List[str], date: datetime, week: int, league: str = 'Unknown') -> List[Dict]:
        """Generate sample matches for a week"""
        
        import random
        
        matches = []
        random.shuffle(teams)
        
        # Create matches (assuming 18 teams, 9 matches per week)
        for i in range(0, min(len(teams), 18), 2):
            if i + 1 < len(teams):
                home_team = teams[i]
                away_team = teams[i + 1]
                
                # Generate realistic scores
                home_score = random.choices([0, 1, 2, 3, 4], weights=[15, 30, 35, 15, 5])[0]
                away_score = random.choices([0, 1, 2, 3, 4], weights=[20, 35, 30, 12, 3])[0]
                
                match = {
                    'match_id': f'L{week:02d}M{i//2 + 1:02d}',
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score,
                    'away_score': away_score,
                    'date': date.strftime('%Y-%m-%d'),
                    'league': league,  # Use the actual league parameter
                    'season': '2024-25',
                    'week': week,
                    'home_odds': round(random.uniform(1.5, 4.0), 2),
                    'draw_odds': round(random.uniform(2.8, 4.5), 2),
                    'away_odds': round(random.uniform(1.5, 4.0), 2),
                    'country': self._get_league_country(league)
                }
                
                matches.append(match)
        
        return matches
    
    def scrape_team_statistics(self, team: str, season: str) -> Dict:
        """
        Scrape detailed statistics for a specific team
        """
        self.logger.info(f"Scraping statistics for {team}")
        
        # In reality, this would scrape from detailed stats pages
        stats = {
            'team': team,
            'season': season,
            'matches_played': 30,
            'wins': 15,
            'draws': 8,
            'losses': 7,
            'goals_scored': 45,
            'goals_conceded': 32,
            'clean_sheets': 12,
            'yellow_cards': 78,
            'red_cards': 4,
            'possession_avg': 52.3,
            'shots_per_game': 12.8,
            'shots_on_target_per_game': 4.6,
            'pass_accuracy': 84.2,
            'corners_per_game': 5.4
        }
        
        return stats
    
    def save_data(self, data: pd.DataFrame, filename: str):
        """Save scraped data to file"""
        
        output_dir = self.config.get('data_raw_dir', 'data/raw')
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        if filename.endswith('.json'):
            data.to_json(filepath, orient='records', indent=2)
        elif filename.endswith('.csv'):
            data.to_csv(filepath, index=False)
        else:
            data.to_pickle(filepath)
        
        self.logger.info(f"Data saved to {filepath}")
        return filepath
    
    def update_data(self):
        """
        Update all data sources
        """
        self.logger.info("Starting data update process")
        
        # Scrape current Spor Toto matches
        spor_toto_matches = self.scrape_spor_toto_matches()
        spor_toto_df = pd.DataFrame(spor_toto_matches)
        self.save_data(spor_toto_df, 'current_spor_toto_matches.json')
        
        # Scrape historical data for top European leagues
        leagues = [
            'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1',
            'Super Lig', 'Eredivisie', 'Primeira Liga', 'Pro League', 'Scottish Premiership'
        ]
        historical_data = self.scrape_historical_matches('2024-25', leagues)
        self.save_data(historical_data, 'historical_matches.csv')
        
        # Update team statistics from multiple leagues
        all_teams = []
        sample_leagues = ['Super Lig', 'Premier League', 'La Liga', 'Bundesliga', 'Serie A']
        
        for league in sample_leagues:
            league_teams = self._get_league_teams(league)
            # Take first 2 teams from each league for sample
            for team in league_teams[:2]:
                all_teams.append({'team': team, 'league': league})
        
        team_stats = []
        
        for team_info in all_teams:
            stats = self.scrape_team_statistics(team_info['team'], '2024-25')
            stats['league'] = team_info['league']  # Add league info
            team_stats.append(stats)
            time.sleep(self.request_delay)
        
        team_stats_df = pd.DataFrame(team_stats)
        self.save_data(team_stats_df, 'team_statistics.json')
        
        self.logger.info("Data update completed")
        
        return {
            'spor_toto_matches': len(spor_toto_matches),
            'historical_matches': len(historical_data),
            'team_stats': len(team_stats)
        }

class DataValidator:
    """
    Validate scraped data for quality and completeness
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_matches_data(self, df: pd.DataFrame) -> Dict:
        """Validate match data"""
        
        issues = []
        
        # Check required columns
        required_cols = ['home_team', 'away_team', 'home_score', 'away_score', 'date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
        
        # Check for missing values
        missing_values = df[required_cols].isnull().sum()
        if missing_values.any():
            issues.append(f"Missing values: {missing_values.to_dict()}")
        
        # Check score validity
        if 'home_score' in df.columns and 'away_score' in df.columns:
            invalid_scores = df[
                (df['home_score'] < 0) | (df['away_score'] < 0) |
                (df['home_score'] > 10) | (df['away_score'] > 10)
            ]
            if len(invalid_scores) > 0:
                issues.append(f"Invalid scores found: {len(invalid_scores)} matches")
        
        # Check date format
        if 'date' in df.columns:
            try:
                pd.to_datetime(df['date'])
            except:
                issues.append("Invalid date format found")
        
        validation_result = {
            'total_matches': len(df),
            'issues_found': len(issues),
            'issues': issues,
            'data_quality_score': max(0, 100 - len(issues) * 10)
        }
        
        return validation_result
