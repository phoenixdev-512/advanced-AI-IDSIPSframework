"""
Support Vector Machine Classifier for network anomaly detection
"""

import numpy as np
from typing import Dict, Any
from sklearn.svm import SVC
from .base_model import BaseModel


class SVMModel(BaseModel):
    """Support Vector Machine model for supervised anomaly detection"""
    
    def __init__(self, C: float = 1.0, kernel: str = 'rbf',
                 gamma: str = 'scale', probability: bool = True,
                 random_state: int = 42):
        """Initialize SVM model
        
        Args:
            C: Regularization parameter
            kernel: Kernel type ('linear', 'poly', 'rbf', 'sigmoid')
            gamma: Kernel coefficient ('scale', 'auto', or float)
            probability: Enable probability estimates
            random_state: Random seed for reproducibility
        """
        super().__init__(name="SVM")
        self.C = C
        self.kernel = kernel
        self.gamma = gamma
        self.probability = probability
        self.random_state = random_state
        
    def build_model(self, **kwargs) -> SVC:
        """Build SVM model
        
        Returns:
            SVC instance
        """
        # Update parameters if provided
        C = kwargs.get('C', self.C)
        kernel = kwargs.get('kernel', self.kernel)
        gamma = kwargs.get('gamma', self.gamma)
        probability = kwargs.get('probability', self.probability)
        
        self.model = SVC(
            C=C,
            kernel=kernel,
            gamma=gamma,
            probability=probability,
            random_state=self.random_state,
            verbose=False
        )
        
        return self.model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None) -> Dict:
        """Train SVM model
        
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
        print("Note: SVM training may take a while for large datasets...")
        
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
    
    def get_support_vectors(self) -> np.ndarray:
        """Get support vectors
        
        Returns:
            Array of support vectors
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")
        
        return self.model.support_vectors_
    
    def get_n_support_vectors(self) -> int:
        """Get number of support vectors
        
        Returns:
            Number of support vectors
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")
        
        return len(self.model.support_vectors_)
