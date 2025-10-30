# Project Argus Dashboard Enhancements

## Overview

This document describes the new features added to Project Argus to enhance its flexibility, user experience, and demonstration capabilities.

## New Features

### 1. Dynamic Network Interface Selection

**Location**: Dashboard homepage - Network Monitoring Configuration card

**Purpose**: Allows users to dynamically switch between network interfaces without editing configuration files or restarting the application manually.

**Features**:
- Dropdown menu populated with all available network interfaces on the system
- Each interface displays its name and IP address (e.g., "eth0 (192.168.1.10)")
- Special "Simulated Traffic (Demo Mode)" option for demonstrations
- "Apply & Restart Monitoring" button to switch interfaces
- Visual feedback with success/error notifications

**Usage**:
1. Select desired interface from the dropdown
2. Click "Apply & Restart Monitoring"
3. System will update configuration and restart monitoring
4. Status indicator updates to show current mode

### 2. Simulated Traffic Mode

**Purpose**: Generate synthetic network traffic for demonstrations and testing without requiring actual network devices or dual interfaces.

**Features**:
- Generates realistic network flows with normal behavior patterns
- Injects configurable anomalies (8% by default):
  - Port scanning attempts
  - Data exfiltration patterns
  - DDoS-like traffic
  - Connections to suspicious ports
- Uses same data structure as real packet capture
- Fully compatible with AI models and trust scoring

**Traffic Patterns Generated**:
- **Normal Traffic**:
  - HTTP/HTTPS web browsing
  - DNS lookups
  - Email (SMTP)
  - NTP time sync
  
- **Anomalous Traffic**:
  - Port scanning (rapid connections to sequential ports)
  - Large data uploads (data exfiltration)
  - High-volume packet floods (DDoS)
  - Connections to dangerous ports (Telnet, FTP, SMB, RDP)

**Usage**:
1. Select "Simulated Traffic (Demo Mode)" from interface dropdown
2. Click "Apply & Restart Monitoring"
3. System status will show "ONLINE (Simulated Mode)"
4. Dashboard will populate with synthetic traffic data

### 3. Light/Dark Mode Toggle

**Location**: Top-right of dashboard

**Purpose**: Allow users to customize the visual theme based on preference or environment.

**Features**:
- Two-button toggle: "🌞 Light Mode" and "🌙 Dark Mode"
- Theme preference persisted in browser localStorage
- Smooth transitions between themes
- All UI components adapt to selected theme:
  - Background colors
  - Text colors
  - Card borders
  - Graph backgrounds
  - Alert colors
  - Table styles

**Usage**:
- Click "🌞 Light Mode" for light theme
- Click "🌙 Dark Mode" for dark theme
- Preference automatically saved and restored on next visit

### 4. Enhanced System Status Indicator

**Location**: Below main header, centered

**Purpose**: Clearly display current system operational mode.

**Modes**:
- 🟢 ONLINE (Passive Mode - eth0) - Monitoring real traffic
- 🟢 ONLINE (Simulated Mode) - Generating demo traffic
- ⚪ OFFLINE - System not running

### 5. Updated Quick Actions Card

**Location**: Below main content area

**Purpose**: Provide quick access to common security actions.

**Buttons**:
- **🔍 Scan for New Devices**: Initiate vulnerability scanning for newly detected devices
- **🚫 Block/Quarantine Selected**: Block or temporarily quarantine suspicious devices
- **📋 View Details**: Navigate to detailed device information

## Technical Implementation

### Backend Components

#### Network Utilities (`src/utils/network_utils.py`)
- Uses `psutil` to detect available network interfaces
- Returns interface details including name, IP addresses, and status
- Filters out loopback interface
- Adds simulated traffic option

#### Simulated Traffic Generator (`src/capture/simulated_capture.py`)
- Generates realistic network flows in background thread
- Configurable anomaly injection rate
- Produces flows compatible with existing processing pipeline
- Thread-safe flow collection

#### API Endpoints
- `GET /api/interfaces` - List available interfaces
- `POST /api/interfaces/update` - Switch interface
- `GET /api/system/status` - Get current system status

### Frontend Components

#### Dashboard Updates (`src/dashboard/main.py`)
- Network Monitoring Configuration card with interface selector
- Theme toggle buttons with localStorage persistence
- System status badge with mode indicator
- Updated Quick Actions with new buttons
- Clientside callback for theme application

### Configuration Updates

#### Dynamic Interface Update (`src/config.py`)
- New `update_interface()` method for runtime updates
- Persists interface selection to config.yaml

#### Main Application (`main.py`)
- Support for simulated traffic mode
- Dynamic interface switching capability
- Restart callback for API integration

## API Reference

### GET /api/interfaces
Returns list of available network interfaces and current state.

**Response**:
```json
{
  "interfaces": [
    {
      "name": "eth0",
      "addresses": ["192.168.1.10"],
      "is_up": true,
      "display_name": "eth0 (192.168.1.10)"
    },
    {
      "name": "simulated",
      "addresses": [],
      "is_up": true,
      "display_name": "Simulated Traffic (Demo Mode)"
    }
  ],
  "current_interface": "eth0",
  "current_mode": "passive"
}
```

### POST /api/interfaces/update
Updates the network interface for packet capture.

**Request**:
```json
{
  "interface": "eth0",
  "mode": "passive"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Interface updated to eth0 in passive mode",
  "interface": "eth0",
  "mode": "passive"
}
```

### GET /api/system/status
Returns current system operational status.

**Response**:
```json
{
  "mode": "passive",
  "interface": "eth0",
  "status": "ONLINE"
}
```

## Configuration

### Simulated Traffic Settings

To adjust anomaly injection rate, modify the initialization in `main.py`:

```python
self.packet_capture = SimulatedTrafficGenerator(anomaly_rate=0.08)  # 8% anomalies
```

### Theme Customization

Default theme is set in dashboard initialization. To change default:

```python
dcc.Store(id='theme-store', storage_type='local', data='light')  # Change to 'light'
```

## Testing

### Running Tests

```bash
# Test network utilities
pytest tests/test_network_utils.py -v

# Test API endpoints
pytest tests/test_api.py -v

# Run all tests
pytest tests/ -v
```

### Test Coverage

- Network interface detection
- Simulated traffic generation (normal and anomalous flows)
- API endpoint functionality
- Interface update validation

## Security Considerations

1. **Interface Switching**: Only administrators should have access to the dashboard
2. **Simulated Mode**: Clearly indicated to prevent confusion with real threats
3. **Configuration Updates**: Config file writes require appropriate permissions
4. **Dependencies**: All dependencies scanned for vulnerabilities (no issues found)

## Future Enhancements

Potential improvements for future versions:

1. **Enhanced Device Icons**: More specific icons for different device types
2. **Traffic Pattern Customization**: UI controls for adjusting simulation parameters
3. **Export Configuration**: Save and load interface preferences
4. **Multi-Interface Monitoring**: Simultaneously monitor multiple interfaces
5. **Advanced Anomaly Patterns**: Additional attack simulation types

## Troubleshooting

### Interface not appearing in dropdown
- Ensure interface is active: `ip link show`
- Check psutil can detect it: `python3 -c "import psutil; print(psutil.net_if_stats())"`

### Simulated traffic not generating
- Check logs: `tail -f data/logs/argus.log`
- Verify mode is set to "simulated"
- Restart monitoring service

### Theme not persisting
- Check browser localStorage is enabled
- Clear browser cache and reload
- Verify JavaScript is enabled

### Interface switch fails
- Check permissions for config file write
- Ensure selected interface is valid
- Review API logs for detailed error messages

## Credits

Enhancements implemented as part of Project Argus evolution to support demonstration and deployment flexibility.
