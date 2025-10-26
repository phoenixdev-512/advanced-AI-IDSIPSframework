#!/bin/bash
# Setup script for Project Argus on Raspberry Pi

set -e

echo "========================================="
echo "Project Argus - Setup Script"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nmap \
    iptables \
    iptables-persistent \
    tcpdump \
    tshark \
    git \
    build-essential \
    libpcap-dev

# Install InfluxDB (optional - can be run on separate server)
read -p "Install InfluxDB on this system? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing InfluxDB..."
    wget -q https://repos.influxdata.com/influxdata-archive_compat.key
    echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
    echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | tee /etc/apt/sources.list.d/influxdata.list
    apt-get update
    apt-get install -y influxdb2
    systemctl enable influxdb
    systemctl start influxdb
    echo "InfluxDB installed. Configure at http://localhost:8086"
fi

# Create project directories
echo "Creating project directories..."
mkdir -p /opt/argus
mkdir -p /opt/argus/data/models
mkdir -p /opt/argus/data/logs
mkdir -p /opt/argus/config

# Copy project files
echo "Copying project files..."
cp -r . /opt/argus/
cd /opt/argus

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit /opt/argus/.env with your configuration"
fi

# Configure network interface for inline mode
read -p "Configure network interface for inline IPS mode? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Network interface configuration:"
    ip link show
    read -p "Enter WAN interface (connected to modem): " WAN_IF
    read -p "Enter LAN interface (connected to router/switch): " LAN_IF
    
    # Enable IP forwarding
    echo "Enabling IP forwarding..."
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    sysctl -p
    
    # Setup NAT
    echo "Setting up NAT..."
    iptables -t nat -A POSTROUTING -o $WAN_IF -j MASQUERADE
    iptables -A FORWARD -i $LAN_IF -o $WAN_IF -j ACCEPT
    iptables -A FORWARD -i $WAN_IF -o $LAN_IF -m state --state RELATED,ESTABLISHED -j ACCEPT
    
    # Save iptables rules
    netfilter-persistent save
    
    echo "Network configured for inline mode"
fi

# Create systemd service files
echo "Creating systemd service files..."

cat > /etc/systemd/system/argus-capture.service <<EOF
[Unit]
Description=Project Argus - Packet Capture
After=network.target influxdb.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/argus
ExecStart=/opt/argus/venv/bin/python3 /opt/argus/main.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/argus-api.service <<EOF
[Unit]
Description=Project Argus - API Server
After=network.target influxdb.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/argus
ExecStart=/opt/argus/venv/bin/python3 /opt/argus/main.py api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/argus-dashboard.service <<EOF
[Unit]
Description=Project Argus - Dashboard
After=network.target argus-api.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/argus
ExecStart=/opt/argus/venv/bin/python3 /opt/argus/main.py dashboard
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure InfluxDB at http://localhost:8086"
echo "2. Update /opt/argus/.env with your settings"
echo "3. Train the model: cd /opt/argus && source venv/bin/activate && python3 train_model.py --synthetic"
echo "4. Enable and start services:"
echo "   systemctl enable argus-capture argus-api argus-dashboard"
echo "   systemctl start argus-capture argus-api argus-dashboard"
echo "5. Access dashboard at http://localhost:8050"
echo ""
echo "To check status: systemctl status argus-*"
echo "To view logs: journalctl -u argus-capture -f"
echo ""
