import os
from collections import defaultdict

def cleanup_nfl_data_folder(data_dir):
    """Clean up the NFL data folder by keeping only the most recent version of each file type."""
    print("Starting cleanup...")
    
    # Group files by type
    file_groups = defaultdict(list)
    total_files = 0
    
    for file in os.listdir(data_dir):
        if file.endswith('.csv'):
            if file.startswith('debug'):
                # Delete all debug files
                os.remove(os.path.join(data_dir, file))
                print(f"Removed debug file: {file}")
                continue
            
            # Group files by their base type
            if 'player' in file:
                # For player stats, group by type (passing, rushing, etc.)
                stat_type = file.split('player_')[1].split('_')[0]
                base_type = f'player_{stat_type}'
            else:
                # For other files, group by main type (games, team_stats)
                base_type = file.split('_20')[0]
            
            file_groups[base_type].append(file)
            total_files += 1
    
    # Keep only the most recent file in each group
    kept_files = 0
    removed_files = 0
    
    for base_type, files in file_groups.items():
        if len(files) > 0:
            # Sort files by timestamp (most recent last)
            files.sort()
            
            # Keep the most recent file
            keep_file = files[-1]
            kept_files += 1
            
            # Remove older files
            for file in files[:-1]:
                try:
                    os.remove(os.path.join(data_dir, file))
                    print(f"Removed old file: {file}")
                    removed_files += 1
                except Exception as e:
                    print(f"Error removing {file}: {str(e)}")
    
    print("\nCleanup Summary:")
    print(f"Total files processed: {total_files}")
    print(f"Files kept: {kept_files}")
    print(f"Files removed: {removed_files}")
    print("\nKept files:")
    for file in os.listdir(data_dir):
        if file.endswith('.csv'):
            print(f"- {file}")

if __name__ == "__main__":
    data_dir = "nfl_data"  # Update this path if needed
    cleanup_nfl_data_folder(data_dir)