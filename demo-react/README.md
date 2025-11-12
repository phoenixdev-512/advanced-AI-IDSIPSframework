# Project Argus - React Interactive Dashboard

A modern, interactive dashboard built with React for the Project Argus AI-Driven Network Threat Intelligence Platform.

## Features

- 🎨 **Modern UI Design**: Glassmorphism effects with transparency and blur
- 🎭 **Smooth Animations**: Powered by Framer Motion for fluid transitions
- 📊 **Interactive Charts**: Real-time data visualization using Recharts
- 🌓 **Dark Theme**: Beautiful dark mode interface
- 📱 **Responsive**: Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast**: Built with Vite for lightning-fast development and builds

## Tech Stack

- **React 18**: Modern React with hooks
- **React Router**: Client-side routing
- **Framer Motion**: Animation library
- **Recharts**: Charting library
- **Lucide React**: Beautiful icon set
- **Vite**: Next-generation build tool

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the demo-react directory:
```bash
cd demo-react
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and visit:
```
http://localhost:3000
```

### Building for Production

To create a production build:

```bash
npm run build
```

The built files will be in the `dist` directory.

To preview the production build:

```bash
npm run preview
```

## Project Structure

```
demo-react/
├── src/
│   ├── components/          # Reusable components
│   │   ├── Navbar.jsx
│   │   ├── Sidebar.jsx
│   │   └── Card.jsx
│   ├── pages/              # Page components
│   │   ├── Dashboard.jsx
│   │   ├── NetworkDiscovery.jsx
│   │   ├── DeviceDetails.jsx
│   │   ├── Alerts.jsx
│   │   └── Admin.jsx
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── index.html              # HTML template
├── vite.config.js          # Vite configuration
└── package.json            # Dependencies
```

## Features Overview

### Dashboard
- Real-time network statistics
- Interactive traffic charts
- Trust score distribution
- Device monitoring table

### Network Discovery
- Live device scanning
- Device type categorization
- Search and filter functionality
- Interactive device cards with animations

### Device Details
- Comprehensive device information
- Network activity charts
- Port scanning results
- Vulnerability assessment

### Alerts & Incidents
- Security alert monitoring
- Severity-based filtering
- Interactive alert cards
- Status tracking

### Admin & Training
- ML model training interface
- Drag-and-drop file upload
- Real-time training progress
- System settings management

## Customization

### Colors

Edit the CSS variables in `src/index.css` to customize the color scheme:

```css
:root {
  --primary: #3b82f6;
  --secondary: #8b5cf6;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  /* ... */
}
```

### Animation Timing

Adjust animation delays in component files to change the stagger effect timing.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Optimized bundle size
- Code splitting with React Router
- Lazy loading for components
- Efficient re-rendering with React hooks

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see the LICENSE file for details

## Acknowledgments

- Built with modern React best practices
- Inspired by Microsoft Fluent Design and Glassmorphism trends
- Uses simulated data for demonstration purposes

## Support

For issues or questions about the React dashboard, please open an issue on GitHub.

---

**Note**: This is a demo version using simulated data. For production use with real network monitoring, integrate with the Project Argus backend API.
