"""
Logistic Regression Classifier for network anomaly detection
"""

import numpy as np
from typing import Dict, Any
from sklearn.linear_model import LogisticRegression
from .base_model import BaseModel


class LogisticRegressionModel(BaseModel):
    """Logistic Regression model for supervised anomaly detection"""
    
    def __init__(self, C: float = 1.0, penalty: str = 'l2',
                 solver: str = 'lbfgs', max_iter: int = 1000,
                 random_state: int = 42):
        """Initialize Logistic Regression model
        
        Args:
            C: Inverse of regularization strength (smaller = stronger)
            penalty: Regularization penalty ('l1', 'l2', 'elasticnet', 'none')
            solver: Optimization algorithm ('lbfgs', 'liblinear', 'saga', etc.)
            max_iter: Maximum iterations for solver convergence
            random_state: Random seed for reproducibility
        """
        super().__init__(name="LogisticRegression")
        self.C = C
        self.penalty = penalty
        self.solver = solver
        self.max_iter = max_iter
        self.random_state = random_state
        
    def build_model(self, **kwargs) -> LogisticRegression:
        """Build Logistic Regression model
        
        Returns:
            LogisticRegression instance
        """
        # Update parameters if provided
        C = kwargs.get('C', self.C)
        penalty = kwargs.get('penalty', self.penalty)
        solver = kwargs.get('solver', self.solver)
        max_iter = kwargs.get('max_iter', self.max_iter)
        
        self.model = LogisticRegression(
            C=C,
            penalty=penalty,
            solver=solver,
            max_iter=max_iter,
            random_state=self.random_state,
            n_jobs=-1,  # Use all CPU cores
            verbose=0
        )
        
        return self.model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None) -> Dict:
        """Train Logistic Regression model
        
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
    
    def get_coefficients(self) -> np.ndarray:
        """Get model coefficients
        
        Returns:
            Array of coefficients
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")
        
        return self.model.coef_[0]
    
    def get_feature_importance(self) -> np.ndarray:
        """Get feature importance based on absolute coefficient values
        
        Returns:
            Array of feature importance scores
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")
        
        # Use absolute coefficients as importance
        return np.abs(self.model.coef_[0])
