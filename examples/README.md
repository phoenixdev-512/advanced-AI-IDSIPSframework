# Examples Directory

This directory contains sample scripts and data for demonstrating Project Argus capabilities.

## 🎯 Quick Demo

To see Project Argus in action without any hardware setup:

```bash
python3 examples/demo.py
```

This runs a complete end-to-end detection flow using sample network traffic.

## 📁 Contents

### Scripts

- **`demo.py`** - Complete detection flow demonstration
  - Loads sample PCAP traffic
  - Trains anomaly detection model
  - Analyzes traffic and detects threats
  - Calculates device trust scores
  - Displays results with color-coded threat levels
  
- **`usage_examples.py`** - Component usage examples
  - Model training examples
  - Trust score management examples
  - Useful for learning individual components

- **`generate_sample_pcap.py`** - PCAP file generator
  - Creates sample network traffic with realistic patterns
  - Includes both normal and anomalous traffic
  - Useful for testing and development

### Data

- **`demo_data/sample_traffic.pcap`** - Sample network capture (4.6KB)
  - 64 packets of realistic network traffic
  - Includes normal web browsing (DNS, HTTPS)
  - Contains suspicious port scanning activity
  - Demonstrates data exfiltration attempts

## 🔍 What the Demo Shows

The demo demonstrates Project Argus's key capabilities:

1. **Traffic Analysis**: Extracts network flows from PCAP data
2. **AI Detection**: Trains and applies autoencoder model to detect anomalies
3. **Trust Scoring**: Calculates device trust scores (0-100)
4. **Threat Classification**: Color-codes devices by threat level:
   - ✅ TRUSTED (80-100): Normal behavior
   - ⚠️ MONITOR (60-79): Some anomalies detected
   - 🚨 SUSPICIOUS (<60): Critical trust score, needs attention

## 💡 Use Cases

### Learning
Run the demo to understand how:
- Network traffic is analyzed
- ML models detect anomalies
- Trust scores are calculated
- Threats are identified

### Testing
Use `generate_sample_pcap.py` to create custom test scenarios:
```python
# Edit the script to customize traffic patterns
# Then run to generate new PCAP
python3 examples/generate_sample_pcap.py
```

### Development
Use `usage_examples.py` to learn how to:
- Train custom models
- Manage trust scores
- Integrate components

## 📊 Expected Demo Output

When you run `demo.py`, you should see:
- Traffic summary (devices, flows, anomalies)
- Device-by-device analysis with trust scores
- List of suspicious activities
- Recommendations for low-trust devices

The demo typically completes in 30-60 seconds.

## 🛠️ Requirements

The demo requires:
- Python 3.8+
- Dependencies from `requirements.txt`
- No special hardware or network access
- No root privileges

Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Next Steps

After trying the demo:
1. Review the [main README](../README.md) for full installation
2. Check [documentation](../docs/) for detailed guides
3. Explore the [source code](../src/) to understand components
4. Try modifying the demo for your use case
