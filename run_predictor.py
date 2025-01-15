from nfl_data_prep import NFLDataPreprocessor
import pandas as pd

def main():
    # Initialize preprocessor
    preprocessor = NFLDataPreprocessor()
    
    # Load data
    if not preprocessor.load_data():
        print("Failed to load data")
        return
    
    # Set teams to analyze
    team1 = "Dallas Cowboys"
    team2 = "Philadelphia Eagles"
    print(f"\nAnalyzing matchups between {team1} and {team2}")
    
    # Find all games between these teams
    matches = preprocessor.games_df[
        ((preprocessor.games_df['winner'] == team1) & (preprocessor.games_df['loser'] == team2)) |
        ((preprocessor.games_df['winner'] == team2) & (preprocessor.games_df['loser'] == team1))
    ].sort_values('date')
    
    print(f"\nFound {len(matches)} games between these teams")
    
    if len(matches) > 0:
        # Show each game
        print("\nGame History:")
        for _, game in matches.iterrows():
            date = game['date'].strftime('%Y-%m-%d')
            winner = game['winner']
            loser = game['loser']
            winner_pts = game['winner_pts']
            loser_pts = game['loser_pts']
            print(f"{date}: {winner} ({winner_pts}) def. {loser} ({loser_pts})")
        
        # Calculate win percentages
        team1_wins = len(matches[matches['winner'] == team1])
        team2_wins = len(matches[matches['winner'] == team2])
        total_games = len(matches)
        
        team1_pct = (team1_wins / total_games) * 100
        team2_pct = (team2_wins / total_games) * 100
        
        print(f"\nHistorical Record:")
        print(f"{team1}: {team1_wins} wins ({team1_pct:.1f}%)")
        print(f"{team2}: {team2_wins} wins ({team2_pct:.1f}%)")
        
        # Make prediction
        print(f"\nPrediction for next matchup:")
        if team1_wins > team2_wins:
            print(f"{team1} is favored to win ({team1_pct:.1f}% chance)")
        elif team2_wins > team1_wins:
            print(f"{team2} is favored to win ({team2_pct:.1f}% chance)")
        else:
            print("Teams are evenly matched (50% chance each)")
            
    else:
        print("No games found between these teams")

if __name__ == "__main__":
    main()