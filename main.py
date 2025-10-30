#!/usr/bin/env python3
"""
Main entry point for Project Argus
"""

import logging
import argparse
import sys
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.capture.packet_capture import PacketCapture
from src.capture.simulated_capture import SimulatedTrafficGenerator
from src.capture.influxdb_manager import InfluxDBManager
from src.models import AutoencoderModel, FeaturePreprocessor
from src.scoring import TrustScoreManager, VulnerabilityScanner
from src.ips import IPTablesManager
from src.api import app, initialize_api
from src.api.main import set_current_state
from src.dashboard import ArgusDashboard

import uvicorn


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/argus.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ProjectArgus:
    """Main orchestrator for Project Argus"""
    
    def __init__(self, mode: str = "passive"):
        """Initialize Project Argus
        
        Args:
            mode: Operating mode ('passive' for IDS, 'inline' for IPS, 'simulated' for demo)
        """
        self.mode = mode
        self.capture_mode = mode  # Track whether using real or simulated capture
        logger.info(f"Initializing Project Argus in {mode} mode")
        
        # Initialize capture based on mode
        if mode == "simulated":
            self.packet_capture = SimulatedTrafficGenerator(anomaly_rate=0.08)
            self.simulated_mode = True
        else:
            self.packet_capture = PacketCapture(
                interface=config.get('capture.interface', 'eth0'),
                flow_timeout=config.get('capture.flow_timeout', 120)
            )
            self.simulated_mode = False
        
        self.influxdb = InfluxDBManager(
            url=config.influxdb_url,
            token=config.influxdb_token,
            org=config.influxdb_org,
            bucket=config.influxdb_bucket
        )
        
        self.preprocessor = FeaturePreprocessor()
        self.model = None
        
        self.trust_manager = TrustScoreManager(
            behavioral_weight=config.get('trust_score.behavioral_weight', 0.5),
            vulnerability_weight=config.get('trust_score.vulnerability_weight', 0.3),
            reputation_weight=config.get('trust_score.reputation_weight', 0.2),
            decay_rate=config.get('trust_score.decay_rate', 0.95)
        )
        
        self.vulnerability_scanner = VulnerabilityScanner(
            timeout=config.get('vulnerability_scan.periodic_scan_interval', 300)
        )
        
        self.ips_manager = IPTablesManager(
            enabled=(mode == "inline" and config.ips_enabled)
        )
        
        self.running = False
        
        # Load model if exists
        self._load_model()
        
        # Initialize API with restart callback
        async def restart_callback(interface: str, mode: str):
            """Callback for restarting capture from API"""
            # This would need to be handled in a separate thread
            # For now, just log it - actual implementation would require
            # more sophisticated process management
            logger.info(f"Restart requested for interface {interface} in mode {mode}")
            # Note: Actual restart would be handled by a process manager or systemd
            return True
        
        initialize_api(
            self.trust_manager, 
            self.ips_manager, 
            self.vulnerability_scanner,
            restart_callback
        )
        
        # Set initial API state
        interface = config.get('capture.interface', 'eth0')
        set_current_state(
            interface if not self.simulated_mode else 'simulated',
            'simulated' if self.simulated_mode else 'passive'
        )
        
        logger.info("Project Argus initialized successfully")
    
    def _load_model(self):
        """Load trained model if available"""
        model_path = Path(config.model_path)
        preprocessor_path = Path('data/models/preprocessor.pkl')
        
        if model_path.exists() and preprocessor_path.exists():
            try:
                self.model = AutoencoderModel(input_dim=17)  # Will be overwritten
                self.model.load_model(str(model_path))
                self.preprocessor.load(str(preprocessor_path))
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                self.model = None
        else:
            logger.warning("No trained model found. Run train_model.py first.")
    
    def _process_flows(self):
        """Background thread to process completed flows"""
        while self.running:
            try:
                # Get completed flows
                flows = self.packet_capture.get_completed_flows(clear=True)
                
                if flows:
                    logger.info(f"Processing {len(flows)} completed flows")
                    
                    # Store in InfluxDB
                    self.influxdb.write_flows(flows)
                    
                    # Process with ML model if available
                    if self.model and self.preprocessor:
                        self._analyze_flows(flows)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error processing flows: {e}")
    
    def _analyze_flows(self, flows):
        """Analyze flows for anomalies"""
        try:
            # Preprocess features
            X = self.preprocessor.transform(flows)
            
            if len(X) == 0:
                return
            
            # Predict anomalies
            anomaly_scores, is_anomaly = self.model.predict_anomaly(X)
            
            # Update trust scores
            for i, flow in enumerate(flows):
                device_ip = flow['src_ip']
                
                if is_anomaly[i]:
                    logger.warning(f"Anomaly detected from {device_ip}: "
                                 f"score={anomaly_scores[i]:.4f}")
                    
                    # Update behavioral score
                    self.trust_manager.update_behavioral_score(
                        device_ip, 
                        anomaly_scores[i]
                    )
                    
                    # Write anomaly to InfluxDB
                    self.influxdb.write_anomaly(device_ip, anomaly_scores[i], flow)
                    
                    # Check if action needed
                    device = self.trust_manager.get_device_score(device_ip)
                    if device and device.trust_score < config.trust_score_critical:
                        logger.critical(f"Critical trust score for {device_ip}: "
                                      f"{device.trust_score:.2f}")
                        
                        if config.auto_block_enabled:
                            self.ips_manager.quarantine_ip(device_ip)
                            self.influxdb.write_alert(
                                device_ip, 
                                "auto_quarantine", 
                                "critical",
                                f"Device quarantined due to low trust score"
                            )
                
                # Update device score in InfluxDB
                device = self.trust_manager.get_device_score(device_ip)
                if device:
                    self.influxdb.write_device_score(
                        device_ip,
                        device.trust_score,
                        device.behavioral_score,
                        device.vulnerability_score,
                        device.reputation_score
                    )
        
        except Exception as e:
            logger.error(f"Error analyzing flows: {e}")
    
    def _scan_new_devices(self):
        """Background thread to scan new devices"""
        scanned_devices = set()
        
        while self.running:
            try:
                # Get all devices
                devices = self.trust_manager.get_all_devices()
                
                for device in devices:
                    if device.device_ip not in scanned_devices:
                        logger.info(f"Scanning new device: {device.device_ip}")
                        
                        # Scan for vulnerabilities
                        scan_results = self.vulnerability_scanner.scan_device(
                            device.device_ip, quick=True
                        )
                        
                        if scan_results.get('scan_success'):
                            vulnerable_ports = scan_results.get('vulnerable_ports', [])
                            
                            # Update vulnerability score
                            self.trust_manager.update_vulnerability_score(
                                device.device_ip,
                                vulnerable_ports
                            )
                            
                            if vulnerable_ports:
                                logger.warning(f"Vulnerabilities found on {device.device_ip}: "
                                             f"{vulnerable_ports}")
                                self.influxdb.write_alert(
                                    device.device_ip,
                                    "vulnerability",
                                    "medium",
                                    f"Found {len(vulnerable_ports)} vulnerable ports"
                                )
                        
                        scanned_devices.add(device.device_ip)
                
                time.sleep(60)  # Scan check every minute
                
            except Exception as e:
                logger.error(f"Error scanning devices: {e}")
    
    def _apply_score_decay(self):
        """Background thread to apply score decay"""
        while self.running:
            try:
                self.trust_manager.apply_score_decay(hours_elapsed=1.0)
                time.sleep(3600)  # Every hour
            except Exception as e:
                logger.error(f"Error applying score decay: {e}")
    
    def _check_quarantine_expiry(self):
        """Background thread to check quarantine expiry"""
        while self.running:
            try:
                self.ips_manager.check_quarantine_expiry()
                time.sleep(60)  # Every minute
            except Exception as e:
                logger.error(f"Error checking quarantine expiry: {e}")
    
    def start_capture(self):
        """Start packet capture"""
        logger.info(f"Starting capture in {self.capture_mode} mode...")
        self.running = True
        
        # Start background threads
        flow_thread = threading.Thread(target=self._process_flows, daemon=True)
        flow_thread.start()
        
        scan_thread = threading.Thread(target=self._scan_new_devices, daemon=True)
        scan_thread.start()
        
        decay_thread = threading.Thread(target=self._apply_score_decay, daemon=True)
        decay_thread.start()
        
        quarantine_thread = threading.Thread(target=self._check_quarantine_expiry, daemon=True)
        quarantine_thread.start()
        
        # Start packet capture based on mode
        try:
            if self.simulated_mode:
                self.packet_capture.start_generation()
                # Keep running until interrupted
                while self.running:
                    time.sleep(1)
            else:
                self.packet_capture.start_capture()
        except KeyboardInterrupt:
            logger.info("Capture interrupted by user")
        finally:
            self.stop()
    
    def switch_interface(self, interface: str, mode: str = "passive"):
        """Switch network interface dynamically
        
        Args:
            interface: New interface name
            mode: 'passive' for real traffic, 'simulated' for demo traffic
        """
        logger.info(f"Switching to interface {interface} in {mode} mode")
        
        # Stop current capture
        if self.running:
            self.stop()
            time.sleep(1)  # Give it time to stop
        
        # Update mode
        self.capture_mode = mode
        
        # Reinitialize capture
        if interface == 'simulated' or mode == 'simulated':
            self.packet_capture = SimulatedTrafficGenerator(anomaly_rate=0.08)
            self.simulated_mode = True
            logger.info("Switched to simulated traffic mode")
        else:
            self.packet_capture = PacketCapture(
                interface=interface,
                flow_timeout=config.get('capture.flow_timeout', 120)
            )
            self.simulated_mode = False
            config.update_interface(interface)
            logger.info(f"Switched to interface: {interface}")
        
        # Restart capture
        self.start_capture()
    
    def stop(self):
        """Stop all components"""
        logger.info("Stopping Project Argus...")
        self.running = False
        self.packet_capture.stop()
        self.influxdb.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Project Argus - AI-Driven NIDS/NIPS")
    parser.add_argument('command', choices=['start', 'api', 'dashboard', 'full'],
                       help='Command to run')
    parser.add_argument('--mode', choices=['passive', 'inline'], default='passive',
                       help='Operating mode (default: passive)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--api-port', type=int, default=8000,
                       help='API port (default: 8000)')
    parser.add_argument('--dashboard-port', type=int, default=8050,
                       help='Dashboard port (default: 8050)')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        # Start packet capture only
        argus = ProjectArgus(mode=args.mode)
        argus.start_capture()
    
    elif args.command == 'api':
        # Start API server only
        logger.info(f"Starting API server on {args.host}:{args.api_port}")
        argus = ProjectArgus(mode=args.mode)
        uvicorn.run(app, host=args.host, port=args.api_port)
    
    elif args.command == 'dashboard':
        # Start dashboard only
        logger.info(f"Starting dashboard on {args.host}:{args.dashboard_port}")
        dashboard = ArgusDashboard(api_url=f"http://localhost:{args.api_port}")
        dashboard.run(host=args.host, port=args.dashboard_port)
    
    elif args.command == 'full':
        # Start everything
        argus = ProjectArgus(mode=args.mode)
        
        # Start API in thread
        api_thread = threading.Thread(
            target=lambda: uvicorn.run(app, host=args.host, port=args.api_port),
            daemon=True
        )
        api_thread.start()
        
        # Start dashboard in thread
        dashboard = ArgusDashboard(api_url=f"http://localhost:{args.api_port}")
        dashboard_thread = threading.Thread(
            target=lambda: dashboard.run(host=args.host, port=args.dashboard_port),
            daemon=True
        )
        dashboard_thread.start()
        
        # Start capture in main thread
        argus.start_capture()


if __name__ == "__main__":
    main()
