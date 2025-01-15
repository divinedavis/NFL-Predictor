# Set these environment variables before importing tensorflow
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Now import the rest
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from nfl_data_prep import NFLDataPreprocessor
from nfl_predictor import NFLPredictor
import pandas as pd
from datetime import datetime

def main():
    try:
        # Initialize data preprocessor
        print("\n=== Loading NFL Data ===")
        preprocessor = NFLDataPreprocessor()
        
        # Load data
        if not preprocessor.load_data():
            raise ValueError("Failed to load data")
        
        # Prepare features
        print("\n=== Preparing Features ===")
        X, y = preprocessor.prepare_features(lookback_games=5)
        print(f"Total samples: {len(X)}")
        print(f"Feature dimensions: {X.shape}")
        
        # Create and train model
        print("\n=== Training Model ===")
        predictor = NFLPredictor()
        history = predictor.train(X, y, epochs=100, batch_size=32)
        
        # Save results
        print("\n=== Saving Results ===")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save metrics
        metrics = {
            'final_loss': history.history['loss'][-1],
            'final_accuracy': history.history['accuracy'][-1],
            'val_loss': history.history['val_loss'][-1],
            'val_accuracy': history.history['val_accuracy'][-1],
            'total_samples': len(X),
            'feature_dimensions': X.shape[1]
        }
        
        metrics_df = pd.DataFrame([metrics])
        metrics_filename = f'model_metrics_{timestamp}.csv'
        metrics_df.to_csv(metrics_filename, index=False)
        
        # Plot training history
        predictor.plot_training_history()
        
        print(f"\nModel Performance:")
        print(f"Training Accuracy: {metrics['final_accuracy']:.4f}")
        print(f"Validation Accuracy: {metrics['val_accuracy']:.4f}")
        print(f"\nResults saved to:")
        print(f"- Metrics: {metrics_filename}")
        print(f"- Training plot: training_history_{timestamp}.png")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()