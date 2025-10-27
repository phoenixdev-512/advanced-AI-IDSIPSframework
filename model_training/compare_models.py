#!/usr/bin/env python3
"""
Compare performance of trained models
"""

import argparse
import logging
import pickle
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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


def load_test_data(data_path: str) -> tuple:
    """Load test dataset
    
    Args:
        data_path: Path to test data pickle
        
    Returns:
        Tuple of (X_test, y_test)
    """
    logger.info(f"Loading test data from {data_path}...")
    
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    
    X_test = data.get('X_test')
    y_test = data.get('y_test')
    
    if X_test is None or y_test is None:
        raise ValueError("Test data must contain 'X_test' and 'y_test'")
    
    logger.info(f"Loaded {len(X_test)} test samples")
    return X_test, y_test


def load_models(models_dir: str) -> dict:
    """Load all trained models from directory
    
    Args:
        models_dir: Directory containing model files
        
    Returns:
        Dictionary of {model_name: model_instance}
    """
    models_dir = Path(models_dir)
    models = {}
    
    model_files = {
        'RandomForest': 'randomforest_model.pkl',
        'DecisionTree': 'decisiontree_model.pkl',
        'LogisticRegression': 'logisticregression_model.pkl',
        'SVM': 'svm_model.pkl'
    }
    
    model_classes = {
        'RandomForest': RandomForestModel,
        'DecisionTree': DecisionTreeModel,
        'LogisticRegression': LogisticRegressionModel,
        'SVM': SVMModel
    }
    
    for model_name, filename in model_files.items():
        model_path = models_dir / filename
        if model_path.exists():
            logger.info(f"Loading {model_name}...")
            model = model_classes[model_name]()
            model.load_model(str(model_path))
            models[model_name] = model
        else:
            logger.warning(f"Model file not found: {model_path}")
    
    logger.info(f"Loaded {len(models)} models")
    return models


def compare_models(models: dict, X_test: np.ndarray, y_test: np.ndarray) -> pd.DataFrame:
    """Compare performance of all models
    
    Args:
        models: Dictionary of models
        X_test: Test features
        y_test: Test labels
        
    Returns:
        DataFrame with comparison metrics
    """
    logger.info("Evaluating models...")
    
    results = []
    
    for model_name, model in models.items():
        logger.info(f"Evaluating {model_name}...")
        
        # Evaluate model
        metrics = model.evaluate(X_test, y_test)
        
        result = {
            'Model': model_name,
            'Accuracy': metrics['accuracy'],
            'Precision': metrics['precision'],
            'Recall': metrics['recall'],
            'F1-Score': metrics['f1_score'],
            'ROC-AUC': metrics['roc_auc'],
            'FPR': metrics.get('false_positive_rate', 0),
            'TPR': metrics.get('true_positive_rate', 0)
        }
        
        results.append(result)
    
    df = pd.DataFrame(results)
    df = df.sort_values('F1-Score', ascending=False)
    
    return df


def save_comparison_report(df: pd.DataFrame, output_path: str):
    """Save comparison report as HTML
    
    Args:
        df: Comparison DataFrame
        output_path: Output file path
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    html = f"""
    <html>
    <head>
        <title>Model Comparison Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .best {{ background-color: #d4edda; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Model Comparison Report</h1>
        <p>Comparison of machine learning models for network anomaly detection</p>
        
        <h2>Performance Metrics</h2>
        {df.to_html(index=False, classes='comparison-table', float_format=lambda x: f'{x:.4f}')}
        
        <h2>Metric Definitions</h2>
        <ul>
            <li><strong>Accuracy:</strong> Overall correctness (TP+TN)/(TP+TN+FP+FN)</li>
            <li><strong>Precision:</strong> Of predicted anomalies, how many are real? TP/(TP+FP)</li>
            <li><strong>Recall:</strong> Of real anomalies, how many did we detect? TP/(TP+FN)</li>
            <li><strong>F1-Score:</strong> Harmonic mean of Precision and Recall</li>
            <li><strong>ROC-AUC:</strong> Area under ROC curve (threshold-independent)</li>
            <li><strong>FPR:</strong> False Positive Rate FP/(FP+TN)</li>
            <li><strong>TPR:</strong> True Positive Rate (same as Recall)</li>
        </ul>
        
        <h2>Recommendations</h2>
        <ul>
            <li><strong>Best Overall:</strong> {df.iloc[0]['Model']} (F1-Score: {df.iloc[0]['F1-Score']:.4f})</li>
            <li><strong>Highest Precision:</strong> {df.loc[df['Precision'].idxmax()]['Model']} (fewer false alarms)</li>
            <li><strong>Highest Recall:</strong> {df.loc[df['Recall'].idxmax()]['Model']} (detects more threats)</li>
        </ul>
    </body>
    </html>
    """
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    logger.info(f"Report saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Compare trained models")
    parser.add_argument('--models-dir', type=str, required=True,
                       help='Directory containing trained models')
    parser.add_argument('--test-data', type=str, required=True,
                       help='Path to test data (.pkl)')
    parser.add_argument('--output', type=str, default='model_training/results/metrics/',
                       help='Output directory for comparison results')
    
    args = parser.parse_args()
    
    # Load test data
    X_test, y_test = load_test_data(args.test_data)
    
    # Load models
    models = load_models(args.models_dir)
    
    if not models:
        logger.error("No models found to compare!")
        return
    
    # Compare models
    df = compare_models(models, X_test, y_test)
    
    # Print results
    logger.info("\n" + "="*80)
    logger.info("Model Comparison Results")
    logger.info("="*80)
    print("\n" + df.to_string(index=False))
    
    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV
    csv_path = output_dir / "comparison.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"\nResults saved to {csv_path}")
    
    # Save as HTML report
    html_path = output_dir / "comparison_report.html"
    save_comparison_report(df, str(html_path))
    
    # Save as JSON
    json_path = output_dir / "comparison.json"
    df.to_json(json_path, orient='records', indent=2)
    logger.info(f"Results saved to {json_path}")
    
    logger.info("\nComparison completed successfully!")


if __name__ == "__main__":
    main()
