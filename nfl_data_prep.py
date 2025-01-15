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

    def prepare_features(self, lookback_games=5):
        """Prepare features using only win/loss history."""
        if self.games_df is None:
            raise ValueError("No games data loaded")
        
        print("\n=== Preparing Features ===")
        print(f"Using {lookback_games} previous games for each team")
        
        features = []
        targets = []
        skipped_games = 0
        
        # Sort games by date
        self.games_df = self.games_df.sort_values('date')
        
        print("\nProcessing games...")
        for idx, game in self.games_df.iterrows():
            try:
                # Get teams
                winner = game['winner']
                loser = game['loser']
                game_date = game['date']
                
                print(f"\nProcessing game: {winner} vs {loser} on {game_date.date()}")
                
                # Get features for both teams
                winner_features = self._get_team_features(winner, game_date, lookback_games)
                loser_features = self._get_team_features(loser, game_date, lookback_games)
                
                if winner_features is not None and loser_features is not None:
                    # Combine features
                    game_features = np.concatenate([winner_features, loser_features])
                    features.append(game_features)
                    targets.append(1)  # 1 for winner
                    print("Successfully processed")
                else:
                    skipped_games += 1
                    print("Skipped - insufficient history")
            
            except Exception as e:
                print(f"Error processing game: {str(e)}")
                skipped_games += 1
        
        print(f"\nFeature preparation complete:")
        print(f"Processed games: {len(features)}")
        print(f"Skipped games: {skipped_games}")
        
        if len(features) == 0:
            raise ValueError("No valid features could be created")
            
        return np.array(features), np.array(targets)

    def _get_team_features(self, team, game_date, lookback_games):
        """Get win/loss history for a team."""
        # Get previous games for the team
        prev_games = self.games_df[
            ((self.games_df['winner'] == team) | (self.games_df['loser'] == team)) &
            (self.games_df['date'] < game_date)
        ].tail(lookback_games)
        
        if len(prev_games) < lookback_games:
            return None  # Not enough history
        
        # Create features array (1 for win, 0 for loss)
        features = []
        for _, prev_game in prev_games.iterrows():
            won = prev_game['winner'] == team
            features.append(1 if won else 0)
        
        return np.array(features)