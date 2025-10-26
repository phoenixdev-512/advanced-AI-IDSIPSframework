# API Reference

## Base URL
```
http://localhost:8000
```

## Endpoints

### System Status

#### GET /
Get API information and status.

**Response:**
```json
{
  "name": "Project Argus API",
  "version": "1.0.0",
  "status": "running"
}
```

### Devices

#### GET /api/devices
List all devices and their trust scores.

**Response:**
```json
[
  {
    "device_ip": "192.168.1.100",
    "trust_score": 85.5,
    "behavioral_score": 90.0,
    "vulnerability_score": 75.0,
    "reputation_score": 100.0,
    "last_updated": "2025-10-26T19:00:00",
    "anomaly_count": 2,
    "vulnerable_ports": [80],
    "is_whitelisted": false,
    "is_blacklisted": false
  }
]
```

#### GET /api/devices/{device_ip}
Get specific device information.

**Parameters:**
- `device_ip` (path): IP address of device

**Response:** Same as single device object above.

#### GET /api/devices/low-trust
Get devices with trust scores below threshold.

**Query Parameters:**
- `threshold` (optional, default: 50.0): Trust score threshold

**Response:**
```json
[
  {
    "device_ip": "192.168.1.101",
    "trust_score": 35.2
  }
]
```

#### POST /api/devices/action
Perform action on a device.

**Request Body:**
```json
{
  "device_ip": "192.168.1.100",
  "action": "whitelist"  // whitelist, blacklist, block, unblock, quarantine
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Device 192.168.1.100 whitelisted"
}
```

### Scanning

#### POST /api/scan
Scan device for vulnerabilities.

**Request Body:**
```json
{
  "device_ip": "192.168.1.100",
  "quick": true
}
```

**Response:**
```json
{
  "device_ip": "192.168.1.100",
  "scan_success": true,
  "hostname": "device-name",
  "state": "up",
  "open_ports": [22, 80, 443],
  "vulnerable_ports": [80],
  "vulnerability_details": [
    {
      "port": 80,
      "service": "HTTP (unencrypted web)",
      "severity": "medium"
    }
  ]
}
```

### IPS

#### GET /api/ips/blocked
Get list of blocked and quarantined IPs.

**Response:**
```json
{
  "blocked_ips": ["192.168.1.200"],
  "quarantined_ips": ["192.168.1.201"]
}
```

### Statistics

#### GET /api/stats
Get system statistics.

**Response:**
```json
{
  "total_devices": 15,
  "low_trust_devices": 3,
  "critical_devices": 1,
  "whitelisted_devices": 2,
  "blacklisted_devices": 1,
  "blocked_ips": 2
}
```

### WebSocket

#### WS /ws
WebSocket endpoint for real-time updates.

Connect to receive real-time notifications about:
- New devices detected
- Trust score changes
- Security alerts
- Blocked IPs

**Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

## Error Responses

All endpoints may return error responses:

**404 Not Found:**
```json
{
  "detail": "Device not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Trust manager not initialized"
}
```

## Rate Limiting

Currently no rate limiting is enforced. Consider implementing rate limiting for production deployments.

## Authentication

Currently no authentication is required. For production deployments, implement authentication using:
- API keys
- JWT tokens
- OAuth2

## Interactive Documentation

FastAPI provides interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
