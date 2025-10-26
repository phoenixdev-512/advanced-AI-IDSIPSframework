"""
Device trust scoring system
"""

import logging
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DeviceScore:
    """Represents a device's trust score and components"""
    device_ip: str
    trust_score: float = 100.0
    behavioral_score: float = 100.0
    vulnerability_score: float = 100.0
    reputation_score: float = 100.0
    last_updated: float = field(default_factory=time.time)
    anomaly_count: int = 0
    vulnerable_ports: List[int] = field(default_factory=list)
    is_whitelisted: bool = False
    is_blacklisted: bool = False
    
    def update_timestamp(self):
        """Update last_updated timestamp"""
        self.last_updated = time.time()


class TrustScoreManager:
    """Manages device trust scores"""
    
    def __init__(self, 
                 behavioral_weight: float = 0.5,
                 vulnerability_weight: float = 0.3,
                 reputation_weight: float = 0.2,
                 decay_rate: float = 0.95):
        """Initialize trust score manager
        
        Args:
            behavioral_weight: Weight for behavioral score component
            vulnerability_weight: Weight for vulnerability score component
            reputation_weight: Weight for reputation score component
            decay_rate: Score recovery rate per hour (0-1)
        """
        self.behavioral_weight = behavioral_weight
        self.vulnerability_weight = vulnerability_weight
        self.reputation_weight = reputation_weight
        self.decay_rate = decay_rate
        
        self.devices: Dict[str, DeviceScore] = {}
        
        # Normalize weights
        total = behavioral_weight + vulnerability_weight + reputation_weight
        self.behavioral_weight /= total
        self.vulnerability_weight /= total
        self.reputation_weight /= total
        
        logger.info(f"TrustScoreManager initialized with weights: "
                   f"behavioral={self.behavioral_weight:.2f}, "
                   f"vulnerability={self.vulnerability_weight:.2f}, "
                   f"reputation={self.reputation_weight:.2f}")
    
    def get_or_create_device(self, device_ip: str) -> DeviceScore:
        """Get existing device or create new one
        
        Args:
            device_ip: Device IP address
            
        Returns:
            DeviceScore object
        """
        if device_ip not in self.devices:
            self.devices[device_ip] = DeviceScore(device_ip=device_ip)
            logger.info(f"New device registered: {device_ip}")
        
        return self.devices[device_ip]
    
    def update_behavioral_score(self, device_ip: str, anomaly_score: float):
        """Update device behavioral score based on anomaly detection
        
        Args:
            device_ip: Device IP address
            anomaly_score: Anomaly score from ML model (higher = more anomalous)
        """
        device = self.get_or_create_device(device_ip)
        
        # Convert anomaly score to behavioral score (inverse relationship)
        # High anomaly score -> low behavioral score
        score_penalty = min(anomaly_score * 100, 50)  # Cap penalty at 50 points
        
        device.behavioral_score = max(0, device.behavioral_score - score_penalty)
        device.anomaly_count += 1
        
        self._update_overall_score(device)
        
        logger.info(f"Device {device_ip} behavioral score updated: "
                   f"{device.behavioral_score:.2f} (anomaly_score={anomaly_score:.4f})")
    
    def update_vulnerability_score(self, device_ip: str, vulnerable_ports: List[int]):
        """Update device vulnerability score based on port scan
        
        Args:
            device_ip: Device IP address
            vulnerable_ports: List of vulnerable/dangerous open ports
        """
        device = self.get_or_create_device(device_ip)
        device.vulnerable_ports = vulnerable_ports
        
        # Calculate vulnerability score
        # Each vulnerable port reduces score
        penalty_per_port = 15
        total_penalty = min(len(vulnerable_ports) * penalty_per_port, 80)
        
        device.vulnerability_score = max(20, 100 - total_penalty)
        
        self._update_overall_score(device)
        
        logger.info(f"Device {device_ip} vulnerability score updated: "
                   f"{device.vulnerability_score:.2f} "
                   f"({len(vulnerable_ports)} vulnerable ports)")
    
    def update_reputation_score(self, device_ip: str, is_malicious: bool):
        """Update device reputation score based on threat intelligence
        
        Args:
            device_ip: Device IP address
            is_malicious: Whether device contacted known malicious IPs
        """
        device = self.get_or_create_device(device_ip)
        
        if is_malicious:
            device.reputation_score = max(0, device.reputation_score - 50)
            logger.warning(f"Device {device_ip} contacted malicious IP. "
                          f"Reputation score: {device.reputation_score:.2f}")
        else:
            # Gradually improve reputation if no malicious activity
            device.reputation_score = min(100, device.reputation_score + 5)
        
        self._update_overall_score(device)
    
    def _update_overall_score(self, device: DeviceScore):
        """Calculate overall trust score from components
        
        Args:
            device: DeviceScore object
        """
        device.trust_score = (
            self.behavioral_weight * device.behavioral_score +
            self.vulnerability_weight * device.vulnerability_score +
            self.reputation_weight * device.reputation_score
        )
        
        device.update_timestamp()
        
        logger.debug(f"Device {device.device_ip} overall trust score: "
                    f"{device.trust_score:.2f}")
    
    def apply_score_decay(self, hours_elapsed: float = 1.0):
        """Apply time-based score recovery (decay)
        
        Args:
            hours_elapsed: Hours since last decay application
        """
        decay_factor = self.decay_rate ** hours_elapsed
        
        for device in self.devices.values():
            # Allow behavioral score to recover over time
            if device.behavioral_score < 100:
                recovery = (100 - device.behavioral_score) * (1 - decay_factor)
                device.behavioral_score = min(100, device.behavioral_score + recovery)
            
            # Allow reputation score to recover over time
            if device.reputation_score < 100:
                recovery = (100 - device.reputation_score) * (1 - decay_factor)
                device.reputation_score = min(100, device.reputation_score + recovery)
            
            self._update_overall_score(device)
        
        logger.debug(f"Applied score decay with factor {decay_factor:.4f}")
    
    def whitelist_device(self, device_ip: str):
        """Add device to whitelist
        
        Args:
            device_ip: Device IP address
        """
        device = self.get_or_create_device(device_ip)
        device.is_whitelisted = True
        device.is_blacklisted = False
        
        # Set all scores to max
        device.behavioral_score = 100.0
        device.vulnerability_score = 100.0
        device.reputation_score = 100.0
        self._update_overall_score(device)
        
        logger.info(f"Device {device_ip} whitelisted")
    
    def blacklist_device(self, device_ip: str):
        """Add device to blacklist
        
        Args:
            device_ip: Device IP address
        """
        device = self.get_or_create_device(device_ip)
        device.is_blacklisted = True
        device.is_whitelisted = False
        
        # Set all scores to minimum
        device.behavioral_score = 0.0
        device.vulnerability_score = 0.0
        device.reputation_score = 0.0
        self._update_overall_score(device)
        
        logger.info(f"Device {device_ip} blacklisted")
    
    def get_device_score(self, device_ip: str) -> Optional[DeviceScore]:
        """Get device score
        
        Args:
            device_ip: Device IP address
            
        Returns:
            DeviceScore object or None
        """
        return self.devices.get(device_ip)
    
    def get_all_devices(self) -> List[DeviceScore]:
        """Get all device scores
        
        Returns:
            List of DeviceScore objects
        """
        return list(self.devices.values())
    
    def get_low_trust_devices(self, threshold: float = 50.0) -> List[DeviceScore]:
        """Get devices with trust score below threshold
        
        Args:
            threshold: Trust score threshold
            
        Returns:
            List of DeviceScore objects
        """
        return [
            device for device in self.devices.values()
            if device.trust_score < threshold and not device.is_whitelisted
        ]
    
    def to_dict(self) -> Dict[str, dict]:
        """Convert all device scores to dictionary
        
        Returns:
            Dictionary of device scores
        """
        return {
            ip: {
                'device_ip': score.device_ip,
                'trust_score': score.trust_score,
                'behavioral_score': score.behavioral_score,
                'vulnerability_score': score.vulnerability_score,
                'reputation_score': score.reputation_score,
                'last_updated': datetime.fromtimestamp(score.last_updated).isoformat(),
                'anomaly_count': score.anomaly_count,
                'vulnerable_ports': score.vulnerable_ports,
                'is_whitelisted': score.is_whitelisted,
                'is_blacklisted': score.is_blacklisted
            }
            for ip, score in self.devices.items()
        }
