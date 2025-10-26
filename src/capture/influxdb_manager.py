"""
InfluxDB integration for time-series storage
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class InfluxDBManager:
    """Manages InfluxDB connections and operations"""
    
    def __init__(self, url: str, token: str, org: str, bucket: str):
        """Initialize InfluxDB manager
        
        Args:
            url: InfluxDB URL
            token: Authentication token
            org: Organization name
            bucket: Bucket name for storing data
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        
        try:
            self.client = InfluxDBClient(url=url, token=token, org=org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            logger.info(f"Connected to InfluxDB at {url}")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            self.client = None
            self.write_api = None
            self.query_api = None
    
    def write_flow(self, flow_data: Dict[str, Any]):
        """Write network flow data to InfluxDB
        
        Args:
            flow_data: Flow data dictionary
        """
        if not self.write_api:
            logger.warning("InfluxDB not connected, skipping write")
            return
        
        try:
            point = Point("network_flow") \
                .tag("src_ip", flow_data['src_ip']) \
                .tag("dst_ip", flow_data['dst_ip']) \
                .tag("protocol", flow_data['protocol']) \
                .field("src_port", flow_data['src_port']) \
                .field("dst_port", flow_data['dst_port']) \
                .field("flow_duration", flow_data['flow_duration']) \
                .field("total_fwd_packets", flow_data['total_fwd_packets']) \
                .field("total_bwd_packets", flow_data['total_bwd_packets']) \
                .field("total_fwd_bytes", flow_data['total_fwd_bytes']) \
                .field("total_bwd_bytes", flow_data['total_bwd_bytes']) \
                .field("total_packets", flow_data['total_packets']) \
                .field("total_bytes", flow_data['total_bytes']) \
                .field("packet_inter_arrival_time", flow_data['packet_inter_arrival_time'])
            
            self.write_api.write(bucket=self.bucket, record=point)
            
        except Exception as e:
            logger.error(f"Error writing flow to InfluxDB: {e}")
    
    def write_flows(self, flows: List[Dict[str, Any]]):
        """Write multiple network flows to InfluxDB
        
        Args:
            flows: List of flow data dictionaries
        """
        for flow in flows:
            self.write_flow(flow)
    
    def write_device_score(self, device_ip: str, score: float, 
                          behavioral_score: float = 0.0,
                          vulnerability_score: float = 0.0,
                          reputation_score: float = 0.0):
        """Write device trust score to InfluxDB
        
        Args:
            device_ip: Device IP address
            score: Overall trust score
            behavioral_score: Behavioral component
            vulnerability_score: Vulnerability component
            reputation_score: Reputation component
        """
        if not self.write_api:
            logger.warning("InfluxDB not connected, skipping write")
            return
        
        try:
            point = Point("device_trust_score") \
                .tag("device_ip", device_ip) \
                .field("trust_score", score) \
                .field("behavioral_score", behavioral_score) \
                .field("vulnerability_score", vulnerability_score) \
                .field("reputation_score", reputation_score)
            
            self.write_api.write(bucket=self.bucket, record=point)
            
        except Exception as e:
            logger.error(f"Error writing device score to InfluxDB: {e}")
    
    def write_anomaly(self, device_ip: str, anomaly_score: float, 
                     flow_data: Optional[Dict[str, Any]] = None):
        """Write anomaly detection event to InfluxDB
        
        Args:
            device_ip: Device IP address
            anomaly_score: Anomaly score from model
            flow_data: Optional flow data associated with anomaly
        """
        if not self.write_api:
            logger.warning("InfluxDB not connected, skipping write")
            return
        
        try:
            point = Point("anomaly_event") \
                .tag("device_ip", device_ip) \
                .field("anomaly_score", anomaly_score)
            
            if flow_data:
                point = point.tag("protocol", flow_data.get('protocol', 'UNKNOWN'))
                point = point.field("total_bytes", flow_data.get('total_bytes', 0))
            
            self.write_api.write(bucket=self.bucket, record=point)
            
        except Exception as e:
            logger.error(f"Error writing anomaly to InfluxDB: {e}")
    
    def write_alert(self, device_ip: str, alert_type: str, severity: str, message: str):
        """Write security alert to InfluxDB
        
        Args:
            device_ip: Device IP address
            alert_type: Type of alert
            severity: Alert severity (low, medium, high, critical)
            message: Alert message
        """
        if not self.write_api:
            logger.warning("InfluxDB not connected, skipping write")
            return
        
        try:
            point = Point("security_alert") \
                .tag("device_ip", device_ip) \
                .tag("alert_type", alert_type) \
                .tag("severity", severity) \
                .field("message", message)
            
            self.write_api.write(bucket=self.bucket, record=point)
            
        except Exception as e:
            logger.error(f"Error writing alert to InfluxDB: {e}")
    
    def query_recent_flows(self, device_ip: Optional[str] = None, 
                          hours: int = 1) -> List[Dict[str, Any]]:
        """Query recent network flows
        
        Args:
            device_ip: Optional device IP to filter by
            hours: Number of hours to look back
            
        Returns:
            List of flow data dictionaries
        """
        if not self.query_api:
            logger.warning("InfluxDB not connected, cannot query")
            return []
        
        try:
            filter_clause = f'|> filter(fn: (r) => r["src_ip"] == "{device_ip}" or r["dst_ip"] == "{device_ip}")' \
                           if device_ip else ""
            
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r["_measurement"] == "network_flow")
                {filter_clause}
            '''
            
            result = self.query_api.query(query=query)
            flows = []
            
            for table in result:
                for record in table.records:
                    flows.append(record.values)
            
            return flows
            
        except Exception as e:
            logger.error(f"Error querying flows from InfluxDB: {e}")
            return []
    
    def close(self):
        """Close InfluxDB connection"""
        if self.client:
            self.client.close()
            logger.info("InfluxDB connection closed")
