from nfl_data_prep import NFLDataPreprocessor

def get_all_teams(games_df):
    """Get list of all teams"""
    teams = set()
    for team in games_df['winner'].unique():
        teams.add(team)
    for team in games_df['loser'].unique():
        teams.add(team)
    return sorted(list(teams))

def analyze_team_performance(games_df, team1, team2):
    """Compare two teams based on common opponents"""
    team1_points = 0
    team2_points = 0
    
    # Get results for each team
    team1_games = games_df[
        (games_df['winner'] == team1) | (games_df['loser'] == team1)
    ]
    team2_games = games_df[
        (games_df['winner'] == team2) | (games_df['loser'] == team2)
    ]
    
    # Get opponents for each team
    team1_opponents = set()
    team2_opponents = set()
    
    for _, game in team1_games.iterrows():
        if game['winner'] == team1:
            team1_opponents.add(game['loser'])
        else:
            team1_opponents.add(game['winner'])
            
    for _, game in team2_games.iterrows():
        if game['winner'] == team2:
            team2_opponents.add(game['loser'])
        else:
            team2_opponents.add(game['winner'])
            
    # Find common opponents
    common_opponents = team1_opponents.intersection(team2_opponents) - {team1, team2}
    
    # For each common opponent
    for opponent in common_opponents:
        team1_won = any(
            game['winner'] == team1 
            for _, game in team1_games[
                (team1_games['winner'] == team1) & (team1_games['loser'] == opponent) |
                (team1_games['winner'] == opponent) & (team1_games['loser'] == team1)
            ].iterrows()
        )
        
        team2_won = any(
            game['winner'] == team2 
            for _, game in team2_games[
                (team2_games['winner'] == team2) & (team2_games['loser'] == opponent) |
                (team2_games['winner'] == opponent) & (team2_games['loser'] == team2)
            ].iterrows()
        )
        
        if team1_won and not team2_won:
            team1_points += 1
        elif team2_won and not team1_won:
            team2_points += 1
            
    return team1_points, team2_points

def main():
    # Initialize preprocessor
    preprocessor = NFLDataPreprocessor()
    
    # Load data
    if not preprocessor.load_data():
        print("Failed to load data")
        return
    
    # Get all teams
    teams = get_all_teams(preprocessor.games_df)
    
    # Calculate scores for each team
    team_scores = {team: 0 for team in teams}
    games_compared = {team: 0 for team in teams}
    
    print("\nCalculating scores based on common opponent performance...")
    
    # Compare each team with every other team
    for i, team1 in enumerate(teams):
        for team2 in teams[i+1:]:
            team1_points, team2_points = analyze_team_performance(
                preprocessor.games_df, team1, team2
            )
            team_scores[team1] += team1_points
            team_scores[team2] += team2_points
            games_compared[team1] += 1
            games_compared[team2] += 1
    
    # Sort teams by score
    sorted_teams = sorted(
        teams,
        key=lambda x: (
            team_scores[x] / games_compared[x] if games_compared[x] > 0 else 0
        ),
        reverse=True
    )
    
    print("\nFinal Team Rankings (based on common opponent performance):")
    print("========================================================")
    for rank, team in enumerate(sorted_teams, 1):
        avg_score = team_scores[team] / games_compared[team] if games_compared[team] > 0 else 0
        print(f"{rank}. {team:<30} Score: {team_scores[team]:>3} points in {games_compared[team]:>2} comparisons (Avg: {avg_score:.2f})")

if __name__ == "__main__":
    main()