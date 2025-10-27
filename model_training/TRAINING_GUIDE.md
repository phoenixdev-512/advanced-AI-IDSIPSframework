# Model Training Guide - Project Argus

## Quick Start

This guide explains how to train and compare different machine learning models for network anomaly detection in Project Argus.

## Directory Structure

```
model_training/
├── README.md                    # This guide
├── ML_OVERVIEW.md              # Comprehensive ML documentation
├── TRAINING_GUIDE.md           # Detailed training instructions
├── algorithms/                 # ML algorithm implementations
│   ├── __init__.py
│   ├── random_forest.py       # Random Forest classifier
│   ├── decision_tree.py       # Decision Tree classifier
│   ├── logistic_regression.py # Logistic Regression classifier
│   ├── svm.py                 # Support Vector Machine
│   └── base_model.py          # Base class for all models
├── data/                      # Training data (gitignored)
│   ├── processed/            # Preprocessed features
│   └── raw/                  # Raw network flows
├── results/                   # Training results (gitignored)
│   ├── models/               # Trained model files
│   ├── metrics/              # Performance metrics
│   └── plots/                # Visualization plots
├── notebooks/                 # Jupyter notebooks (optional)
├── train_basic_models.py     # Main training script
├── compare_models.py         # Model comparison script
├── prepare_dataset.py        # Dataset preparation script
└── visualize_results.py      # Results visualization
```

## Prerequisites

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Step 1: Prepare Training Data

### Option A: Use Synthetic Data (Testing/Development)

Generate synthetic network flow data:

```bash
python model_training/prepare_dataset.py --synthetic --num-flows 10000 --output data/synthetic_flows.pkl
```

Parameters:
- `--synthetic`: Generate synthetic data
- `--num-flows`: Number of flows to generate (default: 10000)
- `--output`: Output file path

### Option B: Use Real Network Data (Production)

Collect real network traffic data:

1. Start packet capture and let it run for 24-48 hours:
```bash
python main.py start --mode passive
```

2. Export flows from InfluxDB:
```bash
python model_training/prepare_dataset.py --from-influxdb --hours 48 --output data/real_flows.pkl
```

Parameters:
- `--from-influxdb`: Load from InfluxDB
- `--hours`: Hours of historical data
- `--output`: Output file path

### Option C: Use Labeled Dataset (Supervised Training)

If you have labeled attack data:

```bash
python model_training/prepare_dataset.py --labeled --normal-file data/normal.csv --attack-file data/attacks.csv --output data/labeled_flows.pkl
```

## Step 2: Train Individual Models

### Train All Basic ML Models

Train all basic machine learning algorithms:

```bash
python model_training/train_basic_models.py --data data/synthetic_flows.pkl --output results/models/
```

This will train:
- Random Forest
- Decision Tree
- Logistic Regression
- Support Vector Machine (SVM)

Parameters:
- `--data`: Path to prepared dataset
- `--output`: Directory to save models
- `--test-size`: Test set ratio (default: 0.2)
- `--random-state`: Random seed for reproducibility

### Train Specific Model

Train only one algorithm:

```bash
# Random Forest
python model_training/train_basic_models.py --data data/synthetic_flows.pkl --model random_forest

# Decision Tree
python model_training/train_basic_models.py --data data/synthetic_flows.pkl --model decision_tree

# Logistic Regression
python model_training/train_basic_models.py --data data/synthetic_flows.pkl --model logistic_regression

# SVM
python model_training/train_basic_models.py --data data/synthetic_flows.pkl --model svm
```

### Advanced Training Options

```bash
python model_training/train_basic_models.py \
  --data data/real_flows.pkl \
  --output results/models/ \
  --test-size 0.2 \
  --cross-validation 5 \
  --hyperparameter-tuning \
  --random-state 42
```

Parameters:
- `--cross-validation`: K-fold cross-validation (default: 5)
- `--hyperparameter-tuning`: Enable GridSearchCV for best parameters
- `--random-state`: Seed for reproducibility

## Step 3: Train Deep Learning Models

For Autoencoder and other deep learning models:

```bash
# Train Autoencoder (from root directory)
python train_model.py --model autoencoder --synthetic --num-flows 5000 --save-dir data/models/

# Train Isolation Forest
python train_model.py --model isolation_forest --synthetic --num-flows 5000 --save-dir data/models/
```

With real data:

```bash
python train_model.py --model autoencoder --hours 48 --save-dir data/models/
```

## Step 4: Compare Models

Compare performance of all trained models:

```bash
python model_training/compare_models.py --models-dir results/models/ --test-data data/test_flows.pkl
```

This generates:
- Performance metrics comparison table
- ROC curves for all models
- Precision-Recall curves
- Confusion matrices
- Feature importance rankings

Output saved to: `results/metrics/comparison_report.html`

## Step 5: Visualize Results

Create visualizations of training results:

```bash
python model_training/visualize_results.py --results results/metrics/
```

Generates:
- Model performance bar charts
- ROC curve comparisons
- Feature importance plots
- Confusion matrix heatmaps
- Training history plots (for neural networks)

Output saved to: `results/plots/`

## Model Selection Guidelines

### When to Use Each Algorithm

**Random Forest**:
- ✅ Best for: General-purpose classification with labeled data
- ✅ Advantages: High accuracy, robust, feature importance
- ❌ Disadvantages: Slower inference than simpler models

**Decision Tree**:
- ✅ Best for: Interpretability, understanding decision logic
- ✅ Advantages: Fast, easy to visualize and explain
- ❌ Disadvantages: Prone to overfitting, lower accuracy

**Logistic Regression**:
- ✅ Best for: Baseline comparison, linear relationships
- ✅ Advantages: Fast, simple, interpretable coefficients
- ❌ Disadvantages: Cannot capture complex patterns

**SVM**:
- ✅ Best for: Small to medium datasets, clear class separation
- ✅ Advantages: Effective in high dimensions, memory efficient
- ❌ Disadvantages: Slow with large datasets, hyperparameter sensitive

**Autoencoder** (Deep Learning):
- ✅ Best for: Unsupervised anomaly detection, no labeled data
- ✅ Advantages: Detects complex patterns, no labels needed
- ❌ Disadvantages: Computationally expensive, less interpretable

**Isolation Forest**:
- ✅ Best for: Fast unsupervised anomaly detection, real-time
- ✅ Advantages: Fast, memory efficient, no labels needed
- ❌ Disadvantages: May miss subtle anomalies

### Recommended Approach

1. **For Production (No Labeled Data)**:
   - Primary: Autoencoder or Isolation Forest
   - Reason: Unsupervised, detects unknown attacks

2. **For Research/Comparison (Labeled Data)**:
   - Train all algorithms
   - Compare performance
   - Use Random Forest for best accuracy
   - Use Decision Tree for interpretability

3. **For Resource-Constrained Devices**:
   - Isolation Forest (fastest)
   - Logistic Regression (simplest)
   - TFLite Autoencoder (optimized)

## Performance Metrics Explained

### For Binary Classification (Normal vs. Anomaly)

- **Accuracy**: (TP + TN) / Total
  - Overall correctness, but misleading with imbalanced data

- **Precision**: TP / (TP + FP)
  - Of all predicted anomalies, how many are real?
  - High precision = Few false alarms

- **Recall (Sensitivity)**: TP / (TP + FN)
  - Of all real anomalies, how many did we detect?
  - High recall = Detect most threats

- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)
  - Balance between precision and recall

- **ROC-AUC**: Area under Receiver Operating Characteristic curve
  - Threshold-independent performance (0.5 = random, 1.0 = perfect)

### Target Metrics for IDS/IPS

- Precision: > 95% (minimize false alarms)
- Recall: > 90% (detect most attacks)
- F1-Score: > 0.92
- ROC-AUC: > 0.95

## Hyperparameter Tuning

### Random Forest

```python
{
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}
```

### Decision Tree

```python
{
    'max_depth': [5, 10, 15, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'criterion': ['gini', 'entropy']
}
```

### SVM

```python
{
    'C': [0.1, 1, 10, 100],
    'kernel': ['rbf', 'linear', 'poly'],
    'gamma': ['scale', 'auto', 0.1, 0.01]
}
```

### Logistic Regression

```python
{
    'C': [0.01, 0.1, 1, 10, 100],
    'penalty': ['l1', 'l2'],
    'solver': ['liblinear', 'saga']
}
```

## Troubleshooting

### Issue: Model overfitting (high train accuracy, low test accuracy)

**Solutions**:
- Increase training data
- Reduce model complexity (e.g., max_depth for trees)
- Use regularization (e.g., higher C for SVM)
- Cross-validation

### Issue: Low recall (missing attacks)

**Solutions**:
- Adjust decision threshold (lower for more sensitivity)
- Collect more attack samples
- Use ensemble methods (Random Forest)
- Try different algorithms

### Issue: High false positive rate

**Solutions**:
- Increase decision threshold
- Use precision-focused metrics
- Filter out benign anomalies (whitelist)
- Collect more normal traffic for training

### Issue: Slow training or inference

**Solutions**:
- Reduce feature dimensionality (feature selection)
- Use simpler algorithms (Logistic Regression, Decision Tree)
- Batch processing
- Model quantization/compression

## Model Deployment

After training and evaluation:

1. **Save Best Model**:
```bash
# Model is auto-saved to results/models/
# Copy to production directory
cp results/models/random_forest_model.pkl data/models/
```

2. **Update Configuration**:
Edit `src/config.py` to use the new model:
```python
MODEL_TYPE = 'random_forest'  # or 'decision_tree', 'svm', etc.
MODEL_PATH = 'data/models/random_forest_model.pkl'
```

3. **Test in Production**:
```bash
python main.py full --mode passive
```

4. **Monitor Performance**:
- Check false positive rate
- Verify detection of test attacks
- Monitor resource usage

## Retraining Schedule

Recommended retraining frequency:

- **Weekly**: If network changes frequently
- **Monthly**: For stable networks
- **On-demand**: After major network changes (new devices, new services)

Automated retraining:
```bash
# Add to crontab for weekly retraining
0 2 * * 0 cd /path/to/project && python model_training/train_basic_models.py --data data/latest_flows.pkl
```

## Additional Resources

- **ML_OVERVIEW.md**: Comprehensive ML theory and architecture
- **Scikit-learn Documentation**: https://scikit-learn.org/
- **TensorFlow Documentation**: https://www.tensorflow.org/
- **Project Argus README**: ../README.md

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review ML_OVERVIEW.md for theory
3. Open an issue on GitHub
4. Check logs in `data/logs/`

---

**Happy Training! 🚀**
