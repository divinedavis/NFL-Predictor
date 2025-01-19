from scraper_class import PFRScraper
import os

def main():
    # Create nfl_data directory if it doesn't exist
    if not os.path.exists('nfl_data'):
        os.makedirs('nfl_data')
        print("Created nfl_data directory")
    
    # Initialize scraper
    scraper = PFRScraper()
    
    try:
        # Scrape 2022 season
        print("\nScraping 2022 season...")
        year = 2022
        
        # Get games data
        games_df = scraper.scrape_game_scores(year)
        
        # Save to CSV
        games_filename = os.path.join('nfl_data', f'nfl_{year}_games.csv')
        games_df.to_csv(games_filename, index=False)
        print(f"\nSaved games data to: {games_filename}")
        print(f"Total games saved: {len(games_df)}")
        
        print("\nScraping completed successfully!")
        
        # Show date range
        if not games_df.empty:
            print("\nDate range of games:")
            print(f"First game: {games_df['date'].min()}")
            print(f"Last game: {games_df['date'].max()}")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()