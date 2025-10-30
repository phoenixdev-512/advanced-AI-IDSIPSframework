"""
Configuration management for Project Argus
"""

import os
import yaml
import logging
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for Project Argus"""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration
        
        Args:
            config_path: Path to YAML configuration file
        """
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._merge_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _merge_env_vars(self):
        """Merge environment variables into configuration"""
        # Network capture
        if os.getenv('CAPTURE_INTERFACE'):
            self.config['capture']['interface'] = os.getenv('CAPTURE_INTERFACE')
        
        # InfluxDB
        self.influxdb_url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        self.influxdb_token = os.getenv('INFLUXDB_TOKEN', '')
        self.influxdb_org = os.getenv('INFLUXDB_ORG', 'argus')
        self.influxdb_bucket = os.getenv('INFLUXDB_BUCKET', 'network_traffic')
        
        # Model paths
        self.model_path = os.getenv('MODEL_PATH', 'data/models/autoencoder.h5')
        self.tflite_model_path = os.getenv('TFLITE_MODEL_PATH', 'data/models/autoencoder.tflite')
        self.model_threshold = float(os.getenv('MODEL_THRESHOLD', '0.1'))
        
        # Trust scores
        self.trust_score_critical = int(os.getenv('TRUST_SCORE_CRITICAL_THRESHOLD', '20'))
        self.trust_score_warning = int(os.getenv('TRUST_SCORE_WARNING_THRESHOLD', '50'))
        
        # IPS
        self.ips_enabled = os.getenv('IPS_ENABLED', 'false').lower() == 'true'
        self.auto_block_enabled = os.getenv('AUTO_BLOCK_ENABLED', 'false').lower() == 'true'
        
        # API
        self.api_host = os.getenv('API_HOST', '0.0.0.0')
        self.api_port = int(os.getenv('API_PORT', '8000'))
        
        # Dashboard
        self.dashboard_host = os.getenv('DASHBOARD_HOST', '0.0.0.0')
        self.dashboard_port = int(os.getenv('DASHBOARD_PORT', '8050'))
        self.dashboard_debug = os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true'
    
    def update_interface(self, interface: str):
        """Update capture interface dynamically
        
        Args:
            interface: New interface name
        """
        self.config['capture']['interface'] = interface
        logger.info(f"Updated capture interface to: {interface}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'capture.interface')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

# Global configuration instance
config = Config()
