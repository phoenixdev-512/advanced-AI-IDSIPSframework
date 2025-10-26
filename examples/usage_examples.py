"""
Example usage of Project Argus components
"""

import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import AutoencoderModel, FeaturePreprocessor
from src.scoring import TrustScoreManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_model_training():
    """Example: Train anomaly detection model"""
    print("\n=== Model Training Example ===")
    
    # Generate synthetic data
    import numpy as np
    
    synthetic_flows = []
    for i in range(100):
        flow = {
            'src_port': np.random.randint(1024, 65535),
            'dst_port': np.random.choice([80, 443, 22]),
            'protocol': 'TCP',
            'flow_duration': np.random.exponential(10),
            'total_fwd_packets': np.random.poisson(20),
            'total_bwd_packets': np.random.poisson(15),
            'total_fwd_bytes': max(0, np.random.normal(5000, 2000)),
            'total_bwd_bytes': max(0, np.random.normal(3000, 1500)),
            'total_packets': 35,
            'total_bytes': 8000,
            'packet_inter_arrival_time': np.random.exponential(0.1)
        }
        synthetic_flows.append(flow)
    
    # Preprocess features
    preprocessor = FeaturePreprocessor()
    X = preprocessor.fit_transform(synthetic_flows)
    print(f"Training data shape: {X.shape}")
    print(f"Features: {preprocessor.feature_names}")
    
    # Train model
    model = AutoencoderModel(input_dim=X.shape[1])
    print("Training Autoencoder...")
    history = model.train(X, epochs=10, batch_size=16)
    
    print(f"Training completed. Final loss: {history['loss'][-1]:.4f}")
    print(f"Anomaly threshold: {model.threshold:.4f}")


def example_trust_scoring():
    """Example: Trust score management"""
    print("\n=== Trust Score Example ===")
    
    # Initialize trust manager
    manager = TrustScoreManager()
    
    # Register devices
    manager.get_or_create_device("192.168.1.100")
    manager.get_or_create_device("192.168.1.101")
    manager.get_or_create_device("192.168.1.102")
    
    # Simulate anomaly detection
    print("\nDetecting anomaly from 192.168.1.100...")
    manager.update_behavioral_score("192.168.1.100", anomaly_score=0.8)
    
    # Simulate vulnerability scan
    print("Found vulnerable ports on 192.168.1.101...")
    manager.update_vulnerability_score("192.168.1.101", vulnerable_ports=[21, 23])
    
    # Whitelist a device
    print("Whitelisting 192.168.1.102...")
    manager.whitelist_device("192.168.1.102")
    
    # Get all devices
    print("\nDevice Trust Scores:")
    for device in manager.get_all_devices():
        status = ""
        if device.is_whitelisted:
            status = " [WHITELISTED]"
        elif device.is_blacklisted:
            status = " [BLACKLISTED]"
        
        print(f"  {device.device_ip}: {device.trust_score:.2f}{status}")
        print(f"    - Behavioral: {device.behavioral_score:.2f}")
        print(f"    - Vulnerability: {device.vulnerability_score:.2f}")
        print(f"    - Reputation: {device.reputation_score:.2f}")
    
    # Get low trust devices
    low_trust = manager.get_low_trust_devices(threshold=75.0)
    print(f"\nLow trust devices (< 75): {len(low_trust)}")
    for device in low_trust:
        print(f"  - {device.device_ip}: {device.trust_score:.2f}")


def main():
    """Run all examples"""
    print("Project Argus - Usage Examples")
    print("=" * 50)
    
    try:
        example_model_training()
        example_trust_scoring()
        
    except Exception as e:
        logger.error(f"Error in example: {e}", exc_info=True)
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
