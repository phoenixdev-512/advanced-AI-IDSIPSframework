"""
Network utility functions for Project Argus
"""

import logging
import psutil
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def get_network_interfaces() -> List[Dict[str, Any]]:
    """Get list of available network interfaces with their details
    
    Returns:
        List of dictionaries containing interface information:
        - name: Interface name (e.g., 'eth0', 'wlan0')
        - addresses: List of IP addresses assigned to the interface
        - is_up: Whether the interface is up
        - is_running: Whether the interface is running
    """
    interfaces = []
    
    try:
        # Get network interface stats
        net_if_stats = psutil.net_if_stats()
        net_if_addrs = psutil.net_if_addrs()
        
        for interface_name, stats in net_if_stats.items():
            # Skip loopback interface
            if interface_name == 'lo':
                continue
            
            addresses = []
            if interface_name in net_if_addrs:
                for addr in net_if_addrs[interface_name]:
                    # Only include IPv4 addresses
                    if addr.family == 2:  # AF_INET (IPv4)
                        addresses.append(addr.address)
            
            interfaces.append({
                'name': interface_name,
                'addresses': addresses,
                'is_up': stats.isup,
                'is_running': stats.isup,
                'display_name': f"{interface_name} ({addresses[0]})" if addresses else interface_name
            })
        
        # Add simulated traffic option
        interfaces.append({
            'name': 'simulated',
            'addresses': [],
            'is_up': True,
            'is_running': True,
            'display_name': 'Simulated Traffic (Demo Mode)'
        })
        
        logger.info(f"Found {len(interfaces)} network interfaces")
        return interfaces
        
    except Exception as e:
        logger.error(f"Error getting network interfaces: {e}")
        # Return at least the simulated option
        return [{
            'name': 'simulated',
            'addresses': [],
            'is_up': True,
            'is_running': True,
            'display_name': 'Simulated Traffic (Demo Mode)'
        }]
