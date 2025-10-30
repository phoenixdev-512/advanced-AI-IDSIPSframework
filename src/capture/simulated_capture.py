"""
Simulated network traffic generator for demonstration purposes
"""

import time
import random
import logging
from typing import Dict, List, Any
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class SimulatedTrafficGenerator:
    """Generates synthetic network traffic for demonstration"""
    
    def __init__(self, anomaly_rate: float = 0.08):
        """Initialize simulated traffic generator
        
        Args:
            anomaly_rate: Percentage of flows that should be anomalous (0.0-1.0)
        """
        self.anomaly_rate = anomaly_rate
        self.running = False
        self.completed_flows: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
        # Common device IPs for simulation
        self.device_ips = [
            '192.168.1.10',  # Laptop
            '192.168.1.11',  # Desktop
            '192.168.1.20',  # Smartphone
            '192.168.1.21',  # Tablet
            '192.168.1.30',  # Smart TV
            '192.168.1.31',  # Smart Speaker
            '192.168.1.40',  # IoT Camera
            '192.168.1.41',  # IoT Sensor
        ]
        
        # Common destination IPs (external services)
        self.external_ips = [
            '8.8.8.8',       # Google DNS
            '1.1.1.1',       # Cloudflare DNS
            '172.217.14.206',  # Google services
            '151.101.1.140',   # Reddit
            '104.244.42.129',  # Twitter
            '157.240.2.35',    # Facebook
            '13.107.42.14',    # Microsoft
        ]
        
        # Common services
        self.normal_ports = {
            'HTTP': 80,
            'HTTPS': 443,
            'DNS': 53,
            'NTP': 123,
            'SMTP': 587,
        }
        
        # Suspicious services (for anomalies)
        self.suspicious_ports = {
            'Telnet': 23,
            'FTP': 21,
            'SMB': 445,
            'RDP': 3389,
            'SSH_Scan': 22,
        }
        
        logger.info(f"SimulatedTrafficGenerator initialized (anomaly_rate={anomaly_rate})")
    
    def _generate_normal_flow(self) -> Dict[str, Any]:
        """Generate a normal network flow"""
        src_ip = random.choice(self.device_ips)
        dst_ip = random.choice(self.external_ips)
        
        # Random normal service
        service = random.choice(list(self.normal_ports.keys()))
        dst_port = self.normal_ports[service]
        src_port = random.randint(49152, 65535)  # Ephemeral port
        
        # Normal flow characteristics
        duration = random.uniform(0.5, 30.0)
        fwd_packets = random.randint(5, 100)
        bwd_packets = random.randint(3, fwd_packets)
        fwd_bytes = random.randint(500, 50000)
        bwd_bytes = random.randint(300, fwd_bytes)
        
        return {
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': src_port,
            'dst_port': dst_port,
            'protocol': 'TCP' if service != 'DNS' else 'UDP',
            'flow_duration': duration,
            'total_fwd_packets': fwd_packets,
            'total_bwd_packets': bwd_packets,
            'total_fwd_bytes': fwd_bytes,
            'total_bwd_bytes': bwd_bytes,
            'total_packets': fwd_packets + bwd_packets,
            'total_bytes': fwd_bytes + bwd_bytes,
            'packet_inter_arrival_time': duration / (fwd_packets + bwd_packets) if (fwd_packets + bwd_packets) > 0 else 0.01,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_anomalous_flow(self) -> Dict[str, Any]:
        """Generate an anomalous network flow"""
        anomaly_type = random.choice(['port_scan', 'data_exfiltration', 'ddos', 'suspicious_service'])
        
        if anomaly_type == 'port_scan':
            # Port scanning pattern
            src_ip = random.choice(self.device_ips)
            dst_ip = random.choice(self.external_ips)
            src_port = random.randint(49152, 65535)
            dst_port = random.randint(1, 1024)  # Scanning low ports
            
            return {
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': 'TCP',
                'flow_duration': 0.1,  # Very short
                'total_fwd_packets': 1,
                'total_bwd_packets': 0,  # No response
                'total_fwd_bytes': 60,
                'total_bwd_bytes': 0,
                'total_packets': 1,
                'total_bytes': 60,
                'packet_inter_arrival_time': 0.01,
                'timestamp': datetime.now().isoformat()
            }
        
        elif anomaly_type == 'data_exfiltration':
            # Large data upload
            src_ip = random.choice(self.device_ips)
            dst_ip = random.choice(self.external_ips)
            src_port = random.randint(49152, 65535)
            dst_port = 443  # HTTPS
            
            return {
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': 'TCP',
                'flow_duration': random.uniform(60, 300),
                'total_fwd_packets': random.randint(500, 2000),
                'total_bwd_packets': random.randint(50, 200),
                'total_fwd_bytes': random.randint(500000, 5000000),  # Large upload
                'total_bwd_bytes': random.randint(5000, 50000),
                'total_packets': random.randint(550, 2200),
                'total_bytes': random.randint(505000, 5050000),
                'packet_inter_arrival_time': 0.001,  # Fast packets
                'timestamp': datetime.now().isoformat()
            }
        
        elif anomaly_type == 'ddos':
            # DDoS pattern - many packets to same destination
            src_ip = random.choice(self.device_ips)
            dst_ip = random.choice(self.external_ips)
            src_port = random.randint(49152, 65535)
            dst_port = 80
            
            return {
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': 'TCP',
                'flow_duration': random.uniform(0.1, 1.0),
                'total_fwd_packets': random.randint(1000, 5000),
                'total_bwd_packets': 0,
                'total_fwd_bytes': random.randint(60000, 300000),
                'total_bwd_bytes': 0,
                'total_packets': random.randint(1000, 5000),
                'total_bytes': random.randint(60000, 300000),
                'packet_inter_arrival_time': 0.0001,  # Very fast
                'timestamp': datetime.now().isoformat()
            }
        
        else:  # suspicious_service
            # Connection to suspicious port
            src_ip = random.choice(self.device_ips)
            dst_ip = random.choice(self.external_ips)
            service = random.choice(list(self.suspicious_ports.keys()))
            dst_port = self.suspicious_ports[service]
            src_port = random.randint(49152, 65535)
            
            return {
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': 'TCP',
                'flow_duration': random.uniform(1.0, 30.0),
                'total_fwd_packets': random.randint(10, 50),
                'total_bwd_packets': random.randint(5, 40),
                'total_fwd_bytes': random.randint(1000, 10000),
                'total_bwd_bytes': random.randint(500, 8000),
                'total_packets': random.randint(15, 90),
                'total_bytes': random.randint(1500, 18000),
                'packet_inter_arrival_time': 0.1,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generation_thread(self):
        """Background thread for generating flows"""
        logger.info("Starting simulated traffic generation")
        
        while self.running:
            try:
                # Generate a flow
                if random.random() < self.anomaly_rate:
                    flow = self._generate_anomalous_flow()
                    logger.debug(f"Generated anomalous flow: {flow['src_ip']} -> {flow['dst_ip']}:{flow['dst_port']}")
                else:
                    flow = self._generate_normal_flow()
                
                with self.lock:
                    self.completed_flows.append(flow)
                
                # Wait before generating next flow (simulate realistic timing)
                time.sleep(random.uniform(0.1, 2.0))
                
            except Exception as e:
                logger.error(f"Error generating simulated flow: {e}")
    
    def start_generation(self):
        """Start generating simulated traffic"""
        if self.running:
            logger.warning("Simulated traffic generation already running")
            return
        
        self.running = True
        self.generation_thread = threading.Thread(target=self._generation_thread, daemon=True)
        self.generation_thread.start()
        logger.info("Simulated traffic generation started")
    
    def stop_generation(self):
        """Stop generating simulated traffic"""
        self.running = False
        logger.info("Simulated traffic generation stopped")
    
    def get_completed_flows(self, clear: bool = True) -> List[Dict[str, Any]]:
        """Get completed flows
        
        Args:
            clear: Whether to clear the completed flows list after retrieval
            
        Returns:
            List of completed flow dictionaries
        """
        with self.lock:
            flows = self.completed_flows.copy()
            if clear:
                self.completed_flows.clear()
        
        return flows
    
    def stop(self):
        """Stop the generator"""
        self.stop_generation()
