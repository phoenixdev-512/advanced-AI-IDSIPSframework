# Developer Guide: Local Testing for New Features

This guide provides step-by-step instructions for developers to clone the repository, set up the environment, and test the new Admin & Model Training page and Live Network Discovery features locally.

## Prerequisites

Before you begin, ensure you have the following software installed on your system:

- **Git**: Version control system to clone the repository
- **Python 3.8+**: Python programming language (Python 3.8 or higher recommended)
- **venv**: Python virtual environment module (usually included with Python)
- **InfluxDB** (Optional): For storing network flow data (can be skipped for basic testing with simulated mode)

## Step 1: Clone the Repository

Open a terminal and run the following command to clone the Project Argus repository:

```bash
git clone https://github.com/phoenixdev-512/advanced-AI-IDSIPSframework.git
cd advanced-AI-IDSIPSframework
```

## Step 2: Check Out the Feature Branch

Switch to the specific branch that contains the new Admin & Model Training page and Live Network Discovery features:

```bash
git checkout copilot/add-admin-model-training-page
```

## Step 3: Set Up the Python Virtual Environment

Create and activate a Python virtual environment to isolate the project dependencies:

### On Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your command prompt, indicating the virtual environment is active.

## Step 4: Install Dependencies

Install all required Python packages using the requirements file:

```bash
pip install -r requirements.txt
```

This may take a few minutes as it downloads and installs all necessary dependencies including TensorFlow, Dash, FastAPI, and other libraries.

## Step 5: Configure the Environment

Copy the example environment configuration file and customize it as needed:

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred text editor. For basic local testing, you can use the default values. Key configurations include:

- **INFLUXDB_URL**: Set to `http://localhost:8086` if you have InfluxDB running locally, or leave as-is
- **INFLUXDB_TOKEN**: Your InfluxDB authentication token (can be a placeholder for simulated mode)
- **CAPTURE_INTERFACE**: Network interface to monitor (e.g., `eth0`, `wlan0`, or use `simulated` for demo data)

**Note**: For initial testing without InfluxDB, the application can run in simulated mode which generates synthetic network traffic.

## Step 6: Create Required Directories

Ensure the necessary data directories exist:

```bash
mkdir -p data/logs data/models model_training/data/raw model_training/trained_models
```

## Step 7: Run the Application

Start the full Project Argus application (API server + Dashboard) in simulated mode:

```bash
python main.py full --mode passive
```

Or, to specifically use simulated traffic for demonstration:

```bash
python main.py full
```

You should see output indicating that:
- The API server is starting on `http://localhost:8000`
- The Dashboard is starting on `http://localhost:8050`
- Packet capture is running (in simulated or passive mode)

## Step 8: View the New Features

Open your web browser and navigate to the following URLs:

### Main Dashboard with Live Network Discovery
Navigate to:
```
http://localhost:8050
```

On this page, you should see:
- The existing dashboard with device statistics, trust scores, and alerts
- **New**: A "Live Network Discovery" card with a "Scan Network for Devices 📡" button
- Click the scan button to discover devices on your local network (or simulated devices in demo mode)
- The results will display in a table showing IP Address, MAC Address, and Manufacturer

### Admin & Model Training Page
Navigate to:
```
http://localhost:8050/admin
```

On this page, you should see:
- **Train New Anomaly Detection Model** card with:
  - Drag & drop file upload area for datasets (.csv, .parquet, .pkl)
  - Model type selection (Autoencoder / Isolation Forest)
  - Training parameters configuration
  - Validation & test options
  - "Start Training 🚀" button
- **Training History** card showing past training runs
- **Current Model Status** card showing the active model details
- Light/Dark mode toggle (should work on this page as well)

### API Documentation
You can also view the auto-generated API documentation:
```
http://localhost:8000/docs
```

This provides an interactive interface to test all API endpoints, including the new:
- `POST /api/train/upload_dataset` - Upload training datasets
- `POST /api/train/start` - Start model training
- `GET /api/train/history` - Get training history
- `POST /api/model/activate` - Activate a trained model
- `POST /api/network/discover` - Discover network devices

## Step 9: Testing the Features

### Testing Live Network Discovery
1. On the main dashboard (`http://localhost:8050`), scroll to the Live Network Discovery card
2. Click the "Scan Network for Devices 📡" button
3. Wait for the scan to complete (this may take 30-60 seconds depending on your network)
4. View the discovered devices in the results table

### Testing Admin & Model Training
1. Navigate to the Admin page (`http://localhost:8050/admin`)
2. In the "Train New Anomaly Detection Model" card:
   - Drag and drop a CSV file with network flow data, or click to select a file
   - Select a model type (e.g., "Autoencoder")
   - Configure training parameters
   - Click "Start Training 🚀"
3. Monitor the training progress (the button will show "Training in Progress...")
4. Once training completes, check the "Training History" card for the new entry
5. Select a trained model from the history and click "Activate Selected Model"

### Testing Theme Toggle
1. On any page (main dashboard or admin page)
2. Click the "🌞 Light Mode" or "🌙 Dark Mode" button
3. Verify the theme changes correctly across all components

## Troubleshooting

### Port Already in Use
If you see an error about port 8000 or 8050 being in use:
```bash
# Find and kill the process using the port (Linux/macOS)
lsof -ti:8000 | xargs kill -9
lsof -ti:8050 | xargs kill -9

# Or change the ports when starting
python main.py full --api-port 8001 --dashboard-port 8051
```

### Missing Dependencies
If you encounter import errors:
```bash
pip install --upgrade -r requirements.txt
```

### Permission Issues (Linux/macOS)
If you get permission errors when running network scans:
```bash
sudo python main.py full
```
**Note**: Running with sudo may be required for actual network interface capture, but simulated mode doesn't require it.

### InfluxDB Connection Errors
If InfluxDB is not installed or running, the application will log warnings but should still function for most features. To install InfluxDB:
- Follow the official guide: https://docs.influxdata.com/influxdb/v2.0/install/

## Stopping the Application

To stop the application:
1. Press `Ctrl+C` in the terminal where the application is running
2. Wait for graceful shutdown
3. If needed, press `Ctrl+C` again to force stop

## Next Steps

After successfully running the application locally:
- Explore the codebase in the `src/` directory
- Review the API implementation in `src/api/main.py`
- Check the dashboard implementation in `src/dashboard/main.py`
- Review training scripts in `model_training/`
- Run tests with `pytest tests/`

## Additional Resources

- **Main README**: See `README.md` for overall project documentation
- **API Documentation**: See `docs/API.md` for API details
- **Architecture**: See `docs/ARCHITECTURE.md` for system architecture
- **Quick Start**: See `docs/QUICK_START_GUIDE.md` for quick setup

## Support

If you encounter any issues:
1. Check the logs in `data/logs/argus.log`
2. Review the console output for error messages
3. Open an issue on GitHub with detailed error information
