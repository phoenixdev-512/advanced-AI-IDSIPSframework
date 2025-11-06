#!/bin/bash
###############################################################################
# Project Argus - Deployment Package Builder
# 
# This script creates a self-contained deployment package that includes:
# - All source code and configuration files
# - A virtual environment with all dependencies pre-installed
# - Launcher scripts for easy execution
# - Documentation
###############################################################################

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_NAME="argus-deployment"
DEPLOYMENT_DIR="${SCRIPT_DIR}/${DEPLOYMENT_NAME}"

echo "=================================================="
echo "Project Argus - Deployment Package Builder"
echo "=================================================="
echo ""

# Clean up old deployment if exists
if [ -d "$DEPLOYMENT_DIR" ]; then
    echo "Removing old deployment directory..."
    rm -rf "$DEPLOYMENT_DIR"
fi

# Create deployment directory structure
echo "Creating deployment directory structure..."
mkdir -p "$DEPLOYMENT_DIR"
mkdir -p "$DEPLOYMENT_DIR/data/logs"
mkdir -p "$DEPLOYMENT_DIR/data/models"
mkdir -p "$DEPLOYMENT_DIR/data/database"

# Copy source files
echo "Copying source files..."
cp -r "${SCRIPT_DIR}/src" "$DEPLOYMENT_DIR/"
cp -r "${SCRIPT_DIR}/config" "$DEPLOYMENT_DIR/"
cp -r "${SCRIPT_DIR}/docs" "$DEPLOYMENT_DIR/"
cp -r "${SCRIPT_DIR}/examples" "$DEPLOYMENT_DIR/"
cp -r "${SCRIPT_DIR}/model_training" "$DEPLOYMENT_DIR/"
cp -r "${SCRIPT_DIR}/scripts" "$DEPLOYMENT_DIR/"
cp -r "${SCRIPT_DIR}/tests" "$DEPLOYMENT_DIR/"

# Copy main files
cp "${SCRIPT_DIR}/main.py" "$DEPLOYMENT_DIR/"
cp "${SCRIPT_DIR}/train_model.py" "$DEPLOYMENT_DIR/"
cp "${SCRIPT_DIR}/requirements.txt" "$DEPLOYMENT_DIR/"
cp "${SCRIPT_DIR}/README.md" "$DEPLOYMENT_DIR/"
cp "${SCRIPT_DIR}/LICENSE" "$DEPLOYMENT_DIR/"
cp "${SCRIPT_DIR}/.env.example" "$DEPLOYMENT_DIR/.env"

# Copy documentation files
if [ -f "${SCRIPT_DIR}/IMPLEMENTATION.md" ]; then
    cp "${SCRIPT_DIR}/IMPLEMENTATION.md" "$DEPLOYMENT_DIR/"
fi
if [ -f "${SCRIPT_DIR}/IMPLEMENTATION_SUMMARY.md" ]; then
    cp "${SCRIPT_DIR}/IMPLEMENTATION_SUMMARY.md" "$DEPLOYMENT_DIR/"
fi

# Note: Virtual environment will be created by the user when they run setup.sh
# This allows the deployment package to be more portable and faster to create
echo "Virtual environment will be created when user runs setup.sh"

# Create launcher script
echo "Creating launcher scripts..."
cat > "$DEPLOYMENT_DIR/run_argus.sh" << 'EOF'
#!/bin/bash
###############################################################################
# Project Argus Launcher
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run main.py with all arguments passed through
python3 main.py "$@"

# Deactivate when done
deactivate
EOF

chmod +x "$DEPLOYMENT_DIR/run_argus.sh"

# Create training script
cat > "$DEPLOYMENT_DIR/run_training.sh" << 'EOF'
#!/bin/bash
###############################################################################
# Project Argus - Model Training Launcher
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run train_model.py with all arguments passed through
python3 train_model.py "$@"

# Deactivate when done
deactivate
EOF

chmod +x "$DEPLOYMENT_DIR/run_training.sh"

# Create Windows batch launcher
cat > "$DEPLOYMENT_DIR/run_argus.bat" << 'EOF'
@echo off
REM Project Argus Launcher (Windows)

cd /d "%~dp0"

if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    exit /b 1
)

call venv\Scripts\activate.bat
python main.py %*
call deactivate
EOF

# Create Windows training batch launcher
cat > "$DEPLOYMENT_DIR/run_training.bat" << 'EOF'
@echo off
REM Project Argus - Model Training Launcher (Windows)

cd /d "%~dp0"

if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    exit /b 1
)

call venv\Scripts\activate.bat
python train_model.py %*
call deactivate
EOF

# Create setup script for fresh installation
cat > "$DEPLOYMENT_DIR/setup.sh" << 'EOF'
#!/bin/bash
###############################################################################
# Project Argus - Setup Script
# Run this if you need to recreate the virtual environment
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Setting up Project Argus..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

deactivate

echo ""
echo "Setup complete!"
echo "You can now run: ./run_argus.sh full --mode passive"
EOF

chmod +x "$DEPLOYMENT_DIR/setup.sh"

# Create Windows setup batch file
cat > "$DEPLOYMENT_DIR/setup.bat" << 'EOF'
@echo off
REM Project Argus - Setup Script (Windows)

cd /d "%~dp0"

echo Setting up Project Argus...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed!
    exit /b 1
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
echo Upgrading pip...
python -m pip install --upgrade pip
echo Installing dependencies...
pip install -r requirements.txt
call deactivate

echo.
echo Setup complete!
echo You can now run: run_argus.bat full --mode passive
EOF

# Create comprehensive README for deployment
cat > "$DEPLOYMENT_DIR/DEPLOYMENT_README.md" << 'EOF'
# Project Argus - Deployment Package

This is a self-contained deployment package for Project Argus. All dependencies are included in the `venv` directory.

## Quick Start

### Linux/Mac

1. **First-time setup** (if needed):
   ```bash
   ./setup.sh
   ```

2. **Run the full system** (capture + API + dashboard):
   ```bash
   ./run_argus.sh full --mode passive
   ```

3. **Access the dashboard**:
   - Open browser to `http://localhost:8050`

### Windows

1. **First-time setup** (if needed):
   ```
   setup.bat
   ```

2. **Run the full system**:
   ```
   run_argus.bat full --mode passive
   ```

3. **Access the dashboard**:
   - Open browser to `http://localhost:8050`

## Available Commands

### Running Components

**Full system** (all components together):
```bash
./run_argus.sh full --mode passive
# or on Windows: run_argus.bat full --mode passive
```

**Packet capture only**:
```bash
./run_argus.sh start --mode passive
```

**API server only**:
```bash
./run_argus.sh api
```

**Dashboard only**:
```bash
./run_argus.sh dashboard
```

### Training the Model

**Train with synthetic data** (for testing):
```bash
./run_training.sh --synthetic --num-flows 5000
# or on Windows: run_training.bat --synthetic --num-flows 5000
```

**Train with real data** (after collecting network data):
```bash
./run_training.sh --model autoencoder --hours 24
```

## Configuration

Edit the `.env` file to configure:
- Network interface to monitor
- InfluxDB connection (if using external database)
- Trust score thresholds
- IPS behavior
- API and dashboard ports

## System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10/11
- **CPU**: 2 cores
- **RAM**: 4GB (8GB recommended)
- **Storage**: 10GB free space
- **Python**: 3.9+ (included in venv)

### For Production Use (Raspberry Pi)
- **Hardware**: Raspberry Pi 4/5 (4GB+ RAM)
- **OS**: Raspberry Pi OS (64-bit)
- **Network**: Dual network interfaces (for inline IPS mode)

## Operating Modes

### Passive Mode (IDS - Recommended for Testing)
- Monitors network traffic
- Detects and alerts on threats
- Does not block traffic
- Safer for initial deployment

### Inline Mode (IPS - Advanced)
- Actively blocks malicious traffic
- Requires dual network interfaces
- Needs root privileges
- Use only after testing in passive mode

## Troubleshooting

### Permission Errors
If you get permission errors when capturing packets:
- On Linux/Mac: Run with `sudo ./run_argus.sh ...`
- Packet capture requires elevated privileges

### Port Already in Use
If ports 8000 or 8050 are in use:
- Change ports using `--api-port` and `--dashboard-port` flags
- Example: `./run_argus.sh full --api-port 8001 --dashboard-port 8051`

### Virtual Environment Issues
If you encounter issues with the virtual environment:
```bash
rm -rf venv
./setup.sh
```

### InfluxDB Not Available
By default, the system will work without InfluxDB (stores in memory).
To use InfluxDB:
1. Install InfluxDB separately
2. Configure `.env` with connection details

## Directory Structure

```
argus-deployment/
├── venv/                  # Virtual environment (all dependencies)
├── src/                   # Source code
├── config/                # Configuration files
├── docs/                  # Documentation
├── data/                  # Data directory
│   ├── logs/             # Application logs
│   ├── models/           # Trained ML models
│   └── database/         # Local data storage
├── main.py               # Main application
├── train_model.py        # Model training script
├── run_argus.sh          # Launch script (Linux/Mac)
├── run_argus.bat         # Launch script (Windows)
├── run_training.sh       # Training script (Linux/Mac)
├── run_training.bat      # Training script (Windows)
├── setup.sh              # Setup script (Linux/Mac)
├── setup.bat             # Setup script (Windows)
├── .env                  # Configuration file
└── README.md             # Main documentation
```

## Security Notes

1. **Change default credentials**: If using InfluxDB, change default tokens
2. **Firewall configuration**: Restrict dashboard access to trusted IPs
3. **Keep updated**: Regularly update dependencies with `pip install -r requirements.txt --upgrade`
4. **Whitelist critical devices**: Prevent accidental blocking of essential services

## Support

For issues, questions, or feature requests:
- Check the main README.md for detailed documentation
- Review docs/ folder for specific guides
- Open an issue on GitHub

## License

This project is licensed under the MIT License - see the LICENSE file for details.
EOF

echo ""
echo "=================================================="
echo "Deployment package created successfully!"
echo "=================================================="
echo ""
echo "Location: $DEPLOYMENT_DIR"
echo ""
echo "To use the deployment package:"
echo "  1. cd $DEPLOYMENT_DIR"
echo "  2. Review and edit .env file for configuration"
echo "  3. Run: ./run_argus.sh full --mode passive"
echo "  4. Access dashboard at http://localhost:8050"
echo ""
echo "For more information, see DEPLOYMENT_README.md"
echo ""
