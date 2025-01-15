import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class NFLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.history = None
    
    def build_model(self, input_dim):
        """Build a simple neural network for win/loss prediction."""
        model = Sequential([
            # Input layer
            Dense(8, activation='relu', input_dim=input_dim),
            Dropout(0.3),
            
            # Output layer
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        print("\nModel Architecture:")
        model.summary()
        
        return model
    
    def train(self, X, y, validation_split=0.2, epochs=50, batch_size=32):
        """Train the model."""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, 
            test_size=validation_split, 
            random_state=42,
            stratify=y
        )
        
        print(f"\nUsing {X.shape[1]} previous games as features")
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        
        # Build model
        if self.model is None:
            self.model = self.build_model(X.shape[1])
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        # Evaluate model
        train_loss, train_acc = self.model.evaluate(X_train, y_train, verbose=0)
        val_loss, val_acc = self.model.evaluate(X_val, y_val, verbose=0)
        
        print("\nFinal Model Performance:")
        print(f"Training - Loss: {train_loss:.4f}, Accuracy: {train_acc:.4f}")
        print(f"Validation - Loss: {val_loss:.4f}, Accuracy: {val_acc:.4f}")
        
        return self.history
    
    def plot_training_history(self):
        """Plot training history."""
        if self.history is None:
            raise ValueError("Model hasn't been trained yet")
        
        plt.figure(figsize=(12, 4))
        
        # Plot loss
        plt.subplot(1, 2, 1)
        plt.plot(self.history.history['loss'], label='Training Loss')
        plt.plot(self.history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Plot accuracy
        plt.subplot(1, 2, 2)
        plt.plot(self.history.history['accuracy'], label='Training Accuracy')
        plt.plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(f'training_history_{timestamp}.png')
        plt.close()

    def predict_game(self, team1_history, team2_history):
        """Predict game outcome from team histories."""
        if self.model is None:
            raise ValueError("Model needs to be trained first")
        
        # Combine team histories
        features = np.concatenate([team1_history, team2_history])
        features = self.scaler.transform(features.reshape(1, -1))
        
        # Make prediction
        prediction = self.model.predict(features)[0][0]
        
        return {
            'team1_win_probability': prediction,
            'team2_win_probability': 1 - prediction,
            'predicted_winner': 'Team 1' if prediction > 0.5 else 'Team 2'
        }