# Installation Guide

## System Requirements

### Hardware
- Raspberry Pi 4 or 5 (4GB+ RAM recommended)
- MicroSD card (32GB minimum, 64GB recommended)
- Ethernet cable(s)
- For inline mode: USB to Ethernet adapter for second network interface

### Software
- Raspberry Pi OS (64-bit recommended)
- Python 3.8+
- InfluxDB 2.0+
- Root/sudo access

## Quick Start

### Automated Installation

```bash
# Clone repository
git clone https://github.com/phoenixdev-512/advanced-AI-IDSIPSframework.git
cd advanced-AI-IDSIPSframework

# Run setup script
chmod +x scripts/setup.sh
sudo ./scripts/setup.sh

# Configure environment
sudo cp .env.example /opt/argus/.env
sudo nano /opt/argus/.env  # Edit with your settings

# Train model
cd /opt/argus
source venv/bin/activate
python3 train_model.py --synthetic --num-flows 5000

# Start services
sudo systemctl start argus-capture argus-api argus-dashboard

# Access dashboard at http://[PI_IP]:8050
```

For detailed installation instructions, see the full documentation.
