"""
Tests for trust score management
"""

import pytest
from src.scoring.trust_score import TrustScoreManager, DeviceScore


class TestTrustScoreManager:
    """Test trust score management functionality"""
    
    def test_create_device(self):
        """Test device creation"""
        manager = TrustScoreManager()
        
        device = manager.get_or_create_device("192.168.1.100")
        
        assert device.device_ip == "192.168.1.100"
        assert device.trust_score == 100.0
        assert device.behavioral_score == 100.0
        assert device.vulnerability_score == 100.0
        assert device.reputation_score == 100.0
    
    def test_update_behavioral_score(self):
        """Test behavioral score update"""
        manager = TrustScoreManager()
        
        # Create device with good score
        device = manager.get_or_create_device("192.168.1.100")
        initial_score = device.trust_score
        
        # Detect anomaly
        manager.update_behavioral_score("192.168.1.100", 0.5)
        
        device = manager.get_device_score("192.168.1.100")
        assert device.trust_score < initial_score
        assert device.anomaly_count == 1
    
    def test_update_vulnerability_score(self):
        """Test vulnerability score update"""
        manager = TrustScoreManager()
        
        device = manager.get_or_create_device("192.168.1.100")
        
        # Found vulnerable ports
        manager.update_vulnerability_score("192.168.1.100", [21, 23])
        
        device = manager.get_device_score("192.168.1.100")
        assert device.vulnerability_score < 100.0
        assert len(device.vulnerable_ports) == 2
    
    def test_whitelist_device(self):
        """Test device whitelisting"""
        manager = TrustScoreManager()
        
        # Create device with low score
        device = manager.get_or_create_device("192.168.1.100")
        manager.update_behavioral_score("192.168.1.100", 1.0)
        
        # Whitelist
        manager.whitelist_device("192.168.1.100")
        
        device = manager.get_device_score("192.168.1.100")
        assert device.is_whitelisted
        assert device.trust_score == 100.0
    
    def test_blacklist_device(self):
        """Test device blacklisting"""
        manager = TrustScoreManager()
        
        device = manager.get_or_create_device("192.168.1.100")
        
        # Blacklist
        manager.blacklist_device("192.168.1.100")
        
        device = manager.get_device_score("192.168.1.100")
        assert device.is_blacklisted
        assert device.trust_score == 0.0
    
    def test_get_low_trust_devices(self):
        """Test getting low trust devices"""
        manager = TrustScoreManager()
        
        # Create devices with different scores
        manager.get_or_create_device("192.168.1.100")
        manager.update_behavioral_score("192.168.1.100", 1.0)  # Low score
        
        manager.get_or_create_device("192.168.1.101")  # Normal score
        
        low_trust = manager.get_low_trust_devices(threshold=75.0)
        
        assert len(low_trust) == 1
        assert low_trust[0].device_ip == "192.168.1.100"
    
    def test_score_decay(self):
        """Test score decay/recovery"""
        manager = TrustScoreManager(decay_rate=0.5)
        
        # Create device and lower score
        device = manager.get_or_create_device("192.168.1.100")
        manager.update_behavioral_score("192.168.1.100", 1.0)
        
        initial_score = manager.get_device_score("192.168.1.100").trust_score
        
        # Apply decay (recovery)
        manager.apply_score_decay(hours_elapsed=1.0)
        
        final_score = manager.get_device_score("192.168.1.100").trust_score
        
        # Score should have recovered
        assert final_score > initial_score
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        manager = TrustScoreManager()
        
        manager.get_or_create_device("192.168.1.100")
        manager.get_or_create_device("192.168.1.101")
        
        devices_dict = manager.to_dict()
        
        assert len(devices_dict) == 2
        assert "192.168.1.100" in devices_dict
        assert "trust_score" in devices_dict["192.168.1.100"]
