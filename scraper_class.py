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

    def _read_table(self, table):
        """Safely read an HTML table using StringIO."""
        return pd.read_html(StringIO(str(table)))[0]

    def scrape_game_scores(self, year):
        """Scrape game scores and basic stats from season schedule."""
        print(f"Scraping {year} game scores...")
        url = f"{self.base_url}/years/{year}/games.htm"
        
        soup = self._get_soup(url)
        games_table = soup.find('table', {'id': 'games'})
        
        if not games_table:
            raise ValueError(f"Could not find games table for {year}")
        
        df = self._read_table(games_table)
        
        print("\nRaw data preview:")
        print(df.head())
        print("\nColumn names:", df.columns.tolist())
        
        # Clean up column names
        df.columns = df.columns.str.lower().str.replace('/', '_').str.replace(' ', '_')
        
        # Remove any rows that are actually headers
        header_indicators = ['Date', 'Week', 'Day']
        for indicator in header_indicators:
            df = df[~df.isin([indicator]).any(axis=1)]
        
        # Rename columns to be more clear
        df = df.rename(columns={
            'winner_tie': 'winner',
            'loser_tie': 'loser',
            'ptsw': 'winner_pts',
            'ptsl': 'loser_pts',
            'ydsw': 'winner_yards',
            'ydsl': 'loser_yards',
            'tow': 'winner_turnovers',
            'tol': 'loser_turnovers'
        })
        
        # Remove any rows where 'date' is 'Date' (header rows)
        df = df[df['date'] != 'Date']
        
        # Convert date string to datetime, using a flexible format
        try:
            df['date'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='mixed')
        except Exception as e:
            print(f"Error converting dates: {e}")
            print("Sample of date values:", df['date'].head())
            raise
        
        # Drop any rows where essential data is missing
        df = df.dropna(subset=['week', 'winner', 'loser', 'winner_pts', 'loser_pts'])
        
        print(f"Successfully processed {len(df)} games")
        return df

    def scrape_team_stats(self, year):
        """Scrape team stats from conference tables."""
        print(f"Scraping {year} team stats...")
        url = f"{self.base_url}/years/{year}"
        
        try:
            soup = self._get_soup(url)
            
            # Get AFC and NFC tables
            afc_table = soup.find('table', {'id': 'AFC'})
            nfc_table = soup.find('table', {'id': 'NFC'})
            
            team_stats = []
            
            if afc_table:
                afc_df = self._read_table(afc_table)
                afc_df['Conference'] = 'AFC'
                team_stats.append(afc_df)
                print("Found AFC table")
            
            if nfc_table:
                nfc_df = self._read_table(nfc_table)
                nfc_df['Conference'] = 'NFC'
                team_stats.append(nfc_df)
                print("Found NFC table")
            
            if team_stats:
                # Combine conference tables
                stats_df = pd.concat(team_stats, ignore_index=True)
                
                # Clean up column names
                stats_df.columns = stats_df.columns.str.lower().str.replace(' ', '_')
                
                # Remove any header rows
                if 'team' in stats_df.columns:
                    stats_df = stats_df[stats_df['team'] != 'Team']
                
                print(f"Successfully processed team stats for {len(stats_df)} teams")
                return stats_df
            else:
                print("Could not find conference tables")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error scraping team stats: {e}")
            return pd.DataFrame()

    def scrape_player_stats(self, year):
        """Scrape individual player statistics for the season."""
        print(f"Scraping {year} player stats...")
        
        stats_types = {
            'passing': 'passing',
            'rushing': 'rushing',
            'receiving': 'receiving',
            'defense': 'defense',
            'kicking': 'kicking'
        }
        
        player_stats = {}
        
        for stat_type, url_suffix in stats_types.items():
            url = f"{self.base_url}/years/{year}/{url_suffix}.htm"
            print(f"\nProcessing {stat_type} stats...")
            
            try:
                soup = self._get_soup(url)
                stats_table = soup.find('table', {'id': f'{stat_type}'})
                
                if stats_table:
                    df = self._read_table(stats_table)
                    
                    # Print column information for debugging
                    print(f"Original columns type: {type(df.columns)}")
                    print(f"Original columns: {list(df.columns)}")
                    
                    # Handle multi-level columns
                    if isinstance(df.columns, pd.MultiIndex):
                        # Create mapping for unnamed columns
                        unnamed_map = {
                            'Rk': 'rank',
                            'Player': 'player',
                            'Tm': 'team',
                            'Age': 'age',
                            'Pos': 'position',
                        }
                        
                        new_cols = []
                        for col in df.columns:
                            if isinstance(col, tuple):
                                # Handle unnamed columns first
                                if col[0].startswith('Unnamed'):
                                    new_cols.append(f"{stat_type}_{unnamed_map.get(col[1], col[1].lower())}")
                                else:
                                    # For regular columns, combine both levels if they're different
                                    level0 = col[0].lower().replace(' ', '_')
                                    level1 = col[1].lower().replace(' ', '_')
                                    if level0 == level1:
                                        new_cols.append(f"{stat_type}_{level0}")
                                    else:
                                        new_cols.append(f"{stat_type}_{level0}_{level1}")
                            else:
                                new_cols.append(f"{stat_type}_{str(col).lower()}")
                        
                        # Clean up special characters
                        new_cols = [col.replace('+', 'plus').replace('%', 'pct').replace('-', '_to_') 
                                  for col in new_cols]
                        
                        print(f"\nNew column names for {stat_type}:")
                        print(new_cols)
                        
                        df.columns = new_cols
                    else:
                        # For single-level columns
                        new_cols = [f"{stat_type}_{str(col)}".lower() for col in df.columns]
                    
                    # Clean up column names
                    new_cols = [col.replace(' ', '_').replace('%', 'pct').replace('+', 'plus')
                               for col in new_cols]
                    
                    # Set the new column names
                    df.columns = new_cols
                    
                    # Remove header rows and clean data
                    first_col = df.columns[0]
                    df = df[pd.to_numeric(df[first_col], errors='coerce').notna()]
                    
                    # Convert numeric columns
                    for col in df.columns:
                        try:
                            df[col] = pd.to_numeric(df[col])
                        except (ValueError, TypeError):
                            # Keep as is if conversion fails
                            continue
                    
                    player_stats[stat_type] = df
                    print(f"Successfully scraped {stat_type} stats: {len(df)} players")
                else:
                    print(f"No table found for {stat_type}")
                
                time.sleep(3)  # Be nice to the server
                
            except Exception as e:
                print(f"Error scraping {stat_type} stats: {e}")
                import traceback
                print(traceback.format_exc())
        
        return player_stats

    def scrape_full_season(self, year, include_player_stats=True):
        """Scrape complete season data including games, team stats, and optionally player stats."""
        season_data = {
            'games': self.scrape_game_scores(year),
            'team_stats': self.scrape_team_stats(year)
        }
        
        if include_player_stats:
            season_data['player_stats'] = self.scrape_player_stats(year)
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save game data
            if 'games' in season_data and not season_data['games'].empty:
                games_filename = f'nfl_{year}_games_{timestamp}.csv'
                print(f"\nSaving game data to: {games_filename}")
                season_data['games'].to_csv(games_filename, index=False)
                print(f"Successfully saved {len(season_data['games'])} games")
            
            # Save team stats
            if 'team_stats' in season_data and not season_data['team_stats'].empty:
                team_stats_filename = f'nfl_{year}_team_stats_{timestamp}.csv'
                print(f"Saving team stats to: {team_stats_filename}")
                season_data['team_stats'].to_csv(team_stats_filename, index=False)
                print(f"Successfully saved team stats")
            
            # Save player stats
            if include_player_stats and 'player_stats' in season_data:
                for stat_type, df in season_data['player_stats'].items():
                    if not df.empty:
                        player_filename = f'nfl_{year}_player_{stat_type}_{timestamp}.csv'
                        print(f"Saving {stat_type} stats to: {player_filename}")
                        df.to_csv(player_filename, index=False)
                        print(f"Successfully saved {len(df)} {stat_type} player records")
            
            print(f"\nAll files saved successfully for {year} season")
            
        except Exception as e:
            print(f"Error saving files for {year} season: {e}")
            import traceback
            print(traceback.format_exc())
        
        return season_data

    def scrape_multiple_seasons(self, start_year, end_year, include_player_stats=True):
        """Scrape data for multiple seasons."""
        all_seasons = {}
        
        for year in range(start_year, end_year + 1):
            try:
                print(f"\nScraping {year} season...")
                all_seasons[year] = self.scrape_full_season(year, include_player_stats)
                time.sleep(5)
            except Exception as e:
                print(f"Error scraping {year} season: {e}")
                continue
        
        return all_seasons