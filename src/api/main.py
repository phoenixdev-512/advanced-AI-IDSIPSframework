"""
FastAPI backend for Project Argus
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import asyncio

from ..scoring import TrustScoreManager, VulnerabilityScanner
from ..ips import IPTablesManager
from ..utils import get_network_interfaces

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Project Argus API",
    description="AI-Driven Network Threat Intelligence Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (will be set by main application)
trust_manager: Optional[TrustScoreManager] = None
ips_manager: Optional[IPTablesManager] = None
vulnerability_scanner: Optional[VulnerabilityScanner] = None

# Global state for capture management
current_interface: str = "eth0"
current_mode: str = "passive"  # passive or simulated
capture_restart_callback = None


def set_current_state(interface: str, mode: str):
    """Set the current interface and mode"""
    global current_interface, current_mode
    current_interface = interface
    current_mode = mode


# WebSocket connections
websocket_connections: List[WebSocket] = []


# Pydantic models
class DeviceInfo(BaseModel):
    """Device information model"""
    device_ip: str
    trust_score: float
    behavioral_score: float
    vulnerability_score: float
    reputation_score: float
    last_updated: str
    anomaly_count: int
    vulnerable_ports: List[int]
    is_whitelisted: bool
    is_blacklisted: bool


class AlertInfo(BaseModel):
    """Alert information model"""
    device_ip: str
    alert_type: str
    severity: str
    message: str
    timestamp: str


class ActionRequest(BaseModel):
    """Device action request model"""
    device_ip: str
    action: str  # whitelist, blacklist, block, unblock, quarantine


class ScanRequest(BaseModel):
    """Vulnerability scan request model"""
    device_ip: str
    quick: bool = True


class InterfaceUpdateRequest(BaseModel):
    """Network interface update request model"""
    interface: str
    mode: str = "passive"  # passive or simulated


# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Project Argus API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/devices", response_model=List[DeviceInfo])
async def get_devices():
    """Get all devices and their trust scores"""
    if not trust_manager:
        raise HTTPException(status_code=500, detail="Trust manager not initialized")
    
    devices = trust_manager.get_all_devices()
    
    return [
        DeviceInfo(
            device_ip=device.device_ip,
            trust_score=device.trust_score,
            behavioral_score=device.behavioral_score,
            vulnerability_score=device.vulnerability_score,
            reputation_score=device.reputation_score,
            last_updated=datetime.fromtimestamp(device.last_updated).isoformat(),
            anomaly_count=device.anomaly_count,
            vulnerable_ports=device.vulnerable_ports,
            is_whitelisted=device.is_whitelisted,
            is_blacklisted=device.is_blacklisted
        )
        for device in devices
    ]


@app.get("/api/devices/{device_ip}", response_model=DeviceInfo)
async def get_device(device_ip: str):
    """Get specific device information"""
    if not trust_manager:
        raise HTTPException(status_code=500, detail="Trust manager not initialized")
    
    device = trust_manager.get_device_score(device_ip)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return DeviceInfo(
        device_ip=device.device_ip,
        trust_score=device.trust_score,
        behavioral_score=device.behavioral_score,
        vulnerability_score=device.vulnerability_score,
        reputation_score=device.reputation_score,
        last_updated=datetime.fromtimestamp(device.last_updated).isoformat(),
        anomaly_count=device.anomaly_count,
        vulnerable_ports=device.vulnerable_ports,
        is_whitelisted=device.is_whitelisted,
        is_blacklisted=device.is_blacklisted
    )


@app.get("/api/devices/low-trust")
async def get_low_trust_devices(threshold: float = 50.0):
    """Get devices with low trust scores"""
    if not trust_manager:
        raise HTTPException(status_code=500, detail="Trust manager not initialized")
    
    devices = trust_manager.get_low_trust_devices(threshold)
    
    return [
        {
            "device_ip": device.device_ip,
            "trust_score": device.trust_score
        }
        for device in devices
    ]


@app.post("/api/devices/action")
async def device_action(request: ActionRequest):
    """Perform action on a device"""
    if not trust_manager or not ips_manager:
        raise HTTPException(status_code=500, detail="Managers not initialized")
    
    device_ip = request.device_ip
    action = request.action
    
    if action == "whitelist":
        trust_manager.whitelist_device(device_ip)
        ips_manager.allow_ip(device_ip)
        return {"status": "success", "message": f"Device {device_ip} whitelisted"}
    
    elif action == "blacklist":
        trust_manager.blacklist_device(device_ip)
        ips_manager.block_ip(device_ip, permanent=True)
        return {"status": "success", "message": f"Device {device_ip} blacklisted"}
    
    elif action == "block":
        ips_manager.block_ip(device_ip)
        return {"status": "success", "message": f"Device {device_ip} blocked"}
    
    elif action == "unblock":
        ips_manager.unblock_ip(device_ip)
        return {"status": "success", "message": f"Device {device_ip} unblocked"}
    
    elif action == "quarantine":
        ips_manager.quarantine_ip(device_ip)
        return {"status": "success", "message": f"Device {device_ip} quarantined"}
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


@app.post("/api/scan")
async def scan_device(request: ScanRequest):
    """Scan device for vulnerabilities"""
    if not vulnerability_scanner:
        raise HTTPException(status_code=500, detail="Vulnerability scanner not initialized")
    
    result = vulnerability_scanner.scan_device(request.device_ip, quick=request.quick)
    
    return result


@app.get("/api/ips/blocked")
async def get_blocked_ips():
    """Get list of blocked IPs"""
    if not ips_manager:
        raise HTTPException(status_code=500, detail="IPS manager not initialized")
    
    return {
        "blocked_ips": ips_manager.get_blocked_ips(),
        "quarantined_ips": ips_manager.get_quarantined_ips()
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    if not trust_manager:
        raise HTTPException(status_code=500, detail="Trust manager not initialized")
    
    all_devices = trust_manager.get_all_devices()
    
    return {
        "total_devices": len(all_devices),
        "low_trust_devices": len(trust_manager.get_low_trust_devices(50)),
        "critical_devices": len(trust_manager.get_low_trust_devices(20)),
        "whitelisted_devices": len([d for d in all_devices if d.is_whitelisted]),
        "blacklisted_devices": len([d for d in all_devices if d.is_blacklisted]),
        "blocked_ips": len(ips_manager.get_blocked_ips()) if ips_manager else 0
    }


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


async def broadcast_update(message: Dict[str, Any]):
    """Broadcast update to all connected WebSocket clients"""
    for connection in websocket_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to WebSocket: {e}")


# Network interface management endpoints
@app.get("/api/interfaces")
async def get_interfaces():
    """Get list of available network interfaces"""
    interfaces = get_network_interfaces()
    return {
        "interfaces": interfaces,
        "current_interface": current_interface,
        "current_mode": current_mode
    }


@app.post("/api/interfaces/update")
async def update_interface(request: InterfaceUpdateRequest):
    """Update the network interface for packet capture
    
    This endpoint will trigger a restart of the capture process
    """
    global current_interface, current_mode
    
    interface = request.interface
    mode = request.mode
    
    # Validate interface
    interfaces = get_network_interfaces()
    valid_interfaces = [iface['name'] for iface in interfaces]
    
    if interface not in valid_interfaces:
        raise HTTPException(status_code=400, detail=f"Invalid interface: {interface}")
    
    # Update global state
    current_interface = interface
    current_mode = mode
    
    # Update config file
    try:
        import yaml
        from pathlib import Path
        
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        config_data['capture']['interface'] = interface
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        logger.info(f"Updated config.yaml with interface: {interface}")
    except Exception as e:
        logger.error(f"Error updating config.yaml: {e}")
    
    # Trigger restart callback if available
    if capture_restart_callback:
        try:
            await capture_restart_callback(interface, mode)
        except Exception as e:
            logger.error(f"Error restarting capture: {e}")
            raise HTTPException(status_code=500, detail=f"Error restarting capture: {str(e)}")
    
    return {
        "status": "success",
        "message": f"Interface updated to {interface} in {mode} mode",
        "interface": interface,
        "mode": mode
    }


@app.get("/api/system/status")
async def get_system_status():
    """Get current system status"""
    return {
        "mode": current_mode,
        "interface": current_interface,
        "status": "ONLINE"
    }


# Initialization function
def initialize_api(trust_mgr: TrustScoreManager, 
                  ips_mgr: IPTablesManager,
                  vuln_scanner: VulnerabilityScanner,
                  restart_callback=None):
    """Initialize API with manager instances
    
    Args:
        trust_mgr: Trust score manager instance
        ips_mgr: IPS manager instance
        vuln_scanner: Vulnerability scanner instance
        restart_callback: Optional callback function for restarting capture
    """
    global trust_manager, ips_manager, vulnerability_scanner, capture_restart_callback
    trust_manager = trust_mgr
    ips_manager = ips_mgr
    vulnerability_scanner = vuln_scanner
    capture_restart_callback = restart_callback
    logger.info("API initialized with manager instances")
