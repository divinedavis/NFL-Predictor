import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from io import StringIO

class PFRScraper:
    def __init__(self):
        self.base_url = "https://www.pro-football-reference.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _get_soup(self, url):
        """Make request and return BeautifulSoup object with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(5 * (attempt + 1))
    
    def scrape_game_scores(self, year):
        """Scrape game scores and basic stats from season schedule."""
        print(f"Scraping {year} game scores...")
        url = f"{self.base_url}/years/{year}/games.htm"
        
        soup = self._get_soup(url)
        games_table = soup.find('table', {'id': 'games'})
        
        if not games_table:
            raise ValueError(f"Could not find games table for {year}")
        
        df = pd.read_html(StringIO(str(games_table)))[0]
        
        # Clean up column names
        df.columns = df.columns.str.lower().str.replace('/', '_').str.replace(' ', '_')
        
        # Remove any header rows
        df = df[df['date'] != 'Date']
        
        # Rename columns to match expected format
        df = df.rename(columns={
            'winner_tie': 'winner',
            'loser_tie': 'loser',
            'pts.1': 'winner_pts',
            'pts.2': 'loser_pts',
            'yds.1': 'winner_yards',
            'yds.2': 'loser_yards',
            'to.1': 'winner_turnovers',
            'to.2': 'loser_turnovers'
        })
        
        # Convert date
        df['date'] = pd.to_datetime(df['date'].astype(str))
        
        print(f"Successfully processed {len(df)} games")
        return df