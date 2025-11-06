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

# Create quick start script for Linux/Mac
cat > "$DEPLOYMENT_DIR/quickstart.sh" << 'EOF'
#!/bin/bash
###############################################################################
# Project Argus - Quick Start Script
# 
# This script automates the entire setup and launch process for first-time users
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Project Argus - Quick Start"
echo "=================================================="
echo ""

# Check if setup has been run
if [ ! -d "venv" ]; then
    echo "First-time setup detected. Installing dependencies..."
    echo "This may take several minutes..."
    echo ""
    
    ./setup.sh
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "Setup failed. Please check the error messages above."
        exit 1
    fi
fi

echo ""
echo "Starting Project Argus in demo mode..."
echo ""
echo "The system will run with simulated traffic for demonstration."
echo "Access the dashboard at: http://localhost:8050"
echo ""
echo "Press Ctrl+C to stop the system."
echo ""

# Give user a moment to read
sleep 3

# Run with simulated traffic (no root required)
./run_argus.sh full --mode passive
EOF

chmod +x "$DEPLOYMENT_DIR/quickstart.sh"

# Create Windows quick start batch file
cat > "$DEPLOYMENT_DIR/quickstart.bat" << 'EOF'
@echo off
REM Project Argus - Quick Start Script (Windows)

cd /d "%~dp0"

echo ==================================================
echo Project Argus - Quick Start
echo ==================================================
echo.

REM Check if setup has been run
if not exist "venv" (
    echo First-time setup detected. Installing dependencies...
    echo This may take several minutes...
    echo.
    
    call setup.bat
    
    if errorlevel 1 (
        echo.
        echo Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

echo.
echo Starting Project Argus in demo mode...
echo.
echo The system will run with simulated traffic for demonstration.
echo Access the dashboard at: http://localhost:8050
echo.
echo Press Ctrl+C to stop the system.
echo.

REM Give user a moment to read
timeout /t 3 /nobreak >nul

REM Run with simulated traffic (no admin required)
call run_argus.bat full --mode passive
EOF

# Create START_HERE documentation
cat > "$DEPLOYMENT_DIR/START_HERE.md" << 'EOF'
# 🚀 START HERE - Project Argus Deployment Package

Welcome to Project Argus! This is a **self-contained deployment package** that includes everything you need to run the AI-driven Network Intrusion Detection/Prevention System.

## ⚡ Fastest Way to Get Started

### Linux/Mac Users:
```bash
./quickstart.sh
```

### Windows Users:
```
quickstart.bat
```

This single command will:
1. Install all dependencies (first time only)
2. Launch the full system with demo traffic
3. Open the dashboard at http://localhost:8050

**That's it!** No complex setup required.

---

## 📦 What's Included

This deployment package contains:
- ✅ Complete source code
- ✅ All configuration files
- ✅ Launch scripts for easy execution
- ✅ Documentation and examples
- ✅ Setup scripts for dependency installation
- ✅ Support for Windows, Linux, and macOS

---

## 🎯 Three Ways to Use This Package

### 1. Quick Demo (Recommended for First Time)

Run with simulated traffic to see how it works:

**Linux/Mac:**
```bash
./quickstart.sh
```

**Windows:**
```
quickstart.bat
```

Then open your browser to: **http://localhost:8050**

### 2. Manual Setup and Launch

If you prefer step-by-step control:

**Step 1: Install Dependencies (First Time Only)**
```bash
./setup.sh          # Linux/Mac
setup.bat           # Windows
```

**Step 2: Launch the System**
```bash
./run_argus.sh full --mode passive    # Linux/Mac
run_argus.bat full --mode passive     # Windows
```

**Step 3: Access Dashboard**
- Open browser to http://localhost:8050

### 3. Production Deployment on Raspberry Pi

For real network monitoring:

1. Copy this entire folder to your Raspberry Pi
2. Run `./setup.sh` to install dependencies
3. Edit `.env` file to configure your network interface
4. Run `sudo ./run_argus.sh full --mode passive` (requires root for packet capture)

---

## 📚 Documentation

- **START_HERE.md** (this file) - Quick start guide
- **DEPLOYMENT_README.md** - Comprehensive deployment guide
- **README.md** - Full project documentation
- **docs/** - Detailed documentation on all features

---

## 🔧 System Requirements

### Minimum (for Demo/Testing):
- Python 3.9+ (no need to install - included in virtual environment)
- 4GB RAM
- 10GB free disk space
- Internet connection (for initial setup only)

### Recommended (for Production):
- Raspberry Pi 4/5 with 4GB+ RAM
- Or any Linux/Mac/Windows machine with 8GB+ RAM
- Dual network interfaces (for inline IPS mode)

---

## 🎮 What You Can Do

Once running, you can:

1. **View Dashboard** - http://localhost:8050
   - See real-time network traffic
   - Monitor device trust scores
   - View security alerts

2. **Access API** - http://localhost:8000
   - Programmatic access to all features
   - REST API for integrations

3. **Train AI Model** - Customize detection
   ```bash
   ./run_training.sh --synthetic --num-flows 5000
   ```

---

## ⚙️ Configuration

Edit the `.env` file to customize:
- Network interface to monitor
- Trust score thresholds
- Auto-blocking behavior
- API and dashboard ports

---

## 🆘 Troubleshooting

### Setup Fails with Network Errors
**Problem:** Can't download Python packages
**Solution:** Check internet connection and try again. The setup script downloads dependencies from PyPI.

### Can't Capture Packets
**Problem:** Permission denied when starting capture
**Solution:** Run with elevated privileges:
- Linux/Mac: `sudo ./run_argus.sh start --mode passive`
- Windows: Run Command Prompt as Administrator

### Port Already in Use
**Problem:** Port 8000 or 8050 already in use
**Solution:** Use custom ports:
```bash
./run_argus.sh full --api-port 8001 --dashboard-port 8051
```

### Virtual Environment Issues
**Problem:** Commands fail or dependencies missing
**Solution:** Recreate the virtual environment:
```bash
rm -rf venv
./setup.sh
```

---

## 🔐 Security Notes

1. **Default Configuration**: The system runs in passive mode (IDS) by default, which is safe and doesn't modify network traffic.

2. **Dashboard Access**: By default, the dashboard is accessible on all network interfaces (0.0.0.0). For production, configure your firewall to restrict access.

3. **Root Privileges**: Packet capture requires root/admin privileges. Demo mode works without special privileges.

---

## 📖 Next Steps

After getting the system running:

1. **Explore the Dashboard** - Familiarize yourself with the interface
2. **Review Documentation** - Read DEPLOYMENT_README.md for details
3. **Customize Configuration** - Edit .env for your environment
4. **Train Your Model** - Use real network data for better detection
5. **Deploy to Production** - Move to Raspberry Pi for real monitoring

---

## 💡 Key Features

- 🤖 **AI-Powered Detection** - Autoencoder neural network for anomaly detection
- 📊 **Dynamic Trust Scores** - Rates all network devices (0-100 scale)
- 🚫 **Active Prevention** - Can automatically block suspicious devices
- 🔍 **Vulnerability Scanning** - Identifies security weaknesses
- 📈 **Real-time Dashboard** - Beautiful web interface for monitoring
- 🔒 **Privacy-First** - All data stays on your device

---

## 🤝 Support

Need help?
- Check DEPLOYMENT_README.md for detailed documentation
- Review the docs/ folder for specific guides
- Visit the GitHub repository for issues and updates

---

## 📄 License

MIT License - See LICENSE file for details

---

**🎉 Thank you for choosing Project Argus! Let's make your network more secure.**
EOF

# Create package verification script
cat > "$DEPLOYMENT_DIR/verify_package.py" << 'EOF'
#!/usr/bin/env python3
"""
Deployment Package Verification Script

This script verifies that the deployment package is complete and ready to use.
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING")
        return False

def check_directory(path, description):
    """Check if a directory exists"""
    if Path(path).is_dir():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("Project Argus - Deployment Package Verification")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check launcher scripts
    print("Checking Launcher Scripts...")
    all_ok &= check_file("quickstart.sh", "Quick start script (Linux/Mac)")
    all_ok &= check_file("quickstart.bat", "Quick start script (Windows)")
    all_ok &= check_file("run_argus.sh", "Main launcher (Linux/Mac)")
    all_ok &= check_file("run_argus.bat", "Main launcher (Windows)")
    all_ok &= check_file("run_training.sh", "Training launcher (Linux/Mac)")
    all_ok &= check_file("run_training.bat", "Training launcher (Windows)")
    all_ok &= check_file("setup.sh", "Setup script (Linux/Mac)")
    all_ok &= check_file("setup.bat", "Setup script (Windows)")
    print()
    
    # Check main files
    print("Checking Main Files...")
    all_ok &= check_file("main.py", "Main application file")
    all_ok &= check_file("train_model.py", "Model training script")
    all_ok &= check_file("requirements.txt", "Python dependencies")
    all_ok &= check_file(".env", "Configuration file")
    print()
    
    # Check documentation
    print("Checking Documentation...")
    all_ok &= check_file("START_HERE.md", "Quick start guide")
    all_ok &= check_file("DEPLOYMENT_README.md", "Deployment documentation")
    all_ok &= check_file("README.md", "Main documentation")
    all_ok &= check_file("LICENSE", "License file")
    print()
    
    # Check directories
    print("Checking Directories...")
    all_ok &= check_directory("src", "Source code directory")
    all_ok &= check_directory("config", "Configuration directory")
    all_ok &= check_directory("docs", "Documentation directory")
    all_ok &= check_directory("data", "Data directory")
    all_ok &= check_directory("data/logs", "Logs directory")
    all_ok &= check_directory("data/models", "Models directory")
    all_ok &= check_directory("examples", "Examples directory")
    all_ok &= check_directory("tests", "Tests directory")
    print()
    
    # Check critical source files
    print("Checking Critical Source Files...")
    all_ok &= check_file("src/__init__.py", "Source package init")
    all_ok &= check_file("src/config.py", "Configuration module")
    all_ok &= check_directory("src/api", "API module")
    all_ok &= check_directory("src/capture", "Capture module")
    all_ok &= check_directory("src/dashboard", "Dashboard module")
    all_ok &= check_directory("src/models", "Models module")
    all_ok &= check_directory("src/scoring", "Scoring module")
    all_ok &= check_directory("src/ips", "IPS module")
    print()
    
    # Check Python version
    print("Checking Python Version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (compatible)")
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)")
        all_ok = False
    print()
    
    # Check virtual environment
    print("Checking Virtual Environment...")
    if Path("venv").exists():
        print("✓ Virtual environment found")
        print("  (Dependencies already installed)")
    else:
        print("⚠ Virtual environment not found")
        print("  (Run setup.sh or setup.bat to install dependencies)")
    print()
    
    # Final result
    print("=" * 60)
    if all_ok:
        print("✓ VERIFICATION COMPLETE - Package is ready to use!")
        print()
        print("Next steps:")
        print("  1. If virtual environment not found, run:")
        print("     Linux/Mac: ./setup.sh")
        print("     Windows:   setup.bat")
        print()
        print("  2. Launch the system:")
        print("     Linux/Mac: ./quickstart.sh")
        print("     Windows:   quickstart.bat")
    else:
        print("✗ VERIFICATION FAILED - Package is incomplete!")
        print()
        print("Some required files or directories are missing.")
        print("Please re-extract the deployment package or run build_deployment.sh")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x "$DEPLOYMENT_DIR/verify_package.py"

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
