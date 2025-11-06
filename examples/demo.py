#!/usr/bin/env python3
"""
Demo Script - Project Argus Complete Detection Flow

This script demonstrates a complete end-to-end detection flow:
1. Loads sample PCAP data
2. Trains a basic anomaly detection model
3. Processes the traffic through the detection pipeline
4. Displays results including trust scores and detected anomalies

Requirements:
- Run from the project root directory
- Sample PCAP file must exist (run generate_sample_pcap.py first)
"""

import sys
import logging
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import AutoencoderModel, FeaturePreprocessor
from src.scoring import TrustScoreManager, VulnerabilityScanner
from scapy.all import rdpcap

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_flows_from_pcap(pcap_file):
    """Extract network flows from PCAP file"""
    logger.info(f"Reading PCAP file: {pcap_file}")
    
    try:
        packets = rdpcap(str(pcap_file))
        logger.info(f"Loaded {len(packets)} packets")
    except Exception as e:
        logger.error(f"Error reading PCAP: {e}")
        return []
    
    # Group packets into flows (simplified)
    flows = {}
    
    for pkt in packets:
        if pkt.haslayer('IP') and (pkt.haslayer('TCP') or pkt.haslayer('UDP')):
            ip_layer = pkt['IP']
            
            # Determine protocol layer
            if pkt.haslayer('TCP'):
                proto_layer = pkt['TCP']
                protocol = 'TCP'
            else:
                proto_layer = pkt['UDP']
                protocol = 'UDP'
            
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            src_port = proto_layer.sport
            dst_port = proto_layer.dport
            
            # Create flow key (5-tuple)
            flow_key = (src_ip, dst_ip, src_port, dst_port, protocol)
            
            if flow_key not in flows:
                flows[flow_key] = {
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'src_port': src_port,
                    'dst_port': dst_port,
                    'protocol': protocol,
                    'total_fwd_packets': 0,
                    'total_bwd_packets': 0,
                    'total_fwd_bytes': 0,
                    'total_bwd_bytes': 0,
                    'flow_duration': 0,
                    'packet_inter_arrival_time': 0,
                }
            
            # Update flow statistics
            packet_len = len(pkt)
            flows[flow_key]['total_fwd_packets'] += 1
            flows[flow_key]['total_fwd_bytes'] += packet_len
    
    # Convert to list and add derived features
    flow_list = []
    for flow_data in flows.values():
        flow_data['total_packets'] = (
            flow_data['total_fwd_packets'] + 
            flow_data['total_bwd_packets']
        )
        flow_data['total_bytes'] = (
            flow_data['total_fwd_bytes'] + 
            flow_data['total_bwd_bytes']
        )
        flow_list.append(flow_data)
    
    logger.info(f"Extracted {len(flow_list)} network flows")
    return flow_list


def train_demo_model(flows):
    """Train a basic anomaly detection model"""
    logger.info("Training anomaly detection model...")
    
    # Preprocess features
    preprocessor = FeaturePreprocessor()
    X = preprocessor.fit_transform(flows)
    
    if len(X) == 0:
        logger.error("No valid features extracted")
        return None, None
    
    logger.info(f"Training data shape: {X.shape}")
    logger.info(f"Features: {preprocessor.feature_names}")
    
    # Train autoencoder
    model = AutoencoderModel(input_dim=X.shape[1])
    history = model.train(X, epochs=20, batch_size=8)
    
    logger.info(f"Training completed. Final loss: {history['loss'][-1]:.4f}")
    logger.info(f"Anomaly threshold: {model.threshold:.4f}")
    
    return model, preprocessor


def analyze_traffic(flows, model, preprocessor):
    """Analyze traffic flows for anomalies"""
    logger.info("Analyzing traffic for anomalies...")
    
    # Preprocess
    X = preprocessor.transform(flows)
    
    if len(X) == 0:
        logger.warning("No valid features to analyze")
        return {}
    
    # Detect anomalies
    anomaly_scores, is_anomaly = model.predict_anomaly(X)
    
    # Group by source IP
    device_anomalies = {}
    
    for i, flow in enumerate(flows):
        src_ip = flow['src_ip']
        
        if src_ip not in device_anomalies:
            device_anomalies[src_ip] = {
                'flows': [],
                'anomalies': [],
                'anomaly_count': 0,
                'total_flows': 0
            }
        
        device_anomalies[src_ip]['total_flows'] += 1
        device_anomalies[src_ip]['flows'].append(flow)
        
        if is_anomaly[i]:
            device_anomalies[src_ip]['anomalies'].append({
                'flow': flow,
                'score': anomaly_scores[i]
            })
            device_anomalies[src_ip]['anomaly_count'] += 1
    
    return device_anomalies


def calculate_trust_scores(device_anomalies):
    """Calculate trust scores for all devices"""
    logger.info("Calculating device trust scores...")
    
    trust_manager = TrustScoreManager()
    
    for device_ip, data in device_anomalies.items():
        # Register device
        trust_manager.get_or_create_device(device_ip)
        
        # Update behavioral score based on anomalies
        if data['anomaly_count'] > 0:
            # Calculate average anomaly score
            avg_anomaly = np.mean([a['score'] for a in data['anomalies']])
            trust_manager.update_behavioral_score(device_ip, avg_anomaly)
    
    return trust_manager


def print_results(device_anomalies, trust_manager):
    """Print detailed results"""
    print("\n" + "="*80)
    print("PROJECT ARGUS - DEMO RESULTS")
    print("="*80)
    
    print("\n📊 TRAFFIC SUMMARY")
    print("-" * 80)
    total_devices = len(device_anomalies)
    total_flows = sum(d['total_flows'] for d in device_anomalies.values())
    total_anomalies = sum(d['anomaly_count'] for d in device_anomalies.values())
    
    print(f"Total Devices: {total_devices}")
    print(f"Total Flows: {total_flows}")
    print(f"Total Anomalies Detected: {total_anomalies}")
    print(f"Anomaly Rate: {(total_anomalies/total_flows)*100:.1f}%")
    
    print("\n🔍 DEVICE ANALYSIS")
    print("-" * 80)
    
    devices = trust_manager.get_all_devices()
    devices_sorted = sorted(devices, key=lambda d: d.trust_score)
    
    for device in devices_sorted:
        ip = device.device_ip
        data = device_anomalies.get(ip, {})
        
        # Determine status emoji
        if device.trust_score >= 80:
            status = "✅ TRUSTED"
        elif device.trust_score >= 60:
            status = "⚠️  MONITOR"
        else:
            status = "🚨 SUSPICIOUS"
        
        print(f"\n{status} - {ip}")
        print(f"  Trust Score: {device.trust_score:.2f}/100")
        print(f"    ├─ Behavioral: {device.behavioral_score:.2f}")
        print(f"    ├─ Vulnerability: {device.vulnerability_score:.2f}")
        print(f"    └─ Reputation: {device.reputation_score:.2f}")
        print(f"  Total Flows: {data.get('total_flows', 0)}")
        print(f"  Anomalies: {data.get('anomaly_count', 0)}")
        
        if data.get('anomalies'):
            print(f"  Suspicious Activity:")
            for anomaly in data['anomalies'][:3]:  # Show first 3
                flow = anomaly['flow']
                print(f"    └─ {flow['protocol']} {flow['dst_ip']}:{flow['dst_port']} "
                      f"(score: {anomaly['score']:.3f})")
    
    # Low trust devices
    low_trust = trust_manager.get_low_trust_devices(threshold=70.0)
    
    if low_trust:
        print("\n⚠️  LOW TRUST DEVICES (Score < 70)")
        print("-" * 80)
        for device in low_trust:
            print(f"  - {device.device_ip}: {device.trust_score:.2f}")
            print(f"    Recommendation: Review activity, consider quarantine")
    
    print("\n" + "="*80)
    print("Demo completed successfully!")
    print("="*80 + "\n")


def main():
    """Run complete demo"""
    print("\n" + "="*80)
    print("🛡️  PROJECT ARGUS - COMPLETE DETECTION FLOW DEMO")
    print("="*80 + "\n")
    
    # Check for sample PCAP
    pcap_file = Path('examples/demo_data/sample_traffic.pcap')
    
    if not pcap_file.exists():
        print("❌ Sample PCAP file not found!")
        print(f"   Expected: {pcap_file}")
        print("\n   Please run: python3 examples/generate_sample_pcap.py")
        sys.exit(1)
    
    try:
        # Step 1: Load PCAP data
        print("Step 1: Loading sample traffic data...")
        flows = extract_flows_from_pcap(pcap_file)
        
        if not flows:
            print("❌ No flows extracted from PCAP")
            sys.exit(1)
        
        print(f"✓ Loaded {len(flows)} network flows\n")
        
        # Step 2: Train model
        print("Step 2: Training anomaly detection model...")
        model, preprocessor = train_demo_model(flows)
        
        if model is None:
            print("❌ Model training failed")
            sys.exit(1)
        
        print("✓ Model trained successfully\n")
        
        # Step 3: Analyze traffic
        print("Step 3: Analyzing traffic for anomalies...")
        device_anomalies = analyze_traffic(flows, model, preprocessor)
        print(f"✓ Analyzed traffic from {len(device_anomalies)} devices\n")
        
        # Step 4: Calculate trust scores
        print("Step 4: Calculating device trust scores...")
        trust_manager = calculate_trust_scores(device_anomalies)
        print("✓ Trust scores calculated\n")
        
        # Step 5: Display results
        print_results(device_anomalies, trust_manager)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during demo: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
