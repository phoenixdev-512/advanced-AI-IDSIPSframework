"""
Decision Tree Classifier for network anomaly detection
"""

import numpy as np
from typing import Dict, Any
from sklearn.tree import DecisionTreeClassifier
from .base_model import BaseModel


class DecisionTreeModel(BaseModel):
    """Decision Tree model for supervised anomaly detection"""
    
    def __init__(self, max_depth: int = None, min_samples_split: int = 2,
                 min_samples_leaf: int = 1, criterion: str = 'gini',
                 random_state: int = 42):
        """Initialize Decision Tree model
        
        Args:
            max_depth: Maximum depth of tree (None = unlimited)
            min_samples_split: Minimum samples to split a node
            min_samples_leaf: Minimum samples in a leaf node
            criterion: Splitting criterion ('gini' or 'entropy')
            random_state: Random seed for reproducibility
        """
        super().__init__(name="DecisionTree")
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.criterion = criterion
        self.random_state = random_state
        
    def build_model(self, **kwargs) -> DecisionTreeClassifier:
        """Build Decision Tree model
        
        Returns:
            DecisionTreeClassifier instance
        """
        # Update parameters if provided
        max_depth = kwargs.get('max_depth', self.max_depth)
        min_samples_split = kwargs.get('min_samples_split', self.min_samples_split)
        min_samples_leaf = kwargs.get('min_samples_leaf', self.min_samples_leaf)
        criterion = kwargs.get('criterion', self.criterion)
        
        self.model = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            criterion=criterion,
            random_state=self.random_state
        )
        
        return self.model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None) -> Dict:
        """Train Decision Tree model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            
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
    
    def export_tree_rules(self, feature_names: list = None) -> str:
        """Export decision tree rules as text
        
        Args:
            feature_names: List of feature names
            
        Returns:
            String representation of tree rules
        """
        from sklearn.tree import export_text
        
        if not self.is_trained:
            raise ValueError("Model not trained.")
        
        tree_rules = export_text(self.model, feature_names=feature_names)
        return tree_rules
