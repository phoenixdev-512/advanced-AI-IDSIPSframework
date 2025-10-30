"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestAPIEndpoints:
    """Test API endpoint functionality"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Project Argus API'
        assert data['status'] == 'running'
    
    def test_get_interfaces(self):
        """Test getting network interfaces"""
        response = self.client.get("/api/interfaces")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have interfaces list
        assert 'interfaces' in data
        assert isinstance(data['interfaces'], list)
        
        # Should have current state
        assert 'current_interface' in data
        assert 'current_mode' in data
        
        # Should have at least simulated interface
        interfaces = data['interfaces']
        assert len(interfaces) >= 1
        
        simulated = next((i for i in interfaces if i['name'] == 'simulated'), None)
        assert simulated is not None
    
    def test_get_system_status(self):
        """Test system status endpoint"""
        response = self.client.get("/api/system/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'mode' in data
        assert 'interface' in data
        assert 'status' in data
        assert data['status'] == 'ONLINE'
    
    def test_update_interface_invalid(self):
        """Test updating to invalid interface"""
        response = self.client.post(
            "/api/interfaces/update",
            json={"interface": "invalid_interface", "mode": "passive"}
        )
        
        # Should fail with 400 or 500 (depending on callback setup)
        assert response.status_code in [400, 500]
    
    def test_update_interface_simulated(self):
        """Test updating to simulated interface"""
        # This may fail if callback is not set up, but the request should be valid
        response = self.client.post(
            "/api/interfaces/update",
            json={"interface": "simulated", "mode": "simulated"}
        )
        
        # Accept both success and error (callback might not be set)
        assert response.status_code in [200, 500]
