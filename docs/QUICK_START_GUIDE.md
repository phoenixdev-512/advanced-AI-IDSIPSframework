# Quick Start: New Dashboard Features

## Switching to Simulated Traffic Mode

Perfect for demonstrations or testing without physical hardware!

1. Open the dashboard at `http://localhost:8050`
2. Find the "Network Monitoring Configuration" card (left side, below statistics)
3. Click the dropdown menu
4. Select "Simulated Traffic (Demo Mode)"
5. Click "🔄 Apply & Restart Monitoring"
6. Watch the dashboard populate with synthetic network traffic!

**What happens**:
- System generates realistic network flows
- Approximately 8% of traffic will be anomalous (port scans, suspicious connections, etc.)
- Trust scores will update based on detected anomalies
- Alerts will appear for suspicious behavior

## Switching Between Network Interfaces

To monitor a different physical network interface:

1. Open the dashboard
2. Go to "Network Monitoring Configuration" card
3. Select your desired interface (e.g., "eth0 (192.168.1.10)")
4. Click "🔄 Apply & Restart Monitoring"
5. System restarts monitoring on the new interface

## Changing Dashboard Theme

### Light Mode (for bright environments)
- Click "🌞 Light Mode" button in the top-right
- Dashboard switches to light theme
- Preference saved automatically

### Dark Mode (default)
- Click "🌙 Dark Mode" button in the top-right
- Dashboard switches to dark theme
- Preference saved automatically

## Quick Actions

### Scan for New Devices
- Click "🔍 Scan for New Devices"
- System initiates vulnerability scanning
- Results appear in device table

### Block/Quarantine Suspicious Devices
- Click "🚫 Block/Quarantine Selected"
- Note: Select devices from table first
- Blocks or temporarily quarantines devices

### View Device Details
- Click "📋 View Details"
- Shows detailed information in device table below

## Understanding System Status

Look at the badge below the header:

- 🟢 **ONLINE (Passive Mode - eth0)**: Monitoring real traffic on eth0
- 🟢 **ONLINE (Simulated Mode)**: Generating demo traffic
- ⚪ **OFFLINE**: System not active

## Dashboard Cards Explained

### Statistics (Top Row)
- **Total Devices**: Number of devices detected
- **Low Trust**: Devices with trust score 20-50
- **Critical**: Devices with trust score below 20
- **Blocked IPs**: Number of currently blocked IPs

### Network Monitoring Configuration
- Interface selection dropdown
- Apply button to switch interfaces
- Description of selected mode

### System Overview
- Quick summary of monitoring hub
- Device count indicator

### Device Trust Scores (Chart)
- Visual bar chart of all device trust scores
- Color-coded: Red (critical), Orange (low), Yellow (medium), Green (good)

### Recent Alerts
- Latest 5 security alerts
- Devices with trust scores below 50

### Quick Actions
- Fast access to common operations
- Scan, block, and view actions

### Device Management Table
- Complete list of all detected devices
- Trust scores, anomaly counts, vulnerable ports
- Status badges
- Action buttons (whitelist, block)

## Tips for Demonstrations

1. **Start with Simulated Mode**: Shows activity immediately
2. **Enable Dark Mode**: Looks professional in presentations
3. **Watch for Anomalies**: Red alerts will appear automatically
4. **Explain Trust Scores**: Point out how scores drop with suspicious activity
5. **Show Interface Switching**: Demonstrate flexibility without restart

## Troubleshooting

**Q: Dropdown is empty?**
- Refresh the page
- Check network interfaces are active: `ip link show`

**Q: No simulated traffic appearing?**
- Wait 10-15 seconds for flows to generate
- Check system status shows "Simulated Mode"
- Refresh the page

**Q: Theme doesn't save?**
- Enable browser localStorage
- Clear browser cache
- Try incognito/private mode

**Q: Interface switch doesn't work?**
- Check you have permissions
- Verify interface name is correct
- Look at browser console for errors

## Example Demo Flow

1. Start dashboard: `python3 main.py dashboard`
2. Switch to Light Mode for presentation
3. Select "Simulated Traffic (Demo Mode)"
4. Click "Apply & Restart Monitoring"
5. Wait 30 seconds for data to populate
6. Point out various devices in the chart
7. Highlight anomalies in the Alerts panel
8. Show trust score drops for suspicious devices
9. Demonstrate Quick Actions buttons
10. Show device details in table

Perfect for showing Project Argus capabilities without needing actual network hardware!
