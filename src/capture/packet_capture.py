"""
Network packet capture and flow extraction module
"""

import time
import logging
from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from scapy.all import sniff, IP, TCP, UDP, ICMP, Raw
from scapy.layers.inet import TCP, UDP
import threading

logger = logging.getLogger(__name__)


class NetworkFlow:
    """Represents a network flow between two endpoints"""
    
    def __init__(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        
        self.start_time = time.time()
        self.last_packet_time = self.start_time
        
        self.fwd_packets = 0
        self.bwd_packets = 0
        self.fwd_bytes = 0
        self.bwd_bytes = 0
        
        self.packet_times = []
        
    def update(self, packet_size: int, is_forward: bool, timestamp: float):
        """Update flow with new packet information"""
        if is_forward:
            self.fwd_packets += 1
            self.fwd_bytes += packet_size
        else:
            self.bwd_packets += 1
            self.bwd_bytes += packet_size
        
        self.packet_times.append(timestamp)
        self.last_packet_time = timestamp
    
    @property
    def duration(self) -> float:
        """Get flow duration in seconds"""
        return self.last_packet_time - self.start_time
    
    @property
    def total_packets(self) -> int:
        """Get total number of packets"""
        return self.fwd_packets + self.bwd_packets
    
    @property
    def total_bytes(self) -> int:
        """Get total number of bytes"""
        return self.fwd_bytes + self.bwd_bytes
    
    @property
    def avg_inter_arrival_time(self) -> float:
        """Calculate average packet inter-arrival time"""
        if len(self.packet_times) < 2:
            return 0.0
        
        intervals = [self.packet_times[i+1] - self.packet_times[i] 
                    for i in range(len(self.packet_times) - 1)]
        return sum(intervals) / len(intervals) if intervals else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert flow to dictionary for storage/processing"""
        return {
            'src_ip': self.src_ip,
            'dst_ip': self.dst_ip,
            'src_port': self.src_port,
            'dst_port': self.dst_port,
            'protocol': self.protocol,
            'flow_duration': self.duration,
            'total_fwd_packets': self.fwd_packets,
            'total_bwd_packets': self.bwd_packets,
            'total_fwd_bytes': self.fwd_bytes,
            'total_bwd_bytes': self.bwd_bytes,
            'total_packets': self.total_packets,
            'total_bytes': self.total_bytes,
            'packet_inter_arrival_time': self.avg_inter_arrival_time,
            'timestamp': datetime.fromtimestamp(self.start_time).isoformat()
        }


class PacketCapture:
    """Captures and processes network packets into flows"""
    
    def __init__(self, interface: str = "eth0", flow_timeout: int = 120):
        """Initialize packet capture
        
        Args:
            interface: Network interface to capture from
            flow_timeout: Timeout in seconds for flow expiration
        """
        self.interface = interface
        self.flow_timeout = flow_timeout
        self.flows: Dict[str, NetworkFlow] = {}
        self.completed_flows: List[Dict[str, Any]] = []
        self.running = False
        self.lock = threading.Lock()
        
        logger.info(f"PacketCapture initialized on interface {interface}")
    
    def _get_flow_key(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str) -> str:
        """Generate unique flow key"""
        # Ensure bidirectional flows use same key
        if src_ip < dst_ip:
            return f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-{protocol}"
        else:
            return f"{dst_ip}:{dst_port}-{src_ip}:{src_port}-{protocol}"
    
    def _is_forward_direction(self, flow: NetworkFlow, src_ip: str, src_port: int) -> bool:
        """Determine if packet is in forward direction"""
        return flow.src_ip == src_ip and flow.src_port == src_port
    
    def _process_packet(self, packet):
        """Process individual packet"""
        try:
            if not packet.haslayer(IP):
                return
            
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            protocol = "OTHER"
            src_port = 0
            dst_port = 0
            packet_size = len(packet)
            
            # Extract transport layer information
            if packet.haslayer(TCP):
                protocol = "TCP"
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
            elif packet.haslayer(UDP):
                protocol = "UDP"
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
            elif packet.haslayer(ICMP):
                protocol = "ICMP"
            
            # Get or create flow
            flow_key = self._get_flow_key(src_ip, dst_ip, src_port, dst_port, protocol)
            current_time = time.time()
            
            with self.lock:
                if flow_key not in self.flows:
                    # Create new flow
                    self.flows[flow_key] = NetworkFlow(src_ip, dst_ip, src_port, dst_port, protocol)
                
                flow = self.flows[flow_key]
                is_forward = self._is_forward_direction(flow, src_ip, src_port)
                flow.update(packet_size, is_forward, current_time)
                
        except Exception as e:
            logger.error(f"Error processing packet: {e}")
    
    def _cleanup_expired_flows(self):
        """Move expired flows to completed flows list"""
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for flow_key, flow in self.flows.items():
                if current_time - flow.last_packet_time > self.flow_timeout:
                    self.completed_flows.append(flow.to_dict())
                    expired_keys.append(flow_key)
            
            # Remove expired flows
            for key in expired_keys:
                del self.flows[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired flows")
    
    def start_capture(self, packet_count: int = 0, timeout: Optional[int] = None):
        """Start capturing packets
        
        Args:
            packet_count: Number of packets to capture (0 for continuous)
            timeout: Capture timeout in seconds (None for no timeout)
        """
        logger.info(f"Starting packet capture on {self.interface}")
        self.running = True
        
        try:
            # Start cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_thread)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
            # Start sniffing
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                count=packet_count,
                timeout=timeout,
                store=False
            )
        except PermissionError:
            logger.error("Permission denied. Packet capture requires root/admin privileges.")
            raise
        except Exception as e:
            logger.error(f"Error during packet capture: {e}")
            raise
        finally:
            self.running = False
    
    def _cleanup_thread(self):
        """Background thread for cleaning up expired flows"""
        while self.running:
            time.sleep(10)  # Check every 10 seconds
            self._cleanup_expired_flows()
    
    def get_completed_flows(self, clear: bool = True) -> List[Dict[str, Any]]:
        """Get completed flows
        
        Args:
            clear: Whether to clear the completed flows list after retrieval
            
        Returns:
            List of completed flow dictionaries
        """
        with self.lock:
            flows = self.completed_flows.copy()
            if clear:
                self.completed_flows.clear()
        
        return flows
    
    def stop(self):
        """Stop packet capture"""
        logger.info("Stopping packet capture")
        self.running = False
        
        # Move all remaining flows to completed
        with self.lock:
            for flow in self.flows.values():
                self.completed_flows.append(flow.to_dict())
            self.flows.clear()
