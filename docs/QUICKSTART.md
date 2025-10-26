# Quick Start Guide

Get Project Argus running in under 10 minutes!

## Prerequisites

- Raspberry Pi 4/5 with Raspberry Pi OS installed
- Network connection
- Root/sudo access

## Step-by-Step Setup

### 1. Clone and Install (5 minutes)

```bash
# Clone the repository
git clone https://github.com/phoenixdev-512/advanced-AI-IDSIPSframework.git
cd advanced-AI-IDSIPSframework

# Run automated setup
chmod +x scripts/setup.sh
sudo ./scripts/setup.sh
```

Follow the prompts to:
- Install system dependencies
- Optionally install InfluxDB
- Configure network (if using inline mode)

### 2. Configure (2 minutes)

```bash
# Copy environment template
sudo cp .env.example /opt/argus/.env

# Edit configuration
sudo nano /opt/argus/.env
```

**Minimal configuration:**
```bash
CAPTURE_INTERFACE=eth0  # Your network interface
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-token-from-influxdb-setup
INFLUXDB_ORG=argus
INFLUXDB_BUCKET=network_traffic
```

### 3. Setup InfluxDB (2 minutes)

If you installed InfluxDB locally:

1. Open: `http://[PI_IP]:8086`
2. Create account
3. Create organization: `argus`
4. Create bucket: `network_traffic`
5. Generate API token
6. Copy token to `.env` file

### 4. Train Model (1 minute)

```bash
cd /opt/argus
source venv/bin/activate
python3 train_model.py --synthetic --num-flows 5000
```

This creates an initial model using synthetic data.

### 5. Start Services (30 seconds)

```bash
# Enable auto-start on boot
sudo systemctl enable argus-capture argus-api argus-dashboard

# Start all services
sudo systemctl start argus-capture argus-api argus-dashboard

# Check status
sudo systemctl status argus-*
```

### 6. Access Dashboard (instant!)

Open browser to: `http://[PI_IP]:8050`

You should see:
- Device statistics
- Trust score chart
- Device management table
- Recent alerts

## What's Next?

### Monitor Your Network

The system is now capturing traffic and analyzing devices. Let it run for a few hours to establish baseline behavior.

### Collect Real Training Data

After 24-48 hours of normal network activity:

```bash
cd /opt/argus
source venv/bin/activate
python3 train_model.py --hours 24
sudo systemctl restart argus-capture
```

### Enable IPS (Optional)

For active threat prevention:

```bash
sudo nano /opt/argus/.env
# Set: IPS_ENABLED=true
# Set: AUTO_BLOCK_ENABLED=true

sudo systemctl restart argus-capture
```

⚠️ **Warning:** Test in passive mode first!

### Whitelist Critical Devices

Use the dashboard or API to whitelist:
- Your router
- DNS servers
- Critical infrastructure

### Monitor Alerts

Check the dashboard regularly for:
- Low trust devices
- Vulnerability discoveries
- Blocked IPs

## Troubleshooting

### Services won't start?

```bash
# Check logs
sudo journalctl -u argus-capture -n 50
sudo journalctl -u argus-api -n 50
sudo journalctl -u argus-dashboard -n 50
```

### Can't access dashboard?

```bash
# Check firewall
sudo ufw allow 8050/tcp
sudo ufw allow 8000/tcp

# Check service is running
sudo systemctl status argus-dashboard
```

### No devices showing?

- Wait a few minutes for traffic
- Ensure correct network interface in `.env`
- Check packet capture has root permissions

### Permission errors?

```bash
# Ensure correct ownership
sudo chown -R root:root /opt/argus

# Restart services
sudo systemctl restart argus-*
```

## Common Commands

```bash
# View real-time logs
sudo journalctl -u argus-capture -f

# Restart all services
sudo systemctl restart argus-*

# Stop all services
sudo systemctl stop argus-*

# Check system status
curl http://localhost:8000/api/stats

# List devices
curl http://localhost:8000/api/devices
```

## Next Steps

- Read [API Documentation](API.md)
- Understand [Architecture](ARCHITECTURE.md)
- Review [Installation Guide](INSTALLATION.md)
- Try [Examples](../examples/usage_examples.py)

## Getting Help

- Check logs: `sudo journalctl -u argus-* -f`
- Review configuration: `cat /opt/argus/.env`
- Test components: `python3 examples/usage_examples.py`
- Open GitHub issue for bugs

---

**Congratulations!** 🎉 Project Argus is now protecting your network!
