#!/usr/bin/env python3
"""
Train the anomaly detection model for Project Argus
"""

import logging
import argparse
import sys
import json
from pathlib import Path

# Check for required dependencies before importing project modules
try:
    import yaml
    import numpy as np
except ImportError as e:
    missing_module = str(e).split("'")[1]
    print("\n" + "=" * 70)
    print(f"ERROR: Required dependency '{missing_module}' is not installed!")
    print("=" * 70)
    print("\nTo fix this issue, please install the required dependencies:")
    print("\n  pip install -r requirements.txt")
    if missing_module == 'yaml':
        print("\nOr install PyYAML specifically:")
        print("\n  pip install pyyaml")
    print("\nFor more information, see README.md or DEPLOYMENT_GUIDE.md")
    print("=" * 70 + "\n")
    sys.exit(1)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.capture.influxdb_manager import InfluxDBManager
from src.models import AutoencoderModel, IsolationForestModel, FeaturePreprocessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def collect_training_data(influxdb: InfluxDBManager, hours: int = 24) -> list:
    """Collect training data from InfluxDB
    
    Args:
        influxdb: InfluxDB manager instance
        hours: Number of hours of data to collect
        
    Returns:
        List of flow dictionaries
    """
    logger.info(f"Collecting {hours} hours of training data...")
    flows = influxdb.query_recent_flows(hours=hours)
    logger.info(f"Collected {len(flows)} flows")
    return flows


def train_autoencoder(flows: list, save_dir: str = "data/models") -> AutoencoderModel:
    """Train Autoencoder model
    
    Args:
        flows: List of flow dictionaries
        save_dir: Directory to save model
        
    Returns:
        Trained AutoencoderModel
    """
    logger.info("Training Autoencoder model...")
    
    # Preprocess features
    preprocessor = FeaturePreprocessor()
    X_train = preprocessor.fit_transform(flows)
    
    logger.info(f"Training data shape: {X_train.shape}")
    logger.info(f"Features: {preprocessor.feature_names}")
    
    # Create and train model
    model = AutoencoderModel(
        input_dim=X_train.shape[1],
        encoding_dim=config.get('model.architecture.encoding_dim', 32),
        hidden_layers=config.get('model.architecture.hidden_layers', [64, 32, 16])
    )
    
    history = model.train(
        X_train,
        epochs=config.get('model.training.epochs', 100),
        batch_size=config.get('model.training.batch_size', 32),
        validation_split=config.get('model.training.validation_split', 0.2)
    )
    
    # Save model and preprocessor
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    
    model_path = f"{save_dir}/autoencoder.h5"
    model.save_model(model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Convert to TFLite
    tflite_path = f"{save_dir}/autoencoder.tflite"
    model.convert_to_tflite(tflite_path)
    logger.info(f"TFLite model saved to {tflite_path}")
    
    # Save preprocessor
    preprocessor_path = f"{save_dir}/preprocessor.pkl"
    preprocessor.save(preprocessor_path)
    logger.info(f"Preprocessor saved to {preprocessor_path}")
    
    # Save training history
    history_path = f"{save_dir}/training_history.json"
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    logger.info(f"Training history saved to {history_path}")
    
    # Feature importance
    importance = preprocessor.get_feature_importance(X_train)
    logger.info("Feature importance:")
    for feature, score in importance.items():
        logger.info(f"  {feature}: {score:.4f}")
    
    return model


def train_isolation_forest(flows: list, save_dir: str = "data/models") -> IsolationForestModel:
    """Train Isolation Forest model
    
    Args:
        flows: List of flow dictionaries
        save_dir: Directory to save model
        
    Returns:
        Trained IsolationForestModel
    """
    logger.info("Training Isolation Forest model...")
    
    # Preprocess features
    preprocessor = FeaturePreprocessor()
    X_train = preprocessor.fit_transform(flows)
    
    logger.info(f"Training data shape: {X_train.shape}")
    logger.info(f"Features: {preprocessor.feature_names}")
    
    # Create and train model
    model = IsolationForestModel(
        contamination=0.1,
        n_estimators=100
    )
    
    model.train(X_train)
    
    # Save model and preprocessor
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    
    model_path = f"{save_dir}/isolation_forest.pkl"
    model.save_model(model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Save preprocessor
    preprocessor_path = f"{save_dir}/preprocessor.pkl"
    preprocessor.save(preprocessor_path)
    logger.info(f"Preprocessor saved to {preprocessor_path}")
    
    return model


def generate_synthetic_data(num_flows: int = 1000) -> list:
    """Generate synthetic training data for testing
    
    Args:
        num_flows: Number of flows to generate
        
    Returns:
        List of synthetic flow dictionaries
    """
    logger.info(f"Generating {num_flows} synthetic flows...")
    
    flows = []
    protocols = ['TCP', 'UDP', 'ICMP']
    
    for i in range(num_flows):
        flow = {
            'src_ip': f"192.168.1.{np.random.randint(1, 255)}",
            'dst_ip': f"10.0.0.{np.random.randint(1, 255)}",
            'src_port': np.random.randint(1024, 65535),
            'dst_port': np.random.choice([80, 443, 22, 53, 8080]),
            'protocol': np.random.choice(protocols),
            'flow_duration': np.random.exponential(10),
            'total_fwd_packets': np.random.poisson(20),
            'total_bwd_packets': np.random.poisson(15),
            'total_fwd_bytes': np.random.normal(5000, 2000),
            'total_bwd_bytes': np.random.normal(3000, 1500),
            'total_packets': 0,
            'total_bytes': 0,
            'packet_inter_arrival_time': np.random.exponential(0.1)
        }
        
        flow['total_packets'] = flow['total_fwd_packets'] + flow['total_bwd_packets']
        flow['total_bytes'] = max(0, flow['total_fwd_bytes'] + flow['total_bwd_bytes'])
        
        flows.append(flow)
    
    return flows


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Train Project Argus anomaly detection model")
    parser.add_argument('--model', choices=['autoencoder', 'isolation_forest'], 
                       default='autoencoder',
                       help='Model type to train')
    parser.add_argument('--hours', type=int, default=24,
                       help='Hours of data to use for training (default: 24)')
    parser.add_argument('--synthetic', action='store_true',
                       help='Generate synthetic training data instead of using InfluxDB')
    parser.add_argument('--num-flows', type=int, default=1000,
                       help='Number of synthetic flows to generate (default: 1000)')
    parser.add_argument('--save-dir', default='data/models',
                       help='Directory to save model (default: data/models)')
    
    args = parser.parse_args()
    
    # Get training data
    if args.synthetic:
        flows = generate_synthetic_data(args.num_flows)
    else:
        # Connect to InfluxDB
        influxdb = InfluxDBManager(
            url=config.influxdb_url,
            token=config.influxdb_token,
            org=config.influxdb_org,
            bucket=config.influxdb_bucket
        )
        
        flows = collect_training_data(influxdb, hours=args.hours)
        influxdb.close()
        
        if not flows:
            logger.error("No training data available. Use --synthetic flag or collect data first.")
            return
    
    # Train model
    if args.model == 'autoencoder':
        model = train_autoencoder(flows, save_dir=args.save_dir)
    else:
        model = train_isolation_forest(flows, save_dir=args.save_dir)
    
    logger.info("Training completed successfully!")


if __name__ == "__main__":
    main()
