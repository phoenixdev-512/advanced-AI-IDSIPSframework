# Project Argus - Demo Portal

This directory contains **two demo experiences** for Project Argus that showcase all features without requiring Python dependencies or installation.

## 🎯 Quick Start

### Option 1: Direct Browser Access (Simplest)

Just open `index.html` in your web browser to access the demo portal:

```bash
# On Linux/Mac
open index.html

# On Windows
start index.html

# Or manually: Right-click index.html → Open with → Your Browser
```

### Option 2: Using Python Web Server (Recommended)

Run the included server script for the best experience with live updates:

```bash
cd demo
python3 serve.py
```

Then open your browser to: http://localhost:8080/

## 🎮 Two Demo Experiences

### 1. **Interactive Demo** (demo.html) - ⭐ Recommended

A fully interactive, Microsoft Fluent Design-inspired demo with:
- **Live Data Updates**: Real-time simulated network traffic and statistics
- **Multiple Interactive Pages**: Dashboard, Network Discovery, Device Details, Alerts, Admin & Training
- **Working Features**: 
  - Interactive charts showing network traffic patterns
  - Live trust score meters with color-coded indicators
  - Simulated ML model training with real-time progress
  - Drag-and-drop dataset upload interface
  - Sidebar navigation between pages
  - Responsive Microsoft Fluent UI design
- **No External Dependencies**: All charting done with pure SVG/CSS

### 2. **Static Overview** (static.html)

A comprehensive single-page overview with:
- Complete feature descriptions
- Dashboard screenshots
- Technology stack information
- Quick start guides
- Installation instructions

## 📁 Directory Structure

```
demo/
├── index.html              # Demo portal (landing page)
├── demo.html               # Interactive demo with Microsoft Fluent UI
├── static.html             # Static overview page
├── serve.py                # Simple Python HTTP server (no dependencies)
├── test_demo.py            # Demo tests
├── README.md               # This file
├── screenshots/            # Dashboard screenshots
│   ├── main-dashboard.png
│   ├── admin-model-training.png
│   ├── network-discovery.png
│   ├── device-details.png
│   └── alerts-incidents.png
└── assets/                 # Placeholder images
    └── placeholder-*.svg
```

## 🌟 What's Included

The interactive demo showcases:

- **📊 Dashboard Page**: Real-time monitoring with live trust scores, network statistics, and animated charts
- **🌐 Network Discovery Page**: Automatic device detection with detailed device information table
- **💻 Device Details Page**: In-depth analytics for individual devices with traffic patterns
- **⚠️ Alerts & Incidents Page**: Security event management with severity-based filtering
- **⚙️ Admin & Training Page**: ML model configuration, training simulation, and system settings

## 🎨 Design Features

- **Microsoft Fluent Design System**: Modern, professional UI inspired by Microsoft's design language
- **Fluent Colors**: Blue (#0078D4) primary, with semantic colors for status indicators
- **Fluent Shadows**: Depth-aware shadow system (depth-4, depth-8, depth-16)
- **Smooth Animations**: Page transitions, hover effects, and live data updates
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Interactive Elements**: Clickable navigation, buttons, and simulated training

## 💻 No Installation Required

This demo is completely self-contained and works without:
- Python dependencies
- External CDN libraries (all visualization done with native SVG/CSS)
- Database setup
- Network hardware
- Complex configuration

## ✨ Interactive Features

The interactive demo includes:

1. **Real-time Data Simulation**: Network traffic updates every 3 seconds
2. **Live Charts**: SVG-based line and bar charts without external libraries
3. **Trust Score Meters**: Color-coded progress bars (green=high, orange=medium, red=low)
4. **Model Training Simulation**: Click "Start Training" to watch a simulated ML training process
5. **Page Navigation**: Sidebar navigation between all dashboard pages
6. **Responsive Tables**: Device lists, alert tables, and network discovery results
7. **Interactive Cards**: Hover effects and smooth transitions

## 🚀 Next Steps

After viewing the demo, if you want to run the full interactive dashboard:

1. **See the main README**: Go back to the root directory and read `README.md`
2. **Quick Start Guide**: Follow `docs/QUICK_START_GUIDE.md`
3. **Deployment Guide**: Read `DEPLOYMENT_GUIDE.md` for full setup

## 📖 Features Demonstrated

### Core Features
- ✅ AI-Powered Anomaly Detection with ML model training
- ✅ Dynamic Trust Scoring (0-100 scale with color indicators)
- ✅ Active Intrusion Prevention (auto-block capabilities)
- ✅ Vulnerability Scanning (open port detection)
- ✅ Real-time Dashboard with live updates

### Pages & Functionality
- ✅ **Dashboard**: Network overview, statistics, charts
- ✅ **Network Discovery**: Device scanning and categorization
- ✅ **Device Details**: Individual device analytics
- ✅ **Alerts & Incidents**: Security event monitoring
- ✅ **Admin & Training**: ML model training interface

### UI/UX Features
- ✅ Microsoft Fluent Design System
- ✅ Responsive layout (mobile, tablet, desktop)
- ✅ Smooth animations and transitions
- ✅ Interactive charts and visualizations
- ✅ Color-coded trust scores and alerts
- ✅ Professional, modern interface

## 🎯 Use Cases

Perfect for:
- **Project Demonstrations**: Show stakeholders what Project Argus can do
- **Educational Purposes**: Learn about network security concepts
- **Feature Preview**: Evaluate before installing the full system
- **Documentation**: Visual reference for the dashboard UI

## 🔗 Links

- GitHub Repository: https://github.com/phoenixdev-512/advanced-AI-IDSIPSframework
- Full Documentation: See `/docs` folder in the main repository

## 🖼️ Screenshots

The demo includes screenshots of all major features in the `screenshots/` directory.

## 📝 Technical Details

- **No External Dependencies**: Pure HTML/CSS/JavaScript
- **Chart Library**: Custom SVG-based charts (no Chart.js or other libraries needed)
- **Design System**: Microsoft Fluent Design inspired
- **Browser Compatibility**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **File Size**: ~50KB for the interactive demo HTML

## 📝 License

MIT License - See LICENSE file in the main repository

---

**Note**: This is a demo for showcase purposes with simulated data. For full functionality with real network monitoring, install and run the complete Project Argus system following the main README.
