import pandas as pd
import os

def examine_games_file():
    print("\n=== Examining Games Data ===")
    
    games_file = os.path.join('nfl_data', 'nfl_2023_games.csv')
    
    # First show raw contents
    print("\nRaw contents of first few lines:")
    with open(games_file, 'r') as f:
        print(f.readline().strip())  # Header line
        for _ in range(3):           # First 3 data lines
            print(f.readline().strip())
            
    # Now load with pandas
    games_df = pd.read_csv(games_file)
    print("\nColumn names from pandas:")
    print(games_df.columns.tolist())
    
    print("\nFirst few rows:")
    print(games_df.head())
    
    return games_df

if __name__ == "__main__":
    games_df = examine_games_file()