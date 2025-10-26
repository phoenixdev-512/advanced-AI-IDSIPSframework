# Project Argus - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Network Traffic                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               Packet Capture Module                          │
│  - Scapy-based packet sniffing                              │
│  - Network flow extraction and aggregation                   │
│  - Real-time flow tracking                                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Feature Preprocessing                           │
│  - Extract flow statistics                                   │
│  - Protocol encoding                                         │
│  - Feature normalization                                     │
└───────────┬──────────────────────────┬──────────────────────┘
            │                          │
            ▼                          ▼
┌──────────────────────┐    ┌──────────────────────┐
│  InfluxDB Storage    │    │   AI/ML Model        │
│  - Time-series data  │    │  - Autoencoder       │
│  - Flow logs         │    │  - Isolation Forest  │
│  - Device scores     │    │  - Anomaly detection │
│  - Alerts            │    │  - TFLite optimized  │
└──────────────────────┘    └──────────┬───────────┘
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │  Trust Score Manager     │
                        │  - Behavioral score      │
                        │  - Vulnerability score   │
                        │  - Reputation score      │
                        │  - Score decay/recovery  │
                        └──────────┬───────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Vulnerability│  │   IPS/IDS    │  │  Threat      │
        │  Scanner     │  │  - iptables  │  │ Intelligence │
        │  - nmap      │  │  - Blocking  │  │  - Feeds     │
        │  - Port scan │  │  - Quarantine│  │  - Blacklist │
        └──────────────┘  └──────┬───────┘  └──────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Auto Prevention      │
                    │  - Trigger on low score│
                    │  - Configurable rules  │
                    └────────────────────────┘
                                 │
                    ┌────────────┴───────────┐
                    │                        │
                    ▼                        ▼
        ┌──────────────────┐    ┌──────────────────┐
        │   FastAPI        │    │  Plotly Dash     │
        │   Backend        │    │  Dashboard       │
        │  - REST API      │◄───┤  - Real-time UI  │
        │  - WebSocket     │    │  - Device mgmt   │
        │  - Device mgmt   │    │  - Analytics     │
        └──────────────────┘    └──────────────────┘
                    │                        │
                    └────────────┬───────────┘
                                 │
                                 ▼
                        ┌────────────────┐
                        │   Admin User   │
                        │  - Monitoring  │
                        │  - Management  │
                        │  - Alerts      │
                        └────────────────┘
```

## Component Details

### 1. Packet Capture Module (`src/capture/`)
- **NetworkFlow**: Bidirectional flow tracking
- **PacketCapture**: Real-time packet sniffing using Scapy
- **InfluxDBManager**: Time-series data storage

**Key Features:**
- Automatic flow aggregation
- Flow timeout handling
- Efficient memory management
- Background processing

### 2. AI/ML Models (`src/models/`)
- **AutoencoderModel**: Neural network for anomaly detection
  - Learns normal traffic patterns
  - Reconstruction error as anomaly score
  - TFLite conversion for Raspberry Pi
- **IsolationForestModel**: Tree-based anomaly detection
  - Fast and efficient
  - Alternative to Autoencoder
- **FeaturePreprocessor**: Feature engineering and normalization

**Features Extracted:**
- Port numbers
- Protocol type
- Flow duration
- Packet counts (forward/backward)
- Byte counts (forward/backward)
- Packet inter-arrival time
- Derived ratios and rates

### 3. Trust Scoring System (`src/scoring/`)
- **TrustScoreManager**: Multi-factor trust scoring
  - Behavioral score (from AI model)
  - Vulnerability score (from port scans)
  - Reputation score (from threat feeds)
  - Weighted combination
  - Time-based decay/recovery

- **VulnerabilityScanner**: Network security scanning
  - nmap integration
  - Dangerous port detection
  - Automated scanning for new devices

### 4. IPS Module (`src/ips/`)
- **IPTablesManager**: Firewall rule management
  - IP blocking
  - Quarantine (temporary block)
  - Rate limiting
  - Whitelist management

**Safety Features:**
- Dry-run mode
- Quarantine expiry
- Manual override capability

### 5. API Backend (`src/api/`)
- **FastAPI Application**
  - RESTful API
  - WebSocket for real-time updates
  - Device management
  - Scanning controls
  - Statistics endpoints

**Security Considerations:**
- CORS enabled (configure for production)
- No authentication by default (add for production)
- Input validation via Pydantic

### 6. Dashboard (`src/dashboard/`)
- **Plotly Dash Interface**
  - Real-time statistics
  - Trust score visualization
  - Device table with management
  - Alert panel
  - Auto-refresh (5 seconds)

**Features:**
- Color-coded trust levels
- Interactive charts
- Device action buttons
- Responsive design

## Data Flow

1. **Capture Phase:**
   - Raw packets → Flow extraction → Feature computation

2. **Analysis Phase:**
   - Features → Preprocessing → ML Model → Anomaly scores

3. **Scoring Phase:**
   - Anomaly scores → Trust score update → Action triggers

4. **Prevention Phase:**
   - Low trust scores → IPS actions → Block/Quarantine

5. **Visualization Phase:**
   - All data → API → Dashboard → User

## Operating Modes

### Passive Mode (IDS)
```
Network → SPAN Port → Raspberry Pi → InfluxDB
                           ↓
                        Analysis
                           ↓
                      Alerts Only
```

### Inline Mode (IPS)
```
Modem → Raspberry Pi → Router → Devices
           ↓
    Analysis + Blocking
           ↓
    Active Prevention
```

## Deployment Architecture

### Systemd Services
- `argus-capture.service`: Packet capture and analysis
- `argus-api.service`: API backend
- `argus-dashboard.service`: Web dashboard

### Data Storage
- **InfluxDB**: Time-series data
  - Network flows
  - Trust scores
  - Anomaly events
  - Alerts

- **Local Files**:
  - ML models (`.h5`, `.tflite`)
  - Preprocessor (`.pkl`)
  - Configuration (`.env`, `.yaml`)

## Security Model

### Defense in Depth
1. **Detection Layer**: AI anomaly detection
2. **Assessment Layer**: Trust scoring
3. **Prevention Layer**: IPS blocking
4. **Response Layer**: Automated actions

### Trust Score Calculation
```
Trust Score = 
    (Behavioral × 0.5) + 
    (Vulnerability × 0.3) + 
    (Reputation × 0.2)
```

### Action Thresholds
- **100-75**: Normal (green)
- **75-50**: Warning (yellow)
- **50-20**: Alert (orange)
- **< 20**: Critical - Auto-block if enabled (red)

## Performance Considerations

### Raspberry Pi 4/5
- **CPU**: Use TFLite for optimized inference
- **Memory**: Flow aggregation reduces memory usage
- **Storage**: InfluxDB handles data retention
- **Network**: Gigabit Ethernet recommended

### Optimization Strategies
- Batch processing of flows
- Model inference on aggregated flows (not packets)
- Background threads for non-critical tasks
- Efficient data structures (dataclasses)

## Extensibility

### Adding New Features
1. Extend `FeaturePreprocessor.extract_features()`
2. Retrain model with new features
3. Update configuration

### Adding New Models
1. Implement model class in `src/models/`
2. Follow interface pattern (train, predict_anomaly)
3. Update `train_model.py`

### Adding New Threat Feeds
1. Extend `TrustScoreManager`
2. Add reputation score update logic
3. Schedule periodic updates

## Future Enhancements

- [ ] Machine learning model retraining
- [ ] Advanced threat intelligence integration
- [ ] Multi-device clustering and coordination
- [ ] Mobile application for monitoring
- [ ] Email/SMS alerting
- [ ] Advanced analytics and reporting
- [ ] Network topology mapping
- [ ] Encrypted traffic analysis (metadata)
