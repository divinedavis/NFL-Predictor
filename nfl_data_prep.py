import pandas as pd
import numpy as np
import os
from datetime import datetime

class NFLDataPreprocessor:
    def __init__(self, data_dir='nfl_data'):
        self.data_dir = os.path.join(os.getcwd(), data_dir)
        self.games_df = None
    
    def load_data(self):
        """Load games data."""
        try:
            games_file = os.path.join(self.data_dir, 'nfl_2023_games.csv')
            if os.path.exists(games_file):
                self.games_df = pd.read_csv(games_file)
                self.games_df['date'] = pd.to_datetime(self.games_df['date'])
                print(f"Loaded {len(self.games_df)} games")
                return True
            else:
                print("Games file not found")
                return False
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
            
    def get_head_to_head_history(self, team1, team2):
        """Get history of games between two specific teams."""
        if self.games_df is None:
            print("No data loaded")
            return pd.DataFrame()
            
        # Find games between these teams
        matches = self.games_df[
            ((self.games_df['winner'] == team1) & (self.games_df['loser'] == team2)) |
            ((self.games_df['winner'] == team2) & (self.games_df['loser'] == team1))
        ].sort_values('date')
        
        print(f"\nHead-to-head history between {team1} and {team2}:")
        print(f"Total games found: {len(matches)}")
        
        if len(matches) > 0:
            print("\nMatch History:")
            for _, game in matches.iterrows():
                date = game['date'].strftime('%Y-%m-%d')
                winner = game['winner']
                loser = game['loser']
                winner_pts = game['winner_pts']
                loser_pts = game['loser_pts']
                print(f"{date}: {winner} ({winner_pts}) def. {loser} ({loser_pts})")
                
        return matches