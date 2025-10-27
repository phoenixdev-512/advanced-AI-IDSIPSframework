"""
Base model class for all ML algorithms
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
import numpy as np
import joblib
import json
from pathlib import Path


class BaseModel(ABC):
    """Abstract base class for all ML models"""
    
    def __init__(self, name: str):
        """Initialize base model
        
        Args:
            name: Model name identifier
        """
        self.name = name
        self.model = None
        self.is_trained = False
        self.metrics = {}
        
    @abstractmethod
    def build_model(self, **kwargs) -> Any:
        """Build the model with specified hyperparameters
        
        Returns:
            Model instance
        """
        pass
    
    @abstractmethod
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray = None, y_val: np.ndarray = None) -> Dict:
        """Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            
        Returns:
            Training metrics dictionary
        """
        pass
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels
        
        Args:
            X: Input features
            
        Returns:
            Predicted labels
        """
        if not self.is_trained:
            raise ValueError(f"Model {self.name} not trained. Call train() first.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities
        
        Args:
            X: Input features
            
        Returns:
            Predicted probabilities
        """
        if not self.is_trained:
            raise ValueError(f"Model {self.name} not trained. Call train() first.")
        
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            # For models without predict_proba, return binary predictions
            predictions = self.predict(X)
            # Convert to probability-like format [prob_class_0, prob_class_1]
            proba = np.zeros((len(predictions), 2))
            proba[predictions == 0, 0] = 1.0
            proba[predictions == 1, 1] = 1.0
            return proba
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, 
            f1_score, roc_auc_score, confusion_matrix
        )
        
        if not self.is_trained:
            raise ValueError(f"Model {self.name} not trained. Call train() first.")
        
        # Get predictions
        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)[:, 1]  # Probability of positive class
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
        }
        
        # ROC-AUC (only if we have both classes)
        if len(np.unique(y_test)) > 1:
            metrics['roc_auc'] = roc_auc_score(y_test, y_proba)
        else:
            metrics['roc_auc'] = 0.0
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics['true_negatives'] = int(tn)
            metrics['false_positives'] = int(fp)
            metrics['false_negatives'] = int(fn)
            metrics['true_positives'] = int(tp)
            
            # Additional metrics
            metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0
            metrics['true_positive_rate'] = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        self.metrics = metrics
        return metrics
    
    def save_model(self, filepath: str):
        """Save model to file
        
        Args:
            filepath: Path to save model
        """
        if not self.is_trained:
            raise ValueError(f"Model {self.name} not trained. Cannot save.")
        
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save model
        joblib.dump(self.model, filepath)
        
        # Save metrics
        metrics_path = filepath.replace('.pkl', '_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"{self.name} model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file
        
        Args:
            filepath: Path to saved model
        """
        self.model = joblib.load(filepath)
        self.is_trained = True
        
        # Load metrics if available
        metrics_path = filepath.replace('.pkl', '_metrics.json')
        if Path(metrics_path).exists():
            with open(metrics_path, 'r') as f:
                self.metrics = json.load(f)
        
        print(f"{self.name} model loaded from {filepath}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores
        
        Returns:
            Dictionary of feature names and importance scores
        """
        if not self.is_trained:
            raise ValueError(f"Model {self.name} not trained.")
        
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            # For linear models, use absolute coefficient values
            return np.abs(self.model.coef_[0])
        else:
            return None
    
    def __str__(self) -> str:
        """String representation"""
        status = "trained" if self.is_trained else "not trained"
        return f"{self.name} ({status})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"{self.__class__.__name__}(name='{self.name}', is_trained={self.is_trained})"
