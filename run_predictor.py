from nfl_data_prep import NFLDataPreprocessor
import pandas as pd

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

def get_all_teams(games_df):
    """Get list of all teams"""
    teams = set(pd.concat([games_df['winner'], games_df['loser']]))
    return sorted(list(teams))

def analyze_common_opponents(games_df, team1, team2):
    """Analyze how two teams performed against common opponents"""
    team1_results = get_team_results(games_df, team1)
    team2_results = get_team_results(games_df, team2)
    
    common_opponents = set(team1_results.keys()) & set(team2_results.keys())
    common_opponents = common_opponents - {team1, team2}  # Remove the teams themselves
    
    team1_points = 0
    team2_points = 0
    
    analysis = f"\n{team1} vs {team2}\n"
    analysis += "Common opponents:\n"
    
    for opponent in sorted(common_opponents):
        analysis += f"- {opponent}\n"
        team1_result = team1_results[opponent]
        team2_result = team2_results[opponent]
        
        if team1_result == 'won' and team2_result == 'lost':
            team1_points += 1
            analysis += f"  {team1} beat {opponent} ({team2} lost) -> {team1} +1\n"
        elif team2_result == 'won' and team1_result == 'lost':
            team2_points += 1
            analysis += f"  {team2} beat {opponent} ({team1} lost) -> {team2} +1\n"
    
    analysis += f"\nResults:\n"
    analysis += f"{team1}: {team1_points} points\n"
    analysis += f"{team2}: {team2_points} points\n"
    
    prediction = ""
    if team1_points > team2_points:
        prediction = f"{team1} predicted to win (+{team1_points-team2_points} points)"
    elif team2_points > team1_points:
        prediction = f"{team2} predicted to win (+{team2_points-team1_points} points)"
    else:
        prediction = "Even matchup"
    
    analysis += f"Prediction: {prediction}\n"
    
    return {
        'team1': team1,
        'team2': team2,
        'team1_points': team1_points,
        'team2_points': team2_points,
        'common_opponents': len(common_opponents),
        'prediction': prediction,
        'analysis': analysis
    }

def main():
    # Initialize preprocessor
    preprocessor = NFLDataPreprocessor()
    
    # Load data
    if not preprocessor.load_data():
        print("Failed to load data")
        return
    
    # Get all teams
    teams = get_all_teams(preprocessor.games_df)
    print(f"\nAnalyzing {len(teams)} teams:")
    for team in teams:
        print(f"- {team}")
    
    # Analyze all possible matchups
    print("\nAnalyzing all matchups...")
    results = []
    
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            team1 = teams[i]
            team2 = teams[j]
            
            analysis = analyze_common_opponents(preprocessor.games_df, team1, team2)
            if analysis['common_opponents'] > 0:  # Only show if they have common opponents
                print(analysis['analysis'])
                results.append(analysis)
    
    # Summary
    print("\nSummary of Predictions:")
    print("=====================")
    for result in results:
        print(f"{result['team1']} vs {result['team2']}: {result['prediction']}")

if __name__ == "__main__":
    main()