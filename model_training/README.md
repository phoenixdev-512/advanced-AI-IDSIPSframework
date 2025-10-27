# Model Training - Project Argus

This folder contains everything you need to train, evaluate, and compare machine learning models for network anomaly detection in Project Argus.

## 📋 Overview

The `model_training/` directory provides a complete framework for training basic machine learning algorithms on network traffic data. This complements the existing deep learning models (Autoencoder, Isolation Forest) and enables you to:

- Train multiple ML algorithms (Random Forest, Decision Tree, Logistic Regression, SVM)
- Compare model performance objectively
- Understand which algorithm works best for your network
- Deploy the best model for production use

## 📁 Directory Structure

```
model_training/
├── README.md                    # This file
├── ML_OVERVIEW.md              # Comprehensive ML theory and architecture
├── TRAINING_GUIDE.md           # Detailed step-by-step training guide
│
├── algorithms/                 # ML algorithm implementations
│   ├── __init__.py
│   ├── base_model.py          # Base class for all models
│   ├── random_forest.py       # Random Forest classifier
│   ├── decision_tree.py       # Decision Tree classifier
│   ├── logistic_regression.py # Logistic Regression classifier
│   └── svm.py                 # Support Vector Machine
│
├── data/                       # Training data (gitignored)
│   ├── processed/             # Preprocessed features
│   └── raw/                   # Raw network flows
│
├── results/                    # Training results (gitignored)
│   ├── models/                # Trained model files (.pkl)
│   ├── metrics/               # Performance metrics (CSV, JSON, HTML)
│   └── plots/                 # Visualization plots (PNG)
│
├── notebooks/                  # Jupyter notebooks (optional)
│
├── prepare_dataset.py         # Dataset preparation script
├── train_basic_models.py      # Main training script
├── compare_models.py          # Model comparison script
└── visualize_results.py       # Results visualization script
```

## 🚀 Quick Start

### 1. Generate Synthetic Training Data

```bash
python model_training/prepare_dataset.py \
  --synthetic \
  --num-flows 10000 \
  --anomaly-ratio 0.1 \
  --output model_training/data/synthetic_flows.pkl
```

### 2. Train All Models

```bash
python model_training/train_basic_models.py \
  --data model_training/data/synthetic_flows.pkl \
  --output model_training/results/models/
```

### 3. Compare Models

```bash
# First, save test data during training or create it separately
python model_training/compare_models.py \
  --models-dir model_training/results/models/ \
  --test-data model_training/data/test_flows.pkl
```

### 4. Visualize Results

```bash
python model_training/visualize_results.py \
  --results model_training/results/metrics/comparison.csv \
  --output model_training/results/plots/
```

## 📚 Documentation

### Core Documentation

- **[ML_OVERVIEW.md](ML_OVERVIEW.md)**: Comprehensive guide to machine learning in Project Argus
  - Explains the role of ML in IDS/IPS systems
  - Detailed algorithm descriptions
  - Feature engineering approach
  - Model evaluation methodology
  - Deployment strategies

- **[TRAINING_GUIDE.md](TRAINING_GUIDE.md)**: Step-by-step training instructions
  - Data preparation options
  - Training procedures
  - Hyperparameter tuning
  - Model selection guidelines
  - Troubleshooting tips

### Quick Reference

**What is the role of Machine Learning in this project?**

Machine Learning enables **anomaly detection** - the system learns what normal network traffic looks like and identifies deviations that may indicate:
- Compromised devices
- Port scanning attacks
- DDoS attempts
- Data exfiltration
- Unknown/zero-day threats

Unlike signature-based systems, ML can detect novel attacks without prior knowledge of specific attack patterns.

## 🎯 Use Cases

### 1. Model Selection & Comparison

Train multiple algorithms and compare their performance to find the best fit for your network:

```bash
# Train all models
python model_training/train_basic_models.py --data your_data.pkl --model all

# Compare them
python model_training/compare_models.py --models-dir results/models/ --test-data test_data.pkl
```

### 2. Supervised Learning with Labeled Data

If you have labeled attack data:

```bash
# Prepare labeled dataset
python model_training/prepare_dataset.py \
  --labeled \
  --normal-file data/normal_traffic.csv \
  --attack-file data/attack_traffic.csv \
  --output data/labeled_flows.pkl

# Train models
python model_training/train_basic_models.py --data data/labeled_flows.pkl
```

### 3. Real Network Data Training

Collect real data and train:

```bash
# Collect 48 hours of real traffic
python model_training/prepare_dataset.py \
  --from-influxdb \
  --hours 48 \
  --output data/real_flows.pkl

# Train (unsupervised)
python train_model.py --data data/real_flows.pkl
```

## 🔬 Algorithms Included

| Algorithm | Type | Speed | Accuracy | Interpretability | Best For |
|-----------|------|-------|----------|------------------|----------|
| **Random Forest** | Ensemble | Medium | High | Medium | General purpose, high accuracy |
| **Decision Tree** | Tree-based | Fast | Medium | High | Interpretability, understanding rules |
| **Logistic Regression** | Linear | Very Fast | Medium | High | Baseline, simple patterns |
| **SVM** | Kernel | Slow | High | Low | Small datasets, clear separation |
| **Autoencoder** (existing) | Deep Learning | Medium | High | Low | Unsupervised, complex patterns |
| **Isolation Forest** (existing) | Tree-based | Fast | Medium | Low | Unsupervised, real-time |

## 📊 Outputs

### Trained Models
- `results/models/randomforest_model.pkl`
- `results/models/decisiontree_model.pkl`
- `results/models/logisticregression_model.pkl`
- `results/models/svm_model.pkl`
- `results/models/preprocessor.pkl`

### Metrics
- `results/metrics/comparison.csv` - Performance metrics table
- `results/metrics/comparison.json` - JSON format metrics
- `results/metrics/comparison_report.html` - Detailed HTML report

### Visualizations
- `results/plots/model_comparison.png` - Bar charts of all metrics
- `results/plots/metrics_heatmap.png` - Heatmap of model performance
- `results/plots/precision_recall_tradeoff.png` - Precision vs Recall scatter
- `results/plots/roc_auc_comparison.png` - ROC-AUC comparison
- `results/plots/summary_dashboard.png` - Comprehensive summary

## 🎓 Learning Resources

### Understanding the Metrics

- **Accuracy**: How often is the model correct overall?
- **Precision**: Of predicted attacks, how many are real? (Low false alarms)
- **Recall**: Of real attacks, how many did we detect? (High detection)
- **F1-Score**: Balance between Precision and Recall
- **ROC-AUC**: Overall discriminative ability (0.5=random, 1.0=perfect)

### Target Performance for IDS/IPS

- ✅ Precision > 95% (minimize false alarms)
- ✅ Recall > 90% (detect most threats)
- ✅ F1-Score > 0.92
- ✅ ROC-AUC > 0.95

## 🛠️ Advanced Usage

### Custom Hyperparameters

Edit the model initialization in `train_basic_models.py`:

```python
models['random_forest'] = RandomForestModel(
    n_estimators=200,      # More trees
    max_depth=30,          # Deeper trees
    min_samples_split=5,
    random_state=42
)
```

### Feature Engineering

Modify `src/models/feature_preprocessing.py` to add custom features, then retrain all models.

### Cross-Validation

For more robust evaluation, implement k-fold cross-validation in your training script.

## 🤝 Integration with Project Argus

### Deploy Trained Model

After training and evaluation:

1. Choose the best model based on metrics
2. Copy model file to production directory:
   ```bash
   cp model_training/results/models/randomforest_model.pkl data/models/
   cp model_training/results/models/preprocessor.pkl data/models/
   ```

3. Update system configuration to use the new model

### Use with Existing Pipeline

The trained models integrate seamlessly with the existing feature preprocessing and trust scoring system.

## 📝 Example Workflow

```bash
# Step 1: Prepare synthetic data for testing
python model_training/prepare_dataset.py \
  --synthetic --num-flows 10000 \
  --output model_training/data/training_data.pkl

# Step 2: Train all models
python model_training/train_basic_models.py \
  --data model_training/data/training_data.pkl \
  --output model_training/results/models/

# Step 3: Create test dataset
python model_training/prepare_dataset.py \
  --synthetic --num-flows 2000 \
  --output model_training/data/test_data.pkl

# Step 4: Compare models
python model_training/compare_models.py \
  --models-dir model_training/results/models/ \
  --test-data model_training/data/test_data.pkl \
  --output model_training/results/metrics/

# Step 5: Visualize results
python model_training/visualize_results.py \
  --results model_training/results/metrics/ \
  --output model_training/results/plots/

# Step 6: Review results and deploy best model
# Open: model_training/results/metrics/comparison_report.html
# View: model_training/results/plots/summary_dashboard.png
```

## 🔒 Security Considerations

- Models trained on one network may not generalize to others
- Regular retraining is recommended (weekly/monthly)
- Always validate model performance on your specific network
- Use test data that represents your actual network patterns
- Monitor false positive rates in production

## 🐛 Troubleshooting

### Issue: ImportError for sklearn
```bash
pip install scikit-learn
```

### Issue: Low model accuracy
- Collect more training data
- Ensure data quality (remove corrupted flows)
- Try different algorithms
- Adjust hyperparameters

### Issue: High false positive rate
- Increase decision threshold
- Collect more diverse normal traffic
- Use ensemble methods (Random Forest)
- Implement whitelist for known-good devices

## 📞 Support

- See [TRAINING_GUIDE.md](TRAINING_GUIDE.md) for detailed instructions
- See [ML_OVERVIEW.md](ML_OVERVIEW.md) for theoretical background
- Check the main [README.md](../README.md) for project overview
- Open GitHub issue for bugs or questions

---

**Note**: This folder focuses on basic supervised machine learning algorithms. For unsupervised anomaly detection using deep learning (Autoencoder) or tree-based methods (Isolation Forest), see the main `train_model.py` script in the project root.

**Happy Training! 🚀🔒**
