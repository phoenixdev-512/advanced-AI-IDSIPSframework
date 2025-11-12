# Project Argus - Demo Portal

This directory contains **three demo experiences** for Project Argus that showcase all features.

## 🎯 Quick Start

### Option 1: React Interactive Dashboard (NEW) ⭐

The most modern and interactive experience with advanced animations and glassmorphism design:

```bash
cd demo-react
npm install
npm run dev
# Open http://localhost:3000
```

### Option 2: Direct Browser Access (Simplest)

Just open `index.html` in your web browser to access the demo portal:

```bash
# On Linux/Mac
open index.html

# On Windows
start index.html

# Or manually: Right-click index.html → Open with → Your Browser
```

### Option 3: Using Python Web Server

Run the included server script for the original demos:

```bash
cd demo
python3 serve.py
```

Then open your browser to: http://localhost:8080/

## 🎮 Three Demo Experiences

### 1. **React Interactive Dashboard** (demo-react/) - ⭐ **NEW & RECOMMENDED**

A modern, fully interactive React-based dashboard with:
- **Glassmorphism Design**: Beautiful transparency effects with backdrop blur
- **Advanced Animations**: Powered by Framer Motion for smooth transitions
- **Real-time Charts**: Interactive data visualization using Recharts
- **Dark Theme**: Modern dark interface with animated gradient backgrounds
- **Responsive**: Optimized for desktop, tablet, and mobile
- **Modern Stack**: React 18, React Router, Vite, Lucide icons

**Features:**
- Live updating network traffic charts
- Interactive device cards with hover effects
- Animated trust score meters
- Model training with real-time progress visualization
- Drag-and-drop file upload interface
- Smooth page transitions and micro-interactions

**Requirements:** Node.js 16+

See `demo-react/README.md` for full documentation.

### 2. **Interactive Demo** (demo.html)

A Microsoft Fluent Design-inspired demo with:
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

### 3. **Static Overview** (static.html)

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
├── demo-react/             # NEW: Modern React dashboard
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── pages/         # Dashboard pages
│   │   ├── App.jsx        # Main app component
│   │   └── index.css      # Global styles with glassmorphism
│   ├── package.json
│   ├── vite.config.js
│   └── README.md          # React demo documentation
├── serve.py                # Simple Python HTTP server
├── test_demo.py            # Demo tests
├── README.md               # This file
├── screenshots/            # Dashboard screenshots
└── assets/                 # Placeholder images
```

## 🌟 What's Included

All demos showcase:

- **📊 Dashboard Page**: Real-time monitoring with live trust scores, network statistics, and animated charts
- **🌐 Network Discovery Page**: Automatic device detection with detailed device information
- **💻 Device Details Page**: In-depth analytics for individual devices with traffic patterns
- **⚠️ Alerts & Incidents Page**: Security event management with severity-based filtering
- **⚙️ Admin & Training Page**: ML model configuration, training simulation, and system settings

## 🎨 Design Features

### React Dashboard (NEW)
- **Glassmorphism**: Frosted glass effect with transparency and blur
- **Dark Theme**: Modern dark interface with subtle gradients
- **Smooth Animations**: Framer Motion for fluid page transitions
- **Interactive Charts**: Recharts with live data updates
- **Modern Icons**: Lucide React icon library
- **Advanced Effects**: Hover states, scale transforms, shadow animations

### Original Demos
- **Microsoft Fluent Design System**: Modern, professional UI inspired by Microsoft's design language
- **Fluent Colors**: Blue (#0078D4) primary, with semantic colors for status indicators
- **Fluent Shadows**: Depth-aware shadow system (depth-4, depth-8, depth-16)
- **Smooth Animations**: Page transitions, hover effects, and live data updates
- **Responsive Layout**: Works on desktop, tablet, and mobile devices

## 💻 Installation Requirements

| Demo | Installation | Dependencies |
|------|--------------|--------------|
| React Dashboard | npm install | Node.js 16+ |
| Interactive Demo | None | Modern browser |
| Static Overview | None | Modern browser |

## ✨ Features Comparison

| Feature | Static | Interactive | React Dashboard |
|---------|--------|-------------|-----------------|
| Setup Time | 0 min | 0 min | 2 min |
| Animations | None | Basic | Advanced |
| Interactivity | None | Medium | High |
| Transparency Effects | ❌ | ❌ | ✅ Glassmorphism |
| Charts | Screenshots | SVG | Recharts |
| Modern UI | ✅ | ✅ | ✅✅✅ |
| Live Updates | ❌ | ✅ | ✅✅ |
| Page Routing | ❌ | ❌ | ✅ React Router |

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
- ✅ Modern design (Glassmorphism + Fluent Design)
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
- **UI/UX Showcase**: Demonstrate modern web design techniques

## 🔗 Links

- GitHub Repository: https://github.com/phoenixdev-512/advanced-AI-IDSIPSframework
- Full Documentation: See `/docs` folder in the main repository

## 📝 Technical Details

### React Dashboard
- React 18 with hooks
- React Router for navigation
- Framer Motion for animations
- Recharts for data visualization
- Lucide React for icons
- Vite for fast builds
- CSS3 with glassmorphism effects

### Original Demos
- Pure HTML/CSS/JavaScript
- Custom SVG-based charts
- Microsoft Fluent Design inspired
- No external dependencies

## 📝 License

MIT License - See LICENSE file in the main repository

---

**Note**: These are demos for showcase purposes with simulated data. For full functionality with real network monitoring, install and run the complete Project Argus system following the main README.
