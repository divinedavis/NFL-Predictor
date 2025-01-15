from scraper_class import PFRScraper
import os

def main():
    print("Starting NFL data scraper...")
    
    # Create nfl_data directory if it doesn't exist
    if not os.path.exists('nfl_data'):
        os.makedirs('nfl_data')
        print("Created nfl_data directory")
    
    # Initialize scraper
    scraper = PFRScraper()
    
    try:
        # Scrape just 2023 season
        print("\nScraping 2023 season games data...")
        year = 2023
        
        # Get games data
        games_df = scraper.scrape_game_scores(year)
        
        # Save to CSV
        games_filename = os.path.join('nfl_data', f'nfl_{year}_games.csv')
        games_df.to_csv(games_filename, index=False)
        print(f"\nSaved games data to: {games_filename}")
        print(f"Total games saved: {len(games_df)}")
        
        print("\nScraping completed successfully!")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()