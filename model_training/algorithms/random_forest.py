"""
Random Forest Classifier for network anomaly detection
"""

import numpy as np
from typing import Dict, Any
from sklearn.ensemble import RandomForestClassifier
from .base_model import BaseModel


class RandomForestModel(BaseModel):
    """Random Forest model for supervised anomaly detection"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = None,
                 min_samples_split: int = 2, min_samples_leaf: int = 1,
                 random_state: int = 42):
        """Initialize Random Forest model
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of trees (None = unlimited)
            min_samples_split: Minimum samples to split a node
            min_samples_leaf: Minimum samples in a leaf node
            random_state: Random seed for reproducibility
        """
        super().__init__(name="RandomForest")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        
    def build_model(self, **kwargs) -> RandomForestClassifier:
        """Build Random Forest model
        
        Returns:
            RandomForestClassifier instance
        """
        # Update parameters if provided
        n_estimators = kwargs.get('n_estimators', self.n_estimators)
        max_depth = kwargs.get('max_depth', self.max_depth)
        min_samples_split = kwargs.get('min_samples_split', self.min_samples_split)
        min_samples_leaf = kwargs.get('min_samples_leaf', self.min_samples_leaf)
        
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=self.random_state,
            n_jobs=-1,  # Use all CPU cores
            verbose=0
        )
        
        return self.model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None) -> Dict:
        """Train Random Forest model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional, not used for RF)
            y_val: Validation labels (optional, not used for RF)
            
        Returns:
            Training metrics
        """
        if self.model is None:
            self.build_model()
        
        print(f"Training {self.name} on {X_train.shape[0]} samples with {X_train.shape[1]} features...")
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate on training set
        train_metrics = self.evaluate(X_train, y_train)
        metrics = {
            'train_accuracy': train_metrics['accuracy'],
            'train_precision': train_metrics['precision'],
            'train_recall': train_metrics['recall'],
            'train_f1': train_metrics['f1_score']
        }
        
        # Evaluate on validation set if provided
        if X_val is not None and y_val is not None:
            val_metrics = self.evaluate(X_val, y_val)
            metrics.update({
                'val_accuracy': val_metrics['accuracy'],
                'val_precision': val_metrics['precision'],
                'val_recall': val_metrics['recall'],
                'val_f1': val_metrics['f1_score'],
                'val_roc_auc': val_metrics['roc_auc']
            })
        
        print(f"{self.name} training completed!")
        print(f"Train Accuracy: {metrics['train_accuracy']:.4f}")
        if 'val_accuracy' in metrics:
            print(f"Val Accuracy: {metrics['val_accuracy']:.4f}")
        
        return metrics
    
    def get_feature_importance(self) -> np.ndarray:
        """Get feature importance scores
        
        Returns:
            Array of feature importance scores
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")
        
        return self.model.feature_importances_
