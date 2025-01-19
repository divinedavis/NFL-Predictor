from nfl_data_prep import NFLDataPreprocessor

def get_common_opponents(games_df, team1, team2):
    """Get list of common opponents and their games"""
    # Get all opponents for team1
    team1_games = games_df[
        (games_df['winner'] == team1) | (games_df['loser'] == team1)
    ]
    team1_opponents = set()
    for _, game in team1_games.iterrows():
        if game['winner'] == team1:
            team1_opponents.add(game['loser'])
        else:
            team1_opponents.add(game['winner'])
            
    # Get all opponents for team2
    team2_games = games_df[
        (games_df['winner'] == team2) | (games_df['loser'] == team2)
    ]
    team2_opponents = set()
    for _, game in team2_games.iterrows():
        if game['winner'] == team2:
            team2_opponents.add(game['loser'])
        else:
            team2_opponents.add(game['winner'])
    
    # Find common opponents
    common = team1_opponents.intersection(team2_opponents)
    # Remove the teams themselves
    common = common - {team1, team2}
    return sorted(list(common))

def show_matchups_against_opponent(games_df, team1, team2, opponent):
    """Show how both teams performed against a specific opponent"""
    print(f"\nGames against {opponent}:")
    
    # Get team1's games against opponent
    team1_games = games_df[
        ((games_df['winner'] == team1) & (games_df['loser'] == opponent)) |
        ((games_df['winner'] == opponent) & (games_df['loser'] == team1))
    ].sort_values('date')
    
    print(f"\n{team1} vs {opponent}:")
    for _, game in team1_games.iterrows():
        date = game['date'].strftime('%Y-%m-%d')
        if game['winner'] == team1:
            print(f"{date}: {team1} WON {game['winner_pts']}-{game['loser_pts']}")
        else:
            print(f"{date}: {team1} LOST {game['loser_pts']}-{game['winner_pts']}")
    
    # Get team2's games against opponent
    team2_games = games_df[
        ((games_df['winner'] == team2) & (games_df['loser'] == opponent)) |
        ((games_df['winner'] == opponent) & (games_df['loser'] == team2))
    ].sort_values('date')
    
    print(f"\n{team2} vs {opponent}:")
    for _, game in team2_games.iterrows():
        date = game['date'].strftime('%Y-%m-%d')
        if game['winner'] == team2:
            print(f"{date}: {team2} WON {game['winner_pts']}-{game['loser_pts']}")
        else:
            print(f"{date}: {team2} LOST {game['loser_pts']}-{game['winner_pts']}")
    
    # Compare results
    team1_won = any(game['winner'] == team1 for _, game in team1_games.iterrows())
    team2_won = any(game['winner'] == team2 for _, game in team2_games.iterrows())
    
    if team1_won and not team2_won:
        print(f"\nPoint to {team1} (beat team that {team2} lost to)")
        return 1, 0
    elif team2_won and not team1_won:
        print(f"\nPoint to {team2} (beat team that {team1} lost to)")
        return 0, 1
    else:
        print("\nNo points awarded (similar results)")
        return 0, 0

def main():
    # Initialize preprocessor
    preprocessor = NFLDataPreprocessor()
    
    # Load data
    if not preprocessor.load_data():
        print("Failed to load data")
        return
    
    # Teams to analyze
    team1 = "New York Giants"
    team2 = "Philadelphia Eagles"
    
    # Find common opponents
    common_opponents = get_common_opponents(preprocessor.games_df, team1, team2)
    print(f"\nFound {len(common_opponents)} common opponents:")
    for opponent in common_opponents:
        print(f"- {opponent}")
    
    # Analyze each common opponent
    print("\nAnalyzing results against common opponents:")
    team1_points = 0
    team2_points = 0
    
    for opponent in common_opponents:
        t1_points, t2_points = show_matchups_against_opponent(
            preprocessor.games_df, team1, team2, opponent
        )
        team1_points += t1_points
        team2_points += t2_points
    
    # Show final results
    print(f"\nFinal Score:")
    print(f"{team1}: {team1_points} points")
    print(f"{team2}: {team2_points} points")
    
    # Make prediction
    print("\nPrediction:")
    if team1_points > team2_points:
        print(f"{team1} predicted to win (+{team1_points-team2_points} points)")
    elif team2_points > team1_points:
        print(f"{team2} predicted to win (+{team2_points-team1_points} points)")
    else:
        print("Even matchup")

if __name__ == "__main__":
    main()