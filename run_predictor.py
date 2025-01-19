from nfl_data_prep import NFLDataPreprocessor

def get_team_results(games_df, team):
    """Get wins and losses for a team with opponents"""
    results = {}
    team_games = games_df[
        (games_df['winner'] == team) | (games_df['loser'] == team)
    ]
    
    for _, game in team_games.iterrows():
        opponent = game['loser'] if game['winner'] == team else game['winner']
        won = game['winner'] == team
        results[opponent] = 'won' if won else 'lost'
    
    return results

def main():
    # Initialize preprocessor
    preprocessor = NFLDataPreprocessor()
    
    # Load data
    if not preprocessor.load_data():
        print("Failed to load data")
        return
    
    # Teams to analyze
    cowboys = "Dallas Cowboys"
    eagles = "Philadelphia Eagles"
    
    # Get results for each team
    cowboys_results = get_team_results(preprocessor.games_df, cowboys)
    eagles_results = get_team_results(preprocessor.games_df, eagles)
    
    # Find common opponents
    common_opponents = set(cowboys_results.keys()) & set(eagles_results.keys())
    
    print(f"\nCommon Opponents:")
    for opponent in sorted(common_opponents):
        if opponent not in [cowboys, eagles]:  # Exclude direct matchups
            print(f"- {opponent}")
    
    print(f"\nCommon Opponent Analysis:")
    print("-------------------------")
    
    cowboys_points = 0
    eagles_points = 0
    
    for opponent in sorted(common_opponents):
        if opponent not in [cowboys, eagles]:  # Exclude direct matchups
            cowboys_result = cowboys_results[opponent]
            eagles_result = eagles_results[opponent]
            
            # Detailed logging for each opponent
            print(f"\nAnalyzing {opponent}:")
            print(f"  Cowboys result: {cowboys_result}")
            print(f"  Eagles result: {eagles_result}")
            
            if cowboys_result == 'won' and eagles_result == 'lost':
                cowboys_points += 1
                print(f"  Cowboys beat {opponent} (Eagles lost) -> Cowboys +1")
            elif eagles_result == 'won' and cowboys_result == 'lost':
                eagles_points += 1
                print(f"  Eagles beat {opponent} (Cowboys lost) -> Eagles +1")
            else:
                print("  No points awarded")
    
    print("\nFinal Score:")
    print(f"Cowboys: {cowboys_points} points")
    print(f"Eagles: {eagles_points} points")
    
    # Make prediction based on points
    print("\nPrediction:")
    if cowboys_points > eagles_points:
        print(f"Cowboys performed better against common opponents (+{cowboys_points-eagles_points} points)")
    elif eagles_points > cowboys_points:
        print(f"Eagles performed better against common opponents (+{eagles_points-cowboys_points} points)")
    else:
        print("Teams performed equally against common opponents")

if __name__ == "__main__":
    main()