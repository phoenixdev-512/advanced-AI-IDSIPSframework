#!/usr/bin/env python3
"""
Complete Example: Model Training Workflow for Project Argus

This script demonstrates the complete workflow from data preparation
to model training, evaluation, and visualization.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*70)
print("PROJECT ARGUS - MODEL TRAINING COMPLETE EXAMPLE")
print("="*70)

# Step 1: Dataset Preparation
print("\n" + "="*70)
print("STEP 1: Dataset Preparation")
print("="*70)
print("Generating synthetic network flow data...")

from model_training.prepare_dataset import generate_synthetic_data, save_dataset

flows, labels = generate_synthetic_data(num_flows=5000, anomaly_ratio=0.1)
print(f"✓ Generated {len(flows)} flows")
print(f"  - Normal: {sum(labels == 0)} flows")
print(f"  - Anomaly: {sum(labels == 1)} flows")

# Save dataset
output_dir = Path("model_training/data")
output_dir.mkdir(parents=True, exist_ok=True)
dataset_path = output_dir / "example_data.pkl"
save_dataset(flows, labels, str(dataset_path))
print(f"✓ Dataset saved to {dataset_path}")

# Step 2: Feature Preprocessing
print("\n" + "="*70)
print("STEP 2: Feature Preprocessing")
print("="*70)

from src.models.feature_preprocessing import FeaturePreprocessor
from sklearn.model_selection import train_test_split
import pickle

# Load dataset
with open(dataset_path, 'rb') as f:
    data = pickle.load(f)
flows = data['flows']
labels = data['labels']

# Preprocess
preprocessor = FeaturePreprocessor()
X = preprocessor.fit_transform(flows)
print(f"✓ Preprocessed {X.shape[0]} samples")
print(f"✓ Extracted {X.shape[1]} features:")
for i, name in enumerate(preprocessor.feature_names, 1):
    print(f"    {i}. {name}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, labels, test_size=0.2, random_state=42, stratify=labels
)
print(f"\n✓ Data split:")
print(f"  - Training: {len(X_train)} samples")
print(f"  - Testing: {len(X_test)} samples")

# Step 3: Model Training
print("\n" + "="*70)
print("STEP 3: Model Training")
print("="*70)

from model_training.algorithms import (
    RandomForestModel,
    DecisionTreeModel,
    LogisticRegressionModel,
    SVMModel
)

models = {
    'Random Forest': RandomForestModel(n_estimators=100, max_depth=20, random_state=42),
    'Decision Tree': DecisionTreeModel(max_depth=15, random_state=42),
    'Logistic Regression': LogisticRegressionModel(C=1.0, random_state=42),
    'SVM': SVMModel(C=1.0, kernel='rbf', random_state=42)
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    metrics = model.train(X_train, y_train, X_test, y_test)
    results[name] = metrics
    print(f"  ✓ Accuracy: {metrics['val_accuracy']:.4f}")
    print(f"  ✓ F1-Score: {metrics['val_f1']:.4f}")

# Step 4: Model Comparison
print("\n" + "="*70)
print("STEP 4: Model Comparison")
print("="*70)

import pandas as pd

comparison_data = []
for name, metrics in results.items():
    comparison_data.append({
        'Model': name,
        'Accuracy': metrics['val_accuracy'],
        'Precision': metrics['val_precision'],
        'Recall': metrics['val_recall'],
        'F1-Score': metrics['val_f1'],
        'ROC-AUC': metrics.get('val_roc_auc', 0)
    })

df = pd.DataFrame(comparison_data)
df = df.sort_values('F1-Score', ascending=False)

print("\nPerformance Comparison:")
print(df.to_string(index=False))

# Best model
best_model = df.iloc[0]
print(f"\n🏆 BEST MODEL: {best_model['Model']}")
print(f"   F1-Score: {best_model['F1-Score']:.4f}")
print(f"   Accuracy: {best_model['Accuracy']:.4f}")

# Step 5: Feature Importance (for tree-based models)
print("\n" + "="*70)
print("STEP 5: Feature Importance Analysis")
print("="*70)

rf_model = models['Random Forest']
importance = rf_model.get_feature_importance()

# Create importance dataframe
importance_df = pd.DataFrame({
    'Feature': preprocessor.feature_names,
    'Importance': importance
})
importance_df = importance_df.sort_values('Importance', ascending=False)

print("\nTop 10 Most Important Features (Random Forest):")
print(importance_df.head(10).to_string(index=False))

# Step 6: Save Models
print("\n" + "="*70)
print("STEP 6: Saving Models")
print("="*70)

models_dir = Path("model_training/results/models")
models_dir.mkdir(parents=True, exist_ok=True)

for name, model in models.items():
    model_filename = name.lower().replace(' ', '_') + '_model.pkl'
    model_path = models_dir / model_filename
    model.save_model(str(model_path))
    print(f"✓ Saved {name} to {model_path}")

# Save preprocessor
preprocessor_path = models_dir / "preprocessor.pkl"
preprocessor.save(str(preprocessor_path))
print(f"✓ Saved preprocessor to {preprocessor_path}")

# Save comparison results
metrics_dir = Path("model_training/results/metrics")
metrics_dir.mkdir(parents=True, exist_ok=True)

comparison_path = metrics_dir / "example_comparison.csv"
df.to_csv(comparison_path, index=False)
print(f"✓ Saved comparison to {comparison_path}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\n✅ Successfully trained {len(models)} machine learning models")
print(f"✅ Best model: {best_model['Model']} (F1={best_model['F1-Score']:.4f})")
print(f"✅ All models saved to: {models_dir}")
print(f"✅ Metrics saved to: {metrics_dir}")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)
print("\n1. Review the comparison results:")
print(f"   cat {comparison_path}")
print("\n2. Visualize the results:")
print(f"   python model_training/visualize_results.py --results {comparison_path}")
print("\n3. Deploy the best model:")
print(f"   cp {models_dir}/{best_model['Model'].lower().replace(' ', '_')}_model.pkl data/models/")
print("\n4. Integrate with Project Argus:")
print("   Update configuration to use the trained model")

print("\n" + "="*70)
print("COMPLETED SUCCESSFULLY! 🎉")
print("="*70)
