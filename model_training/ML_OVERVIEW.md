# Machine Learning in Project Argus - Overview

## Table of Contents
1. [Introduction](#introduction)
2. [Role of ML in IDS/IPS](#role-of-ml-in-idsips)
3. [Problem Statement](#problem-statement)
4. [ML Approach](#ml-approach)
5. [Algorithms Used](#algorithms-used)
6. [Feature Engineering](#feature-engineering)
7. [Training Process](#training-process)
8. [Model Evaluation](#model-evaluation)
9. [Deployment](#deployment)

---

## Introduction

Project Argus is an AI-driven Network Intrusion Detection System (NIDS) and Intrusion Prevention System (NIPS) designed for Small Office/Home Office (SOHO) networks. Machine Learning is at the core of this system, enabling intelligent detection of anomalous network behavior that could indicate security threats.

## Role of ML in IDS/IPS

### Why Machine Learning?

Traditional rule-based IDS/IPS systems rely on predefined signatures and patterns to detect known attacks. However, they struggle with:
- **Zero-day attacks**: New, unknown threats
- **Polymorphic malware**: Attacks that change their signature
- **Insider threats**: Compromised internal devices behaving abnormally
- **Sophisticated APTs**: Advanced persistent threats using novel techniques

### How ML Solves These Problems

Machine Learning, specifically **anomaly detection**, addresses these challenges by:

1. **Learning Normal Behavior**: The ML models learn what "normal" network traffic looks like for each device
2. **Detecting Deviations**: Any significant deviation from normal behavior triggers an alert
3. **Adapting Over Time**: Models can be retrained to adapt to evolving network patterns
4. **No Signature Required**: Detects anomalies without needing to know specific attack signatures

## Problem Statement

**Objective**: Develop ML models that can accurately distinguish between normal and anomalous network traffic in real-time on resource-constrained hardware (Raspberry Pi).

**Challenges**:
- Limited computational resources (Raspberry Pi 4/5)
- Real-time processing requirements
- High-dimensional network traffic data
- Imbalanced datasets (normal traffic >> anomalous traffic)
- Need for interpretable results for security analysts

## ML Approach

### Unsupervised Anomaly Detection

Project Argus primarily uses **unsupervised learning** because:
- Labeled attack data is scarce and quickly becomes outdated
- Normal traffic patterns are easier to define than all possible attacks
- Can detect novel, unknown threats

### Primary Techniques

1. **Autoencoder Neural Networks** (Deep Learning)
   - Learns compressed representation of normal traffic
   - Reconstruction error indicates anomalies
   - Best for complex, non-linear patterns

2. **Isolation Forest** (Tree-based)
   - Fast, efficient algorithm
   - Works well with high-dimensional data
   - Good for real-time detection

3. **Supervised Classification** (Baseline)
   - Random Forest, Decision Trees, SVM, Logistic Regression
   - Used when labeled data is available
   - Provides interpretable baseline comparisons

## Algorithms Used

### 1. Autoencoder Neural Network (Primary)

**Type**: Deep Learning, Unsupervised

**How it works**:
- Encoder compresses normal traffic into lower-dimensional representation
- Decoder reconstructs the original input
- For normal traffic: reconstruction error is low
- For anomalies: reconstruction error is high (model hasn't seen this pattern)

**Architecture**:
```
Input (n features) → Dense(64) → Dense(32) → Dense(16) → Dense(32) [encoding]
                                                          ↓
Dense(16) → Dense(32) → Dense(64) → Output (n features) [decoding]
```

**Advantages**:
- Detects complex, non-linear anomalies
- No labels required
- Learns hierarchical feature representations

**Limitations**:
- Requires more computational resources
- Black-box model (less interpretable)
- Needs careful threshold tuning

### 2. Isolation Forest (Alternative)

**Type**: Tree-based, Unsupervised

**How it works**:
- Randomly partitions data using decision trees
- Anomalies are isolated in fewer partitions (easier to separate)
- Anomaly score based on average path length in trees

**Advantages**:
- Fast training and inference
- Works well with high-dimensional data
- Memory efficient
- Good for real-time scenarios

**Limitations**:
- May miss subtle anomalies
- Performance depends on contamination parameter

### 3. Random Forest Classifier (Supervised)

**Type**: Ensemble, Supervised

**How it works**:
- Ensemble of decision trees
- Each tree votes on the classification
- Majority vote determines the final prediction

**Use case**: When labeled attack data is available

**Advantages**:
- High accuracy with labeled data
- Handles non-linear relationships
- Feature importance rankings
- Robust to overfitting

### 4. Decision Tree Classifier (Supervised)

**Type**: Tree-based, Supervised

**How it works**:
- Splits data based on feature values
- Creates a tree of decision rules
- Easy to interpret and visualize

**Use case**: Baseline comparison, interpretability

**Advantages**:
- Highly interpretable
- Fast prediction
- No feature scaling required
- Handles both numerical and categorical data

### 5. Logistic Regression (Supervised)

**Type**: Linear, Supervised

**How it works**:
- Linear combination of features
- Sigmoid function for binary classification
- Probability-based predictions

**Use case**: Baseline, feature importance analysis

**Advantages**:
- Fast and simple
- Interpretable coefficients
- Low computational cost
- Good baseline for comparison

### 6. Support Vector Machine (Supervised)

**Type**: Kernel-based, Supervised

**How it works**:
- Finds optimal hyperplane to separate classes
- Can use kernel trick for non-linear boundaries
- Maximizes margin between classes

**Use case**: Small to medium datasets with clear separation

**Advantages**:
- Effective in high-dimensional spaces
- Memory efficient
- Versatile (different kernel functions)

## Feature Engineering

### Network Flow Features

Features extracted from network traffic flows:

**Basic Flow Features**:
- Source/Destination ports
- Protocol (TCP, UDP, ICMP)
- Flow duration
- Total packets (forward/backward)
- Total bytes (forward/backward)

**Derived Statistical Features**:
- Packet rate (packets/second)
- Byte rate (bytes/second)
- Packet size statistics (mean, std, min, max)
- Inter-arrival time statistics
- Forward/Backward ratio
- Protocol distribution

**Behavioral Features**:
- Connection patterns
- Port scanning indicators
- Data transfer patterns
- Time-based patterns

### Feature Preprocessing

1. **Normalization**: StandardScaler for zero mean, unit variance
2. **Encoding**: One-hot encoding for categorical features (protocol)
3. **Scaling**: MinMaxScaler for neural networks (0-1 range)
4. **Missing Values**: Forward fill or mean imputation

## Training Process

### Data Collection

1. **Normal Traffic Collection**: 24-48 hours of baseline network activity
2. **Synthetic Data Generation**: For testing and initial training
3. **Attack Simulation**: Optional labeled attack data for supervised models

### Training Pipeline

```
Raw Packets → Flow Aggregation → Feature Extraction → Preprocessing
                                                          ↓
                                              Train/Validation Split
                                                          ↓
                                                  Model Training
                                                          ↓
                                              Threshold Calibration
                                                          ↓
                                                Model Evaluation
                                                          ↓
                                            Save Model + Preprocessor
```

### Model Training Steps

1. **Data Preparation**: Load and preprocess flows
2. **Train/Validation Split**: 80/20 split
3. **Model Training**: Fit model on training data
4. **Threshold Tuning**: Set anomaly threshold (95th percentile)
5. **Validation**: Test on validation set
6. **Model Export**: Save model and preprocessor

### Optimization for Raspberry Pi

- **TFLite Conversion**: Convert Keras models to TensorFlow Lite
- **Quantization**: Reduce model size and inference time
- **Batch Processing**: Process flows in batches, not packets
- **Model Compression**: Prune unnecessary weights

## Model Evaluation

### Metrics for Anomaly Detection

Since normal traffic >> anomalous traffic (imbalanced):

1. **Precision**: TP / (TP + FP)
   - What % of detected anomalies are real?
   - Critical to minimize false alarms

2. **Recall**: TP / (TP + FN)
   - What % of real anomalies were detected?
   - Critical for security

3. **F1-Score**: Harmonic mean of Precision and Recall
   - Balanced metric for model comparison

4. **ROC-AUC**: Area under ROC curve
   - Threshold-independent performance

5. **Reconstruction Error Distribution**: For autoencoders
   - Separation between normal and anomalous

### Evaluation Strategy

1. **Validation Set**: Held-out normal traffic (20%)
2. **Attack Simulation**: Known attack patterns
3. **Real-world Testing**: Passive monitoring mode
4. **A/B Testing**: Compare model versions

### Success Criteria

- **False Positive Rate**: < 1% (minimize false alarms)
- **True Positive Rate**: > 95% (detect most threats)
- **Inference Time**: < 100ms per flow (real-time requirement)
- **Model Size**: < 50MB (Raspberry Pi constraint)

## Deployment

### Model Lifecycle

1. **Training**: On development machine or cloud
2. **Conversion**: TFLite for Raspberry Pi
3. **Deployment**: Copy models to `/data/models/`
4. **Loading**: Load at system startup
5. **Inference**: Real-time anomaly detection
6. **Monitoring**: Track model performance
7. **Retraining**: Periodic updates with new normal data

### Integration with Trust Scoring

ML anomaly scores feed into the multi-factor **Trust Score System**:

```
Trust Score = (Behavioral Score × 0.5) + (Vulnerability × 0.3) + (Reputation × 0.2)
```

**Behavioral Score** comes from ML models:
- High reconstruction error → Low behavioral score
- Anomaly detected → Score penalty
- Normal behavior → Score recovery

### Real-time Pipeline

```
Packet Capture → Flow Extraction → Feature Preprocessing
                                            ↓
                                    ML Model Inference
                                            ↓
                                    Anomaly Score Calculation
                                            ↓
                                    Trust Score Update
                                            ↓
                            IPS Action (if score < threshold)
```

## Benefits of ML Approach

1. **Proactive Detection**: Finds unknown threats
2. **Adaptive**: Learns network-specific patterns
3. **Automated**: Minimal manual rule creation
4. **Scalable**: Handles large volumes of traffic
5. **Privacy**: All processing on-device
6. **Cost-effective**: Runs on commodity hardware

## Limitations and Future Work

### Current Limitations

- Requires training period (24-48 hours)
- Potential false positives during network changes
- Model drift over time
- Limited to network flow features (no payload inspection)

### Future Enhancements

- **Online Learning**: Continuous model updates
- **Ensemble Models**: Combine multiple algorithms
- **Deep Packet Inspection**: Payload analysis
- **Federated Learning**: Learn from multiple deployments
- **Advanced Techniques**: GANs, RNNs for sequence modeling
- **Explainable AI**: Better interpretability of decisions

---

## Conclusion

Machine Learning transforms Project Argus from a signature-based system into an intelligent, adaptive security platform. By learning normal behavior and detecting deviations, the system can protect against both known and unknown threats, making advanced network security accessible to SOHO environments.
