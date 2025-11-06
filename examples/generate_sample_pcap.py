#!/usr/bin/env python3
"""
Generate a small sample PCAP file for demo purposes.
This creates realistic network traffic including normal HTTP/HTTPS and some anomalous patterns.
"""

from scapy.all import IP, TCP, UDP, DNS, DNSQR, wrpcap, Ether
from scapy.layers.http import HTTP, HTTPRequest
import random

def generate_sample_pcap(output_file='examples/demo_data/sample_traffic.pcap'):
    """Generate a small PCAP file with realistic network traffic"""
    
    packets = []
    
    # Source devices (home network)
    devices = [
        '192.168.1.100',  # Laptop
        '192.168.1.101',  # Smart TV
        '192.168.1.102',  # IoT Camera
        '192.168.1.103',  # Smartphone
    ]
    
    # Normal traffic patterns
    print("Generating normal traffic patterns...")
    
    # 1. Normal web browsing (HTTP/HTTPS)
    for i in range(10):
        src_ip = random.choice(devices)
        dst_ip = '8.8.8.8'
        src_port = random.randint(49152, 65535)
        
        # DNS query
        dns_pkt = (
            Ether() / 
            IP(src=src_ip, dst=dst_ip) / 
            UDP(sport=src_port, dport=53) / 
            DNS(rd=1, qd=DNSQR(qname='example.com'))
        )
        packets.append(dns_pkt)
        
        # HTTPS connection (SYN)
        https_syn = (
            Ether() /
            IP(src=src_ip, dst='93.184.216.34') / 
            TCP(sport=src_port, dport=443, flags='S')
        )
        packets.append(https_syn)
        
        # HTTPS connection (SYN-ACK)
        https_synack = (
            Ether() /
            IP(src='93.184.216.34', dst=src_ip) / 
            TCP(sport=443, dport=src_port, flags='SA')
        )
        packets.append(https_synack)
        
        # HTTPS connection (ACK)
        https_ack = (
            Ether() /
            IP(src=src_ip, dst='93.184.216.34') / 
            TCP(sport=src_port, dport=443, flags='A')
        )
        packets.append(https_ack)
    
    # 2. Local network communication
    for i in range(5):
        src = devices[0]
        dst = devices[1]
        src_port = random.randint(49152, 65535)
        
        pkt = (
            Ether() /
            IP(src=src, dst=dst) / 
            TCP(sport=src_port, dport=8080, flags='PA')
        )
        packets.append(pkt)
    
    # 3. Anomalous patterns (port scanning from compromised device)
    print("Generating anomalous traffic patterns...")
    
    compromised_device = '192.168.1.102'  # IoT Camera
    target = '192.168.1.1'  # Router
    
    # Simulate port scan
    for port in [21, 22, 23, 25, 80, 443, 3389, 8080]:
        scan_pkt = (
            Ether() /
            IP(src=compromised_device, dst=target) / 
            TCP(sport=random.randint(49152, 65535), dport=port, flags='S')
        )
        packets.append(scan_pkt)
        
        # RST response (port closed)
        rst_pkt = (
            Ether() /
            IP(src=target, dst=compromised_device) / 
            TCP(sport=port, dport=scan_pkt[TCP].sport, flags='R')
        )
        packets.append(rst_pkt)
    
    # 4. Unusual outbound connections (data exfiltration attempt)
    for i in range(3):
        suspicious_pkt = (
            Ether() /
            IP(src=compromised_device, dst='45.33.32.156') /  # Unknown external IP
            TCP(sport=random.randint(49152, 65535), dport=4444, flags='PA')
        )
        packets.append(suspicious_pkt)
    
    # Write packets to file
    print(f"Writing {len(packets)} packets to {output_file}...")
    wrpcap(output_file, packets)
    print(f"Sample PCAP created successfully: {output_file}")
    print(f"File contains {len(packets)} packets including:")
    print("  - Normal web traffic (DNS, HTTPS)")
    print("  - Local network communication")
    print("  - Anomalous port scanning activity")
    print("  - Suspicious outbound connections")
    
    return output_file

if __name__ == '__main__':
    generate_sample_pcap()
