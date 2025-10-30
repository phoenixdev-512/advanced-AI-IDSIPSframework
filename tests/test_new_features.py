"""
Tests for new Admin and Network Discovery features
"""

import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.main import app


class TestNetworkDiscovery:
    """Test network discovery endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_network_discover_endpoint(self):
        """Test network discovery endpoint"""
        response = self.client.post("/api/network/discover")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have required fields
        assert 'status' in data
        assert 'devices' in data
        assert 'count' in data
        assert data['status'] == 'success'
        
        # Devices should be a list
        assert isinstance(data['devices'], list)
        
        # Count should match length
        assert data['count'] == len(data['devices'])
        
        # Each device should have required fields
        if len(data['devices']) > 0:
            device = data['devices'][0]
            assert 'ip' in device
            assert 'mac' in device
            assert 'manufacturer' in device


class TestModelTraining:
    """Test model training endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        
        # Create test directories
        Path("model_training/data/raw").mkdir(parents=True, exist_ok=True)
        Path("model_training/trained_models").mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Cleanup test files"""
        # Clean up test files
        test_file = Path("model_training/data/raw/uploaded_dataset.tmp")
        if test_file.exists():
            test_file.unlink()
        
        history_file = Path("model_training/training_history.json")
        if history_file.exists():
            history_file.unlink()
    
    def test_upload_dataset(self):
        """Test dataset upload endpoint"""
        # Create a test file
        test_data = b"test,data,csv\n1,2,3\n"
        
        response = self.client.post(
            "/api/train/upload_dataset",
            files={"file": ("test.csv", test_data, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'filename' in data
        assert data['filename'] == 'test.csv'
        assert 'size' in data
        
        # File should exist
        uploaded_file = Path("model_training/data/raw/uploaded_dataset.tmp")
        assert uploaded_file.exists()
    
    def test_start_training(self):
        """Test starting model training"""
        config = {
            "model_type": "autoencoder",
            "epochs": 50,
            "batch_size": 32,
            "cross_validation": True,
            "hyperparameter_tuning": False,
            "generate_report": True
        }
        
        response = self.client.post("/api/train/start", json=config)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'message' in data
        assert 'Training started' in data['message']
    
    def test_get_training_history_empty(self):
        """Test getting training history when empty"""
        response = self.client.get("/api/train/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'history' in data
        assert isinstance(data['history'], list)
    
    def test_get_training_history_with_data(self):
        """Test getting training history with existing data"""
        # Create mock history
        history = [
            {
                "id": 1,
                "model_type": "autoencoder",
                "epochs": 50,
                "batch_size": 32,
                "f1_score": 0.85,
                "auc_score": 0.90,
                "status": "completed",
                "trained_at": "2024-01-15T14:30:00",
                "is_active": True
            }
        ]
        
        history_file = Path("model_training/training_history.json")
        with open(history_file, 'w') as f:
            json.dump(history, f)
        
        response = self.client.get("/api/train/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'history' in data
        assert len(data['history']) == 1
        assert data['history'][0]['model_type'] == 'autoencoder'
        assert data['history'][0]['is_active'] is True
    
    def test_activate_model(self):
        """Test activating a model"""
        # Create mock history with multiple models
        history = [
            {
                "id": 1,
                "model_type": "autoencoder",
                "is_active": True
            },
            {
                "id": 2,
                "model_type": "isolation_forest",
                "is_active": False
            }
        ]
        
        history_file = Path("model_training/training_history.json")
        with open(history_file, 'w') as f:
            json.dump(history, f)
        
        # Activate model 2
        response = self.client.post("/api/model/activate?model_id=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert data['model_id'] == 2
        
        # Verify in history file
        with open(history_file, 'r') as f:
            updated_history = json.load(f)
        
        # Model 1 should be inactive, Model 2 should be active
        assert updated_history[0]['is_active'] is False
        assert updated_history[1]['is_active'] is True
    
    def test_activate_nonexistent_model(self):
        """Test activating a model that doesn't exist"""
        # Create empty history
        history = []
        history_file = Path("model_training/training_history.json")
        with open(history_file, 'w') as f:
            json.dump(history, f)
        
        response = self.client.post("/api/model/activate?model_id=999")
        
        assert response.status_code == 404
