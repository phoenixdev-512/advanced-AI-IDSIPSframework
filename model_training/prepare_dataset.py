#!/usr/bin/env python3
"""
Dataset preparation script for model training
"""

import argparse
import logging
import pickle
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.capture.influxdb_manager import InfluxDBManager
from src.config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_synthetic_data(num_flows: int = 10000, anomaly_ratio: float = 0.1) -> tuple:
    """Generate synthetic network flow data with labels
    
    Args:
        num_flows: Total number of flows to generate
        anomaly_ratio: Ratio of anomalous flows (0.0 to 1.0)
        
    Returns:
        Tuple of (flows_list, labels_array)
    """
    logger.info(f"Generating {num_flows} synthetic flows ({anomaly_ratio*100:.1f}% anomalies)...")
    
    num_normal = int(num_flows * (1 - anomaly_ratio))
    num_anomaly = num_flows - num_normal
    
    flows = []
    labels = []
    protocols = ['TCP', 'UDP', 'ICMP']
    
    # Generate normal flows
    for i in range(num_normal):
        flow = {
            'src_ip': f"192.168.1.{np.random.randint(1, 255)}",
            'dst_ip': f"10.0.0.{np.random.randint(1, 255)}",
            'src_port': np.random.randint(1024, 65535),
            'dst_port': np.random.choice([80, 443, 22, 53, 8080, 3306]),
            'protocol': np.random.choice(protocols, p=[0.7, 0.25, 0.05]),
            'flow_duration': max(0.1, np.random.exponential(5)),
            'total_fwd_packets': max(1, int(np.random.poisson(20))),
            'total_bwd_packets': max(1, int(np.random.poisson(15))),
            'total_fwd_bytes': max(100, np.random.normal(5000, 2000)),
            'total_bwd_bytes': max(100, np.random.normal(3000, 1500)),
            'packet_inter_arrival_time': max(0.001, np.random.exponential(0.1))
        }
        flow['total_packets'] = flow['total_fwd_packets'] + flow['total_bwd_packets']
        flow['total_bytes'] = flow['total_fwd_bytes'] + flow['total_bwd_bytes']
        
        flows.append(flow)
        labels.append(0)  # Normal
    
    # Generate anomalous flows (suspicious patterns)
    for i in range(num_anomaly):
        anomaly_type = np.random.choice(['port_scan', 'ddos', 'data_exfil'])
        
        if anomaly_type == 'port_scan':
            # Port scanning: many connections to different ports
            flow = {
                'src_ip': f"192.168.1.{np.random.randint(1, 255)}",
                'dst_ip': f"10.0.0.{np.random.randint(1, 10)}",
                'src_port': np.random.randint(1024, 65535),
                'dst_port': np.random.randint(1, 1024),  # Scanning low ports
                'protocol': 'TCP',
                'flow_duration': max(0.1, np.random.exponential(0.5)),  # Short duration
                'total_fwd_packets': np.random.randint(1, 5),  # Few packets
                'total_bwd_packets': 0,  # No response
                'total_fwd_bytes': np.random.randint(40, 100),  # Small bytes
                'total_bwd_bytes': 0,
                'packet_inter_arrival_time': max(0.001, np.random.exponential(0.01))
            }
        
        elif anomaly_type == 'ddos':
            # DDoS: many packets, high rate
            flow = {
                'src_ip': f"192.168.1.{np.random.randint(1, 255)}",
                'dst_ip': f"10.0.0.{np.random.randint(1, 10)}",
                'src_port': np.random.randint(1024, 65535),
                'dst_port': np.random.choice([80, 443]),
                'protocol': np.random.choice(['TCP', 'UDP']),
                'flow_duration': max(1, np.random.exponential(2)),
                'total_fwd_packets': np.random.randint(500, 2000),  # Many packets
                'total_bwd_packets': np.random.randint(0, 50),
                'total_fwd_bytes': np.random.normal(50000, 10000),  # High bytes
                'total_bwd_bytes': np.random.normal(1000, 500),
                'packet_inter_arrival_time': max(0.0001, np.random.exponential(0.001))  # Very fast
            }
        
        else:  # data_exfil
            # Data exfiltration: large outbound transfer
            flow = {
                'src_ip': f"192.168.1.{np.random.randint(1, 255)}",
                'dst_ip': f"{np.random.randint(1, 255)}.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
                'src_port': np.random.randint(1024, 65535),
                'dst_port': np.random.choice([80, 443, 8080]),
                'protocol': 'TCP',
                'flow_duration': max(10, np.random.exponential(30)),  # Long duration
                'total_fwd_packets': np.random.randint(100, 500),
                'total_bwd_packets': np.random.randint(50, 200),
                'total_fwd_bytes': np.random.normal(500000, 100000),  # Very large
                'total_bwd_bytes': np.random.normal(10000, 5000),
                'packet_inter_arrival_time': max(0.01, np.random.exponential(0.05))
            }
        
        flow['total_packets'] = flow['total_fwd_packets'] + flow['total_bwd_packets']
        flow['total_bytes'] = max(0, flow['total_fwd_bytes'] + flow['total_bwd_bytes'])
        
        flows.append(flow)
        labels.append(1)  # Anomaly
    
    # Shuffle the data
    indices = np.random.permutation(num_flows)
    flows = [flows[i] for i in indices]
    labels = np.array([labels[i] for i in indices])
    
    logger.info(f"Generated {num_normal} normal and {num_anomaly} anomalous flows")
    return flows, labels


def load_from_influxdb(hours: int = 24) -> list:
    """Load flows from InfluxDB
    
    Args:
        hours: Hours of historical data to load
        
    Returns:
        List of flow dictionaries
    """
    logger.info(f"Loading {hours} hours of data from InfluxDB...")
    
    influxdb = InfluxDBManager(
        url=config.influxdb_url,
        token=config.influxdb_token,
        org=config.influxdb_org,
        bucket=config.influxdb_bucket
    )
    
    flows = influxdb.query_recent_flows(hours=hours)
    influxdb.close()
    
    logger.info(f"Loaded {len(flows)} flows from InfluxDB")
    return flows


def load_labeled_data(normal_file: str, attack_file: str) -> tuple:
    """Load labeled data from CSV files
    
    Args:
        normal_file: Path to normal traffic CSV
        attack_file: Path to attack traffic CSV
        
    Returns:
        Tuple of (flows_list, labels_array)
    """
    logger.info(f"Loading labeled data from {normal_file} and {attack_file}...")
    
    # Load normal data
    normal_df = pd.read_csv(normal_file)
    normal_flows = normal_df.to_dict('records')
    normal_labels = np.zeros(len(normal_flows))
    
    # Load attack data
    attack_df = pd.read_csv(attack_file)
    attack_flows = attack_df.to_dict('records')
    attack_labels = np.ones(len(attack_flows))
    
    # Combine
    flows = normal_flows + attack_flows
    labels = np.concatenate([normal_labels, attack_labels])
    
    logger.info(f"Loaded {len(normal_flows)} normal and {len(attack_flows)} attack flows")
    return flows, labels


def save_dataset(flows: list, labels: np.ndarray, output_path: str):
    """Save dataset to pickle file
    
    Args:
        flows: List of flow dictionaries
        labels: Array of labels (if None, unlabeled data)
        output_path: Output file path
    """
    # Create output directory
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save as pickle
    with open(output_path, 'wb') as f:
        pickle.dump({'flows': flows, 'labels': labels}, f)
    
    logger.info(f"Dataset saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Prepare dataset for model training")
    parser.add_argument('--synthetic', action='store_true',
                       help='Generate synthetic data')
    parser.add_argument('--num-flows', type=int, default=10000,
                       help='Number of synthetic flows (default: 10000)')
    parser.add_argument('--anomaly-ratio', type=float, default=0.1,
                       help='Ratio of anomalies in synthetic data (default: 0.1)')
    parser.add_argument('--from-influxdb', action='store_true',
                       help='Load data from InfluxDB')
    parser.add_argument('--hours', type=int, default=24,
                       help='Hours of data from InfluxDB (default: 24)')
    parser.add_argument('--labeled', action='store_true',
                       help='Load labeled data from CSV files')
    parser.add_argument('--normal-file', type=str,
                       help='Path to normal traffic CSV')
    parser.add_argument('--attack-file', type=str,
                       help='Path to attack traffic CSV')
    parser.add_argument('--output', type=str, required=True,
                       help='Output file path (.pkl)')
    
    args = parser.parse_args()
    
    # Load/generate data
    if args.synthetic:
        flows, labels = generate_synthetic_data(args.num_flows, args.anomaly_ratio)
    elif args.from_influxdb:
        flows = load_from_influxdb(args.hours)
        labels = None  # Unlabeled data
    elif args.labeled:
        if not args.normal_file or not args.attack_file:
            parser.error("--labeled requires --normal-file and --attack-file")
        flows, labels = load_labeled_data(args.normal_file, args.attack_file)
    else:
        parser.error("Must specify one of: --synthetic, --from-influxdb, or --labeled")
    
    # Save dataset
    save_dataset(flows, labels, args.output)
    
    logger.info("Dataset preparation completed!")


if __name__ == "__main__":
    main()
