# 🛡️ Project Argus: AI-Driven Network Threat Intelligence Platform

**A Lightweight, AI-Driven NIDS/NIPS for SOHO Networks**

Project Argus is an advanced, low-cost network security platform designed to protect small office/home office (SOHO) environments. It runs on lightweight hardware (Raspberry Pi 4/5) and uses behavioral anomaly detection (AI) to identify, rate, and prevent threats from both outside attackers and compromised internal devices.

## 🌟 Key Features

- **🤖 AI-Powered Anomaly Detection**: Uses Autoencoder neural networks to detect deviations from normal device behavior
- **📊 Dynamic Device Trust Score**: Rates all network devices (0-100) based on AI-detected anomalies, port scans, and threat intelligence
- **🚫 Active Intrusion Prevention (IPS)**: Automatically blocks or quarantines devices with critically low trust scores
- **🔍 Vulnerability Scanning**: Scans new devices for security flaws (open Telnet/FTP ports, etc.)
- **📈 Real-time Dashboard**: Self-hosted web interface for analytics and device management
- **🔒 Privacy-First**: All data stays on your device - no cloud subscriptions required

## 🏗️ Architecture

### Hardware Requirements
- **Raspberry Pi 4/5** (4GB+ RAM recommended)
- **Dual Network Interfaces**: Built-in Ethernet + USB Ethernet adapter (for inline mode)
- **MicroSD Card**: 32GB+ for OS and data storage
- **Power Supply**: Official Raspberry Pi power supply

### Operating Modes

1. **Passive Mode (IDS)**: 
   - Monitors network traffic via SPAN/mirror port
   - Detects and alerts on threats
   - Safer and easier to set up
   
2. **Inline Mode (IPS)**:
   - Sits between modem and router
   - Can actively block malicious traffic
   - Requires IP forwarding and NAT configuration

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/phoenixdev-512/advanced-AI-IDSIPSframework.git
cd advanced-AI-IDSIPSframework
```

2. **Run the setup script** (on Raspberry Pi):
```bash
chmod +x scripts/setup.sh
sudo ./scripts/setup.sh
```

3. **Configure InfluxDB**:
   - Access InfluxDB at `http://localhost:8086`
   - Create an organization and bucket
   - Generate an API token
   - Update `.env` file with credentials

4. **Train the AI model**:
```bash
source venv/bin/activate
python3 train_model.py --synthetic --num-flows 5000
```

5. **Start the services**:
```bash
sudo systemctl start argus-capture argus-api argus-dashboard
```

6. **Access the dashboard**:
   - Open browser to `http://localhost:8050`

## 📚 Documentation

### Configuration

Edit `.env` file to configure:
- Network interface to monitor
- InfluxDB connection details
- Trust score thresholds
- IPS behavior (auto-block settings)
- API and dashboard ports

Example `.env`:
```bash
CAPTURE_INTERFACE=eth0
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-token-here
INFLUXDB_ORG=argus
INFLUXDB_BUCKET=network_traffic
TRUST_SCORE_CRITICAL_THRESHOLD=20
IPS_ENABLED=true
AUTO_BLOCK_ENABLED=true
```

### Training the Model

**Using real network data** (after collecting 24+ hours):
```bash
python3 train_model.py --model autoencoder --hours 24
```

**Using synthetic data** (for testing):
```bash
python3 train_model.py --synthetic --num-flows 5000
```

### Running Components

**All-in-one** (capture + API + dashboard):
```bash
python3 main.py full --mode passive
```

**Individual components**:
```bash
# Packet capture only
python3 main.py start --mode passive

# API server only
python3 main.py api

# Dashboard only
python3 main.py dashboard
```

### API Endpoints

- `GET /api/devices` - List all devices and trust scores
- `GET /api/devices/{ip}` - Get specific device info
- `GET /api/devices/low-trust` - List devices below threshold
- `POST /api/devices/action` - Whitelist/blacklist/block device
- `POST /api/scan` - Scan device for vulnerabilities
- `GET /api/ips/blocked` - List blocked IPs
- `GET /api/stats` - System statistics

## 🎯 Use Cases

### 1. Home Network Protection
- Monitor IoT devices (cameras, smart TVs, etc.)
- Detect compromised devices
- Block malicious connections

### 2. Small Office Security
- Protect against ransomware
- Monitor employee devices
- Detect data exfiltration

### 3. Network Security Research
- Study attack patterns
- Test IDS/IPS effectiveness
- Analyze network behavior

## 🛠️ Tech Stack

- **Packet Capture**: Scapy
- **AI/ML**: TensorFlow/Keras, scikit-learn
- **Database**: InfluxDB (time-series)
- **Backend**: FastAPI
- **Frontend**: Plotly Dash
- **IPS**: iptables
- **Scanning**: python-nmap

## 📊 Dashboard Features

- **Real-time monitoring**: Live network traffic visualization
- **Device trust scores**: Color-coded trust ratings
- **Alert panel**: Recent security events
- **Device management**: Whitelist/blacklist controls
- **Statistics**: Network-wide security metrics

## 🔐 Security Considerations

1. **Run with appropriate privileges**: Packet capture requires root
2. **Secure the dashboard**: Use firewall to restrict access
3. **Regular updates**: Keep system and dependencies updated
4. **Whitelist critical devices**: Prevent accidental blocking of routers/servers
5. **Test in passive mode first**: Before enabling inline IPS

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

## 📈 Roadmap

- [ ] Phase 1: Core packet capture and storage ✅
- [ ] Phase 2: AI model training and detection ✅
- [ ] Phase 3: Dashboard and visualization ✅
- [ ] Phase 4: IPS and prevention ✅
- [ ] Phase 5: Threat intelligence integration
- [ ] Phase 6: Advanced analytics and reporting
- [ ] Phase 7: Mobile app for monitoring
- [ ] Phase 8: Multi-device support and clustering

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by enterprise-grade NIDS/NIPS solutions
- Built for the cybersecurity community
- Designed to make network security accessible to everyone

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**⚠️ Disclaimer**: This tool is for educational and legitimate network security purposes only. Users are responsible for compliance with applicable laws and regulations.