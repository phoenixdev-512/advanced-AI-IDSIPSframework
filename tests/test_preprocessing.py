"""
Tests for feature preprocessing
"""

import pytest
import numpy as np
from src.models.feature_preprocessing import FeaturePreprocessor


class TestFeaturePreprocessor:
    """Test feature preprocessing functionality"""
    
    def test_extract_features(self):
        """Test feature extraction from flows"""
        preprocessor = FeaturePreprocessor()
        
        flows = [
            {
                'src_ip': '192.168.1.100',
                'dst_ip': '10.0.0.1',
                'src_port': 12345,
                'dst_port': 80,
                'protocol': 'TCP',
                'flow_duration': 10.5,
                'total_fwd_packets': 50,
                'total_bwd_packets': 40,
                'total_fwd_bytes': 5000,
                'total_bwd_bytes': 4000,
                'total_packets': 90,
                'total_bytes': 9000,
                'packet_inter_arrival_time': 0.1
            }
        ]
        
        df = preprocessor.extract_features(flows)
        
        assert not df.empty
        assert 'src_port' in df.columns
        assert 'protocol_tcp' in df.columns
        assert len(df) == 1
    
    def test_fit_transform(self):
        """Test fit and transform"""
        preprocessor = FeaturePreprocessor()
        
        flows = [
            {
                'src_port': 12345,
                'dst_port': 80,
                'protocol': 'TCP',
                'flow_duration': 10.5,
                'total_fwd_packets': 50,
                'total_bwd_packets': 40,
                'total_fwd_bytes': 5000,
                'total_bwd_bytes': 4000,
                'total_packets': 90,
                'total_bytes': 9000,
                'packet_inter_arrival_time': 0.1
            }
        ]
        
        X = preprocessor.fit_transform(flows)
        
        assert X.shape[0] == 1
        assert X.shape[1] > 0
        assert preprocessor.is_fitted
    
    def test_transform_without_fit(self):
        """Test that transform fails without fit"""
        preprocessor = FeaturePreprocessor()
        
        flows = [{'src_port': 123}]
        
        with pytest.raises(ValueError):
            preprocessor.transform(flows)
    
    def test_save_load(self, tmp_path):
        """Test save and load functionality"""
        preprocessor = FeaturePreprocessor()
        
        flows = [
            {
                'src_port': 12345,
                'dst_port': 80,
                'protocol': 'TCP',
                'flow_duration': 10.5,
                'total_fwd_packets': 50,
                'total_bwd_packets': 40,
                'total_fwd_bytes': 5000,
                'total_bwd_bytes': 4000,
                'total_packets': 90,
                'total_bytes': 9000,
                'packet_inter_arrival_time': 0.1
            }
        ]
        
        X = preprocessor.fit_transform(flows)
        
        # Save
        save_path = tmp_path / "preprocessor.pkl"
        preprocessor.save(str(save_path))
        
        # Load
        new_preprocessor = FeaturePreprocessor()
        new_preprocessor.load(str(save_path))
        
        assert new_preprocessor.is_fitted
        assert new_preprocessor.feature_names == preprocessor.feature_names
        
        # Transform with loaded preprocessor
        X_new = new_preprocessor.transform(flows)
        np.testing.assert_array_almost_equal(X, X_new)
