# Creating and Using the Deployment Package

This guide explains how to create and use the self-contained deployment package for Project Argus.

## For Developers: Creating the Deployment Package

If you're maintaining this project and want to create a deployment package:

### Step 1: Build the Package

Run the build script from the project root:

```bash
./build_deployment.sh
```

This will create a new directory called `argus-deployment/` containing:
- All source code and configuration files
- Launcher scripts for easy execution
- Setup scripts for dependency installation
- Complete documentation
- Data directories for logs and models

### Step 2: Verify the Package

Check that the package was created successfully:

```bash
cd argus-deployment
ls -la
```

You should see:
- `START_HERE.md` - Quick start guide
- `setup.sh` / `setup.bat` - Dependency installation scripts
- `run_argus.sh` / `run_argus.bat` - Main launcher scripts
- `quickstart.sh` / `quickstart.bat` - One-command launch scripts
- All source directories (src/, config/, docs/, etc.)

### Step 3: Test the Package

Test that the setup script works:

```bash
cd argus-deployment
./setup.sh
```

This will create a virtual environment and install all dependencies.

### Step 4: Distribute the Package

You can now distribute the `argus-deployment/` directory:

**Option A: Create a Tarball (Linux/Mac)**
```bash
tar -czf argus-deployment.tar.gz argus-deployment/
```

**Option B: Create a ZIP (All Platforms)**
```bash
zip -r argus-deployment.zip argus-deployment/
```

**Option C: Direct Copy**
Simply copy the entire `argus-deployment/` folder to the target system.

---

## For End Users: Using the Deployment Package

If you received the deployment package as a .tar.gz, .zip, or folder:

### Step 1: Extract (if compressed)

**Linux/Mac (tarball):**
```bash
tar -xzf argus-deployment.tar.gz
cd argus-deployment
```

**All Platforms (zip):**
```bash
unzip argus-deployment.zip
cd argus-deployment
```

**Direct folder:**
```bash
cd argus-deployment
```

### Step 2: Quick Start

The fastest way to get started:

**Linux/Mac:**
```bash
./quickstart.sh
```

**Windows:**
```
quickstart.bat
```

This will:
1. Automatically install all dependencies (first time only)
2. Launch the system with demo traffic
3. Start the dashboard at http://localhost:8050

### Step 3: Read Documentation

Open `START_HERE.md` for comprehensive usage instructions.

---

## Package Contents

The deployment package includes:

### Executables
- `quickstart.sh` / `quickstart.bat` - One-command launch
- `setup.sh` / `setup.bat` - Dependency installation
- `run_argus.sh` / `run_argus.bat` - Main application launcher
- `run_training.sh` / `run_training.bat` - ML model training launcher

### Documentation
- `START_HERE.md` - Quick start guide
- `DEPLOYMENT_README.md` - Comprehensive deployment guide
- `README.md` - Full project documentation
- `docs/` - Detailed feature documentation

### Source Code
- `src/` - Main application code
- `main.py` - Application entry point
- `train_model.py` - Model training script
- `config/` - Configuration files
- `requirements.txt` - Python dependencies

### Support Files
- `.env` - Configuration file (pre-created from .env.example)
- `data/` - Data directories (logs, models, database)
- `examples/` - Usage examples
- `tests/` - Test suite

---

## System Requirements

### Minimum (Demo/Testing)
- Python 3.9+ (will be installed in virtual environment)
- 4GB RAM
- 10GB disk space
- Internet connection (for initial setup only)

### Recommended (Production)
- Raspberry Pi 4/5 with 4GB+ RAM
- Or any Linux/Mac/Windows machine with 8GB+ RAM
- Dual network interfaces (for inline IPS mode)

---

## Key Features of the Deployment Package

1. **Self-Contained**: All dependencies installed in local virtual environment
2. **Cross-Platform**: Works on Linux, macOS, and Windows
3. **No System-Wide Changes**: Everything runs in isolated environment
4. **Easy to Remove**: Just delete the folder
5. **Portable**: Can be copied to any compatible system
6. **No Build Required**: Pre-configured and ready to run

---

## Troubleshooting

### Setup Script Fails

**Problem:** Network errors during dependency installation

**Solution:** 
- Check internet connection
- Try again (sometimes PyPI has temporary issues)
- On slow connections, the setup may take 10-15 minutes

### Can't Execute Scripts (Linux/Mac)

**Problem:** Permission denied when running .sh scripts

**Solution:**
```bash
chmod +x *.sh
```

### Python Not Found

**Problem:** "python3: command not found" or similar

**Solution:**
- Install Python 3.9 or later from python.org
- On Linux: `sudo apt install python3 python3-venv`
- On Mac: `brew install python3`

### Virtual Environment Issues

**Problem:** Scripts can't find the virtual environment

**Solution:**
```bash
rm -rf venv
./setup.sh
```

---

## Advanced Usage

### Custom Configuration

Edit the `.env` file before running to customize:
- Network interface
- Port numbers
- Trust score thresholds
- Auto-blocking behavior

### Running Individual Components

Instead of `full` mode, you can run components separately:

```bash
# API server only
./run_argus.sh api

# Dashboard only
./run_argus.sh dashboard

# Packet capture only
./run_argus.sh start --mode passive
```

### Training Custom Models

Use real network data to train better models:

```bash
# After collecting 24 hours of data
./run_training.sh --model autoencoder --hours 24
```

---

## Support

For issues or questions:
1. Check START_HERE.md and DEPLOYMENT_README.md
2. Review the docs/ folder for detailed guides
3. Visit the GitHub repository for updates

---

## License

MIT License - See LICENSE file for details
