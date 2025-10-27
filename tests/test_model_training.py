"""
Tests for model training algorithms
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from model_training.algorithms import (
    RandomForestModel,
    DecisionTreeModel,
    LogisticRegressionModel,
    SVMModel
)


class TestModelTraining:
    """Test model training functionality"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample training data"""
        np.random.seed(42)
        X_train = np.random.randn(100, 10)
        y_train = np.random.randint(0, 2, 100)
        X_test = np.random.randn(20, 10)
        y_test = np.random.randint(0, 2, 20)
        return X_train, y_train, X_test, y_test
    
    def test_random_forest_training(self, sample_data, tmp_path):
        """Test Random Forest training"""
        X_train, y_train, X_test, y_test = sample_data
        
        model = RandomForestModel(n_estimators=10, random_state=42)
        
        # Train
        metrics = model.train(X_train, y_train, X_test, y_test)
        
        assert model.is_trained
        assert 'train_accuracy' in metrics
        assert 'val_accuracy' in metrics
        assert metrics['train_accuracy'] > 0
        
        # Predict
        predictions = model.predict(X_test)
        assert len(predictions) == len(y_test)
        
        # Save and load
        model_path = tmp_path / "rf_model.pkl"
        model.save_model(str(model_path))
        assert model_path.exists()
        
        new_model = RandomForestModel()
        new_model.load_model(str(model_path))
        assert new_model.is_trained
    
    def test_decision_tree_training(self, sample_data, tmp_path):
        """Test Decision Tree training"""
        X_train, y_train, X_test, y_test = sample_data
        
        model = DecisionTreeModel(max_depth=5, random_state=42)
        
        # Train
        metrics = model.train(X_train, y_train, X_test, y_test)
        
        assert model.is_trained
        assert 'val_f1' in metrics
        
        # Feature importance
        importance = model.get_feature_importance()
        assert len(importance) == X_train.shape[1]
        
        # Save
        model_path = tmp_path / "dt_model.pkl"
        model.save_model(str(model_path))
        assert model_path.exists()
    
    def test_logistic_regression_training(self, sample_data, tmp_path):
        """Test Logistic Regression training"""
        X_train, y_train, X_test, y_test = sample_data
        
        model = LogisticRegressionModel(C=1.0, random_state=42)
        
        # Train
        metrics = model.train(X_train, y_train, X_test, y_test)
        
        assert model.is_trained
        assert metrics['train_accuracy'] >= 0
        
        # Predictions
        proba = model.predict_proba(X_test)
        assert proba.shape == (len(y_test), 2)
        assert np.all(proba >= 0) and np.all(proba <= 1)
        
        # Save
        model_path = tmp_path / "lr_model.pkl"
        model.save_model(str(model_path))
        assert model_path.exists()
    
    def test_svm_training(self, sample_data, tmp_path):
        """Test SVM training"""
        X_train, y_train, X_test, y_test = sample_data
        
        model = SVMModel(C=1.0, kernel='rbf', random_state=42)
        
        # Train
        metrics = model.train(X_train, y_train, X_test, y_test)
        
        assert model.is_trained
        assert 'val_roc_auc' in metrics
        
        # Predictions
        predictions = model.predict(X_test)
        assert len(predictions) == len(y_test)
        
        # Save
        model_path = tmp_path / "svm_model.pkl"
        model.save_model(str(model_path))
        assert model_path.exists()
    
    def test_model_evaluation(self, sample_data):
        """Test model evaluation metrics"""
        X_train, y_train, X_test, y_test = sample_data
        
        model = RandomForestModel(n_estimators=10, random_state=42)
        model.train(X_train, y_train)
        
        # Evaluate
        metrics = model.evaluate(X_test, y_test)
        
        required_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
        for metric in required_metrics:
            assert metric in metrics
            assert 0 <= metrics[metric] <= 1
    
    def test_predict_without_training(self):
        """Test that prediction fails without training"""
        model = RandomForestModel()
        X = np.random.randn(10, 5)
        
        with pytest.raises(ValueError):
            model.predict(X)
