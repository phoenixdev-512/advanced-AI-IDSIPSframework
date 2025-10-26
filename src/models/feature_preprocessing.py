"""
Feature preprocessing and extraction for ML models
"""

import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle

logger = logging.getLogger(__name__)


class FeaturePreprocessor:
    """Preprocesses network flow features for ML models"""
    
    def __init__(self):
        """Initialize feature preprocessor"""
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_fitted = False
        
        logger.info("FeaturePreprocessor initialized")
    
    def extract_features(self, flows: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract features from flow data
        
        Args:
            flows: List of flow dictionaries
            
        Returns:
            DataFrame with extracted features
        """
        if not flows:
            return pd.DataFrame()
        
        df = pd.DataFrame(flows)
        
        # Select relevant features
        feature_cols = [
            'src_port', 'dst_port', 'flow_duration',
            'total_fwd_packets', 'total_bwd_packets',
            'total_fwd_bytes', 'total_bwd_bytes',
            'total_packets', 'total_bytes',
            'packet_inter_arrival_time'
        ]
        
        # Add protocol encoding
        if 'protocol' in df.columns:
            df['protocol_tcp'] = (df['protocol'] == 'TCP').astype(int)
            df['protocol_udp'] = (df['protocol'] == 'UDP').astype(int)
            df['protocol_icmp'] = (df['protocol'] == 'ICMP').astype(int)
            feature_cols.extend(['protocol_tcp', 'protocol_udp', 'protocol_icmp'])
        
        # Calculate derived features
        if 'total_fwd_packets' in df.columns and 'total_bwd_packets' in df.columns:
            df['packet_ratio'] = df['total_fwd_packets'] / (df['total_bwd_packets'] + 1)
            feature_cols.append('packet_ratio')
        
        if 'total_fwd_bytes' in df.columns and 'total_bwd_bytes' in df.columns:
            df['byte_ratio'] = df['total_fwd_bytes'] / (df['total_bwd_bytes'] + 1)
            feature_cols.append('byte_ratio')
        
        if 'total_bytes' in df.columns and 'flow_duration' in df.columns:
            df['bytes_per_second'] = df['total_bytes'] / (df['flow_duration'] + 0.001)
            feature_cols.append('bytes_per_second')
        
        if 'total_packets' in df.columns and 'flow_duration' in df.columns:
            df['packets_per_second'] = df['total_packets'] / (df['flow_duration'] + 0.001)
            feature_cols.append('packets_per_second')
        
        # Handle missing values
        df = df.fillna(0)
        
        # Select only feature columns that exist
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_names = available_cols
        
        return df[available_cols]
    
    def fit_transform(self, flows: List[Dict[str, Any]]) -> np.ndarray:
        """Fit preprocessor and transform flows
        
        Args:
            flows: List of flow dictionaries
            
        Returns:
            Normalized feature array
        """
        df = self.extract_features(flows)
        
        if df.empty:
            return np.array([])
        
        # Fit and transform
        X = self.scaler.fit_transform(df.values)
        self.is_fitted = True
        
        logger.info(f"Preprocessor fitted with {len(self.feature_names)} features")
        return X
    
    def transform(self, flows: List[Dict[str, Any]]) -> np.ndarray:
        """Transform flows using fitted preprocessor
        
        Args:
            flows: List of flow dictionaries
            
        Returns:
            Normalized feature array
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit_transform first.")
        
        df = self.extract_features(flows)
        
        if df.empty:
            return np.array([])
        
        # Ensure same features as training
        if len(df.columns) != len(self.feature_names):
            logger.warning(f"Feature mismatch: expected {len(self.feature_names)}, "
                          f"got {len(df.columns)}")
        
        X = self.scaler.transform(df.values)
        return X
    
    def save(self, filepath: str):
        """Save preprocessor to file
        
        Args:
            filepath: Path to save preprocessor
        """
        preprocessor_data = {
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'is_fitted': self.is_fitted
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(preprocessor_data, f)
        
        logger.info(f"Preprocessor saved to {filepath}")
    
    def load(self, filepath: str):
        """Load preprocessor from file
        
        Args:
            filepath: Path to saved preprocessor
        """
        with open(filepath, 'rb') as f:
            preprocessor_data = pickle.load(f)
        
        self.scaler = preprocessor_data['scaler']
        self.label_encoders = preprocessor_data['label_encoders']
        self.feature_names = preprocessor_data['feature_names']
        self.is_fitted = preprocessor_data['is_fitted']
        
        logger.info(f"Preprocessor loaded from {filepath}")
    
    def get_feature_importance(self, feature_values: np.ndarray) -> Dict[str, float]:
        """Get feature importance based on variance
        
        Args:
            feature_values: Array of feature values
            
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_fitted:
            return {}
        
        variances = np.var(feature_values, axis=0)
        importance = {
            name: float(var) 
            for name, var in zip(self.feature_names, variances)
        }
        
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
