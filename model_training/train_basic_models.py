#!/usr/bin/env python3
"""
Train basic machine learning models for network anomaly detection
"""

import argparse
import logging
import pickle
import sys
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.feature_preprocessing import FeaturePreprocessor
from model_training.algorithms import (
    RandomForestModel,
    DecisionTreeModel,
    LogisticRegressionModel,
    SVMModel
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_dataset(data_path: str) -> tuple:
    """Load dataset from pickle file
    
    Args:
        data_path: Path to dataset pickle file
        
    Returns:
        Tuple of (flows, labels)
    """
    logger.info(f"Loading dataset from {data_path}...")
    
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    
    flows = data['flows']
    labels = data['labels']
    
    logger.info(f"Loaded {len(flows)} flows")
    if labels is not None:
        unique, counts = np.unique(labels, return_counts=True)
        for label, count in zip(unique, counts):
            label_name = "Normal" if label == 0 else "Anomaly"
            logger.info(f"  {label_name}: {count} ({count/len(labels)*100:.1f}%)")
    
    return flows, labels


def prepare_features(flows: list, preprocessor: FeaturePreprocessor = None,
                    fit: bool = True) -> tuple:
    """Prepare features from flows
    
    Args:
        flows: List of flow dictionaries
        preprocessor: Existing preprocessor (optional)
        fit: Whether to fit the preprocessor
        
    Returns:
        Tuple of (X, preprocessor)
    """
    logger.info("Preparing features...")
    
    if preprocessor is None:
        preprocessor = FeaturePreprocessor()
    
    if fit:
        X = preprocessor.fit_transform(flows)
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Feature names: {preprocessor.feature_names}")
    else:
        X = preprocessor.transform(flows)
    
    return X, preprocessor


def train_model(model, X_train, y_train, X_val, y_val, output_dir: str):
    """Train a model and save it
    
    Args:
        model: Model instance
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        output_dir: Output directory for saved model
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Training {model.name} model...")
    logger.info(f"{'='*60}")
    
    # Train model
    metrics = model.train(X_train, y_train, X_val, y_val)
    
    # Save model
    model_path = Path(output_dir) / f"{model.name.lower()}_model.pkl"
    model.save_model(str(model_path))
    
    # Print metrics
    logger.info(f"\n{model.name} Performance:")
    logger.info(f"  Train Accuracy:  {metrics.get('train_accuracy', 0):.4f}")
    logger.info(f"  Train Precision: {metrics.get('train_precision', 0):.4f}")
    logger.info(f"  Train Recall:    {metrics.get('train_recall', 0):.4f}")
    logger.info(f"  Train F1:        {metrics.get('train_f1', 0):.4f}")
    
    if 'val_accuracy' in metrics:
        logger.info(f"\n  Val Accuracy:    {metrics.get('val_accuracy', 0):.4f}")
        logger.info(f"  Val Precision:   {metrics.get('val_precision', 0):.4f}")
        logger.info(f"  Val Recall:      {metrics.get('val_recall', 0):.4f}")
        logger.info(f"  Val F1:          {metrics.get('val_f1', 0):.4f}")
        logger.info(f"  Val ROC-AUC:     {metrics.get('val_roc_auc', 0):.4f}")
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Train basic ML models for anomaly detection")
    parser.add_argument('--data', type=str, required=True,
                       help='Path to prepared dataset (.pkl)')
    parser.add_argument('--output', type=str, default='model_training/results/models/',
                       help='Output directory for trained models')
    parser.add_argument('--model', type=str, choices=['random_forest', 'decision_tree', 
                                                       'logistic_regression', 'svm', 'all'],
                       default='all',
                       help='Model to train (default: all)')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Test set size (default: 0.2)')
    parser.add_argument('--random-state', type=int, default=42,
                       help='Random seed (default: 42)')
    
    args = parser.parse_args()
    
    # Load dataset
    flows, labels = load_dataset(args.data)
    
    if labels is None:
        logger.error("Dataset must have labels for supervised training!")
        logger.error("Use --synthetic or --labeled when preparing dataset")
        return
    
    # Prepare features
    X, preprocessor = prepare_features(flows, fit=True)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=args.test_size, random_state=args.random_state,
        stratify=labels
    )
    
    logger.info(f"\nDataset split:")
    logger.info(f"  Training samples:   {len(X_train)}")
    logger.info(f"  Test samples:       {len(X_test)}")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save preprocessor
    preprocessor_path = output_dir / "preprocessor.pkl"
    preprocessor.save(str(preprocessor_path))
    logger.info(f"Preprocessor saved to {preprocessor_path}")
    
    # Initialize models
    models = {}
    
    if args.model in ['random_forest', 'all']:
        models['random_forest'] = RandomForestModel(
            n_estimators=100,
            max_depth=20,
            random_state=args.random_state
        )
    
    if args.model in ['decision_tree', 'all']:
        models['decision_tree'] = DecisionTreeModel(
            max_depth=15,
            random_state=args.random_state
        )
    
    if args.model in ['logistic_regression', 'all']:
        models['logistic_regression'] = LogisticRegressionModel(
            C=1.0,
            random_state=args.random_state
        )
    
    if args.model in ['svm', 'all']:
        models['svm'] = SVMModel(
            C=1.0,
            kernel='rbf',
            random_state=args.random_state
        )
    
    # Train models
    all_metrics = {}
    for model_name, model in models.items():
        try:
            metrics = train_model(model, X_train, y_train, X_test, y_test, args.output)
            all_metrics[model_name] = metrics
        except Exception as e:
            logger.error(f"Error training {model_name}: {str(e)}")
            continue
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("Training Summary")
    logger.info(f"{'='*60}")
    
    if all_metrics:
        logger.info(f"\n{'Model':<20} {'Val Accuracy':<15} {'Val F1':<15} {'Val ROC-AUC':<15}")
        logger.info("-" * 65)
        
        for model_name, metrics in all_metrics.items():
            acc = metrics.get('val_accuracy', 0)
            f1 = metrics.get('val_f1', 0)
            roc = metrics.get('val_roc_auc', 0)
            logger.info(f"{model_name:<20} {acc:<15.4f} {f1:<15.4f} {roc:<15.4f}")
        
        # Find best model
        best_model = max(all_metrics.items(), key=lambda x: x[1].get('val_f1', 0))
        logger.info(f"\nBest model (by F1-score): {best_model[0]}")
    
    logger.info(f"\nAll models saved to: {args.output}")
    logger.info("Training completed successfully!")


if __name__ == "__main__":
    main()
