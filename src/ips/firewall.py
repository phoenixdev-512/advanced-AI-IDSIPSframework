"""
Intrusion Prevention System (IPS) using iptables
"""

import logging
import subprocess
from typing import List, Optional, Set
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class IPTablesManager:
    """Manages iptables rules for network filtering"""
    
    def __init__(self, enabled: bool = False):
        """Initialize iptables manager
        
        Args:
            enabled: Whether IPS is enabled
        """
        self.enabled = enabled
        self.blocked_ips: Set[str] = set()
        self.quarantined_ips: Set[str] = set()
        self.quarantine_times: dict = {}
        
        logger.info(f"IPTablesManager initialized (enabled={enabled})")
    
    def _run_iptables_command(self, command: List[str]) -> bool:
        """Run iptables command
        
        Args:
            command: Command arguments
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info(f"IPS disabled, would run: {' '.join(command)}")
            return False
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(f"iptables command successful: {' '.join(command)}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"iptables command failed: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("iptables not found. Ensure it is installed and in PATH.")
            return False
    
    def block_ip(self, ip_address: str, permanent: bool = False) -> bool:
        """Block an IP address
        
        Args:
            ip_address: IP address to block
            permanent: Whether block is permanent
            
        Returns:
            True if successful
        """
        if ip_address in self.blocked_ips:
            logger.info(f"IP {ip_address} already blocked")
            return True
        
        # Block incoming traffic from IP
        success_in = self._run_iptables_command([
            'sudo', 'iptables', '-A', 'INPUT',
            '-s', ip_address,
            '-j', 'DROP'
        ])
        
        # Block outgoing traffic to IP
        success_out = self._run_iptables_command([
            'sudo', 'iptables', '-A', 'OUTPUT',
            '-d', ip_address,
            '-j', 'DROP'
        ])
        
        if success_in and success_out:
            self.blocked_ips.add(ip_address)
            logger.warning(f"IP {ip_address} blocked {'permanently' if permanent else 'temporarily'}")
            return True
        
        return False
    
    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock an IP address
        
        Args:
            ip_address: IP address to unblock
            
        Returns:
            True if successful
        """
        if ip_address not in self.blocked_ips:
            logger.info(f"IP {ip_address} not currently blocked")
            return True
        
        # Remove block on incoming traffic
        success_in = self._run_iptables_command([
            'sudo', 'iptables', '-D', 'INPUT',
            '-s', ip_address,
            '-j', 'DROP'
        ])
        
        # Remove block on outgoing traffic
        success_out = self._run_iptables_command([
            'sudo', 'iptables', '-D', 'OUTPUT',
            '-d', ip_address,
            '-j', 'DROP'
        ])
        
        if success_in and success_out:
            self.blocked_ips.discard(ip_address)
            logger.info(f"IP {ip_address} unblocked")
            return True
        
        return False
    
    def quarantine_ip(self, ip_address: str, duration: int = 3600) -> bool:
        """Quarantine an IP address for a specific duration
        
        Args:
            ip_address: IP address to quarantine
            duration: Quarantine duration in seconds
            
        Returns:
            True if successful
        """
        success = self.block_ip(ip_address, permanent=False)
        
        if success:
            self.quarantined_ips.add(ip_address)
            self.quarantine_times[ip_address] = time.time() + duration
            logger.warning(f"IP {ip_address} quarantined for {duration} seconds")
        
        return success
    
    def check_quarantine_expiry(self):
        """Check and release expired quarantines"""
        current_time = time.time()
        expired_ips = []
        
        for ip_address, expiry_time in self.quarantine_times.items():
            if current_time >= expiry_time:
                expired_ips.append(ip_address)
        
        for ip_address in expired_ips:
            self.unblock_ip(ip_address)
            self.quarantined_ips.discard(ip_address)
            del self.quarantine_times[ip_address]
            logger.info(f"Quarantine expired for IP {ip_address}")
    
    def rate_limit_ip(self, ip_address: str, max_connections: int = 10) -> bool:
        """Apply rate limiting to an IP address
        
        Args:
            ip_address: IP address to rate limit
            max_connections: Maximum connections per minute
            
        Returns:
            True if successful
        """
        success = self._run_iptables_command([
            'sudo', 'iptables', '-A', 'INPUT',
            '-s', ip_address,
            '-m', 'connlimit',
            '--connlimit-above', str(max_connections),
            '-j', 'REJECT'
        ])
        
        if success:
            logger.info(f"Rate limiting applied to IP {ip_address} "
                       f"(max {max_connections} connections)")
        
        return success
    
    def allow_ip(self, ip_address: str) -> bool:
        """Explicitly allow an IP address (whitelist)
        
        Args:
            ip_address: IP address to allow
            
        Returns:
            True if successful
        """
        success = self._run_iptables_command([
            'sudo', 'iptables', '-I', 'INPUT', '1',
            '-s', ip_address,
            '-j', 'ACCEPT'
        ])
        
        if success:
            logger.info(f"IP {ip_address} whitelisted")
        
        return success
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of currently blocked IPs
        
        Returns:
            List of blocked IP addresses
        """
        return list(self.blocked_ips)
    
    def get_quarantined_ips(self) -> List[str]:
        """Get list of currently quarantined IPs
        
        Returns:
            List of quarantined IP addresses
        """
        return list(self.quarantined_ips)
    
    def flush_rules(self) -> bool:
        """Flush all iptables rules (DANGEROUS - use with caution)
        
        Returns:
            True if successful
        """
        logger.warning("Flushing all iptables rules!")
        
        success = self._run_iptables_command([
            'sudo', 'iptables', '-F'
        ])
        
        if success:
            self.blocked_ips.clear()
            self.quarantined_ips.clear()
            self.quarantine_times.clear()
        
        return success
    
    def save_rules(self, filepath: str = "/etc/iptables/rules.v4") -> bool:
        """Save current iptables rules to file
        
        Args:
            filepath: Path to save rules
            
        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ['sudo', 'iptables-save'],
                capture_output=True,
                text=True,
                check=True
            )
            
            with open(filepath, 'w') as f:
                f.write(result.stdout)
            
            logger.info(f"iptables rules saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save iptables rules: {e}")
            return False
