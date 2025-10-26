"""
Autoencoder model for anomaly detection
"""

import numpy as np
import logging
from typing import Tuple, Optional
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf

logger = logging.getLogger(__name__)


class AutoencoderModel:
    """Autoencoder neural network for anomaly detection"""
    
    def __init__(self, input_dim: int, encoding_dim: int = 32, 
                 hidden_layers: list = None):
        """Initialize Autoencoder model
        
        Args:
            input_dim: Number of input features
            encoding_dim: Dimension of encoded representation
            hidden_layers: List of hidden layer sizes
        """
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.hidden_layers = hidden_layers or [64, 32, 16]
        self.model = None
        self.threshold = None
        
        logger.info(f"Autoencoder initialized with input_dim={input_dim}, "
                   f"encoding_dim={encoding_dim}")
    
    def build_model(self) -> Model:
        """Build the Autoencoder model architecture
        
        Returns:
            Keras Model
        """
        # Input layer
        input_layer = keras.Input(shape=(self.input_dim,))
        
        # Encoder
        encoded = input_layer
        for units in self.hidden_layers:
            encoded = layers.Dense(units, activation='relu')(encoded)
        
        # Bottleneck
        encoded = layers.Dense(self.encoding_dim, activation='relu')(encoded)
        
        # Decoder
        decoded = encoded
        for units in reversed(self.hidden_layers):
            decoded = layers.Dense(units, activation='relu')(decoded)
        
        # Output layer
        decoded = layers.Dense(self.input_dim, activation='sigmoid')(decoded)
        
        # Create model
        self.model = Model(inputs=input_layer, outputs=decoded)
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        logger.info("Autoencoder model built successfully")
        return self.model
    
    def train(self, X_train: np.ndarray, X_val: Optional[np.ndarray] = None,
              epochs: int = 100, batch_size: int = 32, 
              validation_split: float = 0.2) -> dict:
        """Train the Autoencoder on benign traffic
        
        Args:
            X_train: Training data (benign traffic only)
            X_val: Optional validation data
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Validation split ratio if X_val not provided
            
        Returns:
            Training history dictionary
        """
        if self.model is None:
            self.build_model()
        
        # Early stopping callback
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train model (autoencoder learns to reconstruct input)
        validation_data = (X_val, X_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, X_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            validation_split=validation_split if validation_data is None else 0.0,
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Calculate threshold based on training data reconstruction error
        self._calculate_threshold(X_train)
        
        logger.info(f"Training completed. Threshold set to {self.threshold:.4f}")
        return history.history
    
    def _calculate_threshold(self, X_train: np.ndarray, percentile: float = 95):
        """Calculate anomaly threshold based on reconstruction error
        
        Args:
            X_train: Training data
            percentile: Percentile for threshold (e.g., 95 means 95% of normal data)
        """
        reconstructions = self.model.predict(X_train)
        reconstruction_errors = np.mean(np.square(X_train - reconstructions), axis=1)
        self.threshold = np.percentile(reconstruction_errors, percentile)
    
    def predict_anomaly(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict anomalies in data
        
        Args:
            X: Input data
            
        Returns:
            Tuple of (anomaly_scores, is_anomaly)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get reconstructions
        reconstructions = self.model.predict(X)
        
        # Calculate reconstruction error (MSE)
        reconstruction_errors = np.mean(np.square(X - reconstructions), axis=1)
        
        # Determine anomalies
        is_anomaly = reconstruction_errors > self.threshold
        
        return reconstruction_errors, is_anomaly
    
    def save_model(self, filepath: str):
        """Save model to file
        
        Args:
            filepath: Path to save model (.h5 or .keras)
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(filepath)
        # Save threshold separately
        np.save(filepath.replace('.h5', '_threshold.npy'), self.threshold)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file
        
        Args:
            filepath: Path to saved model
        """
        self.model = keras.models.load_model(filepath)
        
        # Load threshold
        threshold_path = filepath.replace('.h5', '_threshold.npy')
        try:
            self.threshold = np.load(threshold_path)
            logger.info(f"Model loaded from {filepath}, threshold={self.threshold:.4f}")
        except FileNotFoundError:
            logger.warning(f"Threshold file not found: {threshold_path}")
            self.threshold = 0.1  # Default threshold
    
    def convert_to_tflite(self, filepath: str):
        """Convert model to TensorFlow Lite for Raspberry Pi
        
        Args:
            filepath: Path to save TFLite model
        """
        if self.model is None:
            raise ValueError("No model to convert")
        
        # Convert to TFLite
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        
        # Save model
        with open(filepath, 'wb') as f:
            f.write(tflite_model)
        
        logger.info(f"TFLite model saved to {filepath}")


class IsolationForestModel:
    """Isolation Forest for anomaly detection (alternative to Autoencoder)"""
    
    def __init__(self, contamination: float = 0.1, n_estimators: int = 100):
        """Initialize Isolation Forest model
        
        Args:
            contamination: Expected proportion of outliers
            n_estimators: Number of trees
        """
        from sklearn.ensemble import IsolationForest
        
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42
        )
        logger.info(f"IsolationForest initialized with contamination={contamination}")
    
    def train(self, X_train: np.ndarray):
        """Train the Isolation Forest
        
        Args:
            X_train: Training data
        """
        self.model.fit(X_train)
        logger.info("IsolationForest training completed")
    
    def predict_anomaly(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict anomalies
        
        Args:
            X: Input data
            
        Returns:
            Tuple of (anomaly_scores, is_anomaly)
        """
        # Predict (-1 for anomaly, 1 for normal)
        predictions = self.model.predict(X)
        
        # Get anomaly scores (negative scores = more anomalous)
        anomaly_scores = -self.model.score_samples(X)
        
        # Convert to binary (True = anomaly)
        is_anomaly = predictions == -1
        
        return anomaly_scores, is_anomaly
    
    def save_model(self, filepath: str):
        """Save model to file
        
        Args:
            filepath: Path to save model
        """
        import joblib
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file
        
        Args:
            filepath: Path to saved model
        """
        import joblib
        self.model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
