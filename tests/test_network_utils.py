"""
Tests for network utilities and simulated traffic
"""

import pytest
from src.utils.network_utils import get_network_interfaces
from src.capture.simulated_capture import SimulatedTrafficGenerator


class TestNetworkUtils:
    """Test network utility functions"""
    
    def test_get_network_interfaces(self):
        """Test getting network interfaces"""
        interfaces = get_network_interfaces()
        
        # Should return a list
        assert isinstance(interfaces, list)
        
        # Should have at least the simulated option
        assert len(interfaces) >= 1
        
        # Check that simulated interface exists
        simulated = next((i for i in interfaces if i['name'] == 'simulated'), None)
        assert simulated is not None
        assert simulated['display_name'] == 'Simulated Traffic (Demo Mode)'
        
        # Each interface should have required fields
        for iface in interfaces:
            assert 'name' in iface
            assert 'addresses' in iface
            assert 'is_up' in iface
            assert 'display_name' in iface


class TestSimulatedTrafficGenerator:
    """Test simulated traffic generation"""
    
    def test_initialization(self):
        """Test generator initialization"""
        generator = SimulatedTrafficGenerator(anomaly_rate=0.1)
        
        assert generator.anomaly_rate == 0.1
        assert generator.running is False
        assert len(generator.completed_flows) == 0
    
    def test_generate_normal_flow(self):
        """Test normal flow generation"""
        generator = SimulatedTrafficGenerator()
        
        flow = generator._generate_normal_flow()
        
        # Check required fields
        assert 'src_ip' in flow
        assert 'dst_ip' in flow
        assert 'src_port' in flow
        assert 'dst_port' in flow
        assert 'protocol' in flow
        assert 'flow_duration' in flow
        assert 'total_fwd_packets' in flow
        assert 'total_bwd_packets' in flow
        assert 'timestamp' in flow
        
        # Check IP addresses are from expected ranges
        assert flow['src_ip'].startswith('192.168.1.')
        
        # Check port numbers are valid
        assert 0 < flow['src_port'] <= 65535
        assert 0 < flow['dst_port'] <= 65535
    
    def test_generate_anomalous_flow(self):
        """Test anomalous flow generation"""
        generator = SimulatedTrafficGenerator()
        
        flow = generator._generate_anomalous_flow()
        
        # Check required fields
        assert 'src_ip' in flow
        assert 'dst_ip' in flow
        assert 'protocol' in flow
        assert 'timestamp' in flow
        
        # Should have valid values
        assert flow['src_ip'].startswith('192.168.1.')
    
    def test_flow_retrieval(self):
        """Test getting completed flows"""
        generator = SimulatedTrafficGenerator()
        
        # Add some flows manually
        flow1 = generator._generate_normal_flow()
        flow2 = generator._generate_normal_flow()
        
        generator.completed_flows.append(flow1)
        generator.completed_flows.append(flow2)
        
        # Get flows
        flows = generator.get_completed_flows(clear=False)
        assert len(flows) == 2
        
        # Verify flows still there
        assert len(generator.completed_flows) == 2
        
        # Get flows with clear
        flows = generator.get_completed_flows(clear=True)
        assert len(flows) == 2
        assert len(generator.completed_flows) == 0
    
    def test_stop_generation(self):
        """Test stopping generation"""
        generator = SimulatedTrafficGenerator()
        
        generator.running = True
        generator.stop_generation()
        
        assert generator.running is False
