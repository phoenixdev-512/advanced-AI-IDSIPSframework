import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { StatCard } from '../components/Card'
import { Search, Wifi, Laptop, Smartphone } from 'lucide-react'
import './NetworkDiscovery.css'

const NetworkDiscovery = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [devices, setDevices] = useState([])

  useEffect(() => {
    const deviceList = [
      { name: 'Desktop-PC-01', ip: '192.168.1.105', mac: 'AA:BB:CC:DD:EE:FF', type: 'Computer', status: 'online', trust: 85 },
      { name: 'Laptop-Work', ip: '192.168.1.112', mac: 'BB:CC:DD:EE:FF:AA', type: 'Computer', status: 'online', trust: 92 },
      { name: 'iPhone-Personal', ip: '192.168.1.156', mac: 'CC:DD:EE:FF:AA:BB', type: 'Mobile', status: 'online', trust: 88 },
      { name: 'Smart-TV-Living', ip: '192.168.1.203', mac: 'DD:EE:FF:AA:BB:CC', type: 'IoT', status: 'online', trust: 76 },
      { name: 'Security-Camera-01', ip: '192.168.1.221', mac: 'EE:FF:AA:BB:CC:DD', type: 'IoT', status: 'online', trust: 45 },
      { name: 'Alexa-Echo', ip: '192.168.1.198', mac: 'FF:AA:BB:CC:DD:EE', type: 'IoT', status: 'online', trust: 71 },
      { name: 'MacBook-Pro', ip: '192.168.1.134', mac: 'AA:CC:EE:BB:DD:FF', type: 'Computer', status: 'online', trust: 95 },
      { name: 'iPad-Air', ip: '192.168.1.167', mac: 'BB:DD:FF:CC:EE:AA', type: 'Mobile', status: 'online', trust: 90 }
    ]
    setDevices(deviceList)
  }, [])

  const filteredDevices = devices.filter(device =>
    device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    device.ip.includes(searchTerm) ||
    device.type.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const stats = {
    total: devices.length,
    computers: devices.filter(d => d.type === 'Computer').length,
    iot: devices.filter(d => d.type === 'IoT').length,
    mobile: devices.filter(d => d.type === 'Mobile').length
  }

  return (
    <motion.div
      className="network-discovery"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="page-header">
        <h1 className="page-title">Network Discovery</h1>
        <p className="page-subtitle">Live detection and monitoring of all network devices</p>
      </div>

      <div className="alert-banner glass success">
        <div className="alert-icon">✅</div>
        <div>
          <strong>Scan Complete:</strong> Found {devices.length} devices on your network
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={Wifi}
          title="Scan Status"
          value="Active"
          label="Last scan: Just now"
          color="success"
          delay={0.1}
        />
        <StatCard
          icon={Laptop}
          title="Computers"
          value={stats.computers}
          label="Desktop & Laptop devices"
          color="primary"
          delay={0.2}
        />
        <StatCard
          icon={Smartphone}
          title="Mobile Devices"
          value={stats.mobile}
          label="Phones & Tablets"
          color="info"
          delay={0.3}
        />
        <StatCard
          icon={Wifi}
          title="IoT Devices"
          value={stats.iot}
          label="Smart home & cameras"
          color="warning"
          delay={0.4}
        />
      </div>

      <motion.div 
        className="search-container glass"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Search className="search-icon" size={20} />
        <input
          type="text"
          className="search-input"
          placeholder="Search devices by name, IP, or type..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </motion.div>

      <motion.div 
        className="devices-grid"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        {filteredDevices.map((device, index) => (
          <motion.div
            key={device.ip}
            className="device-card glass"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7 + index * 0.05 }}
            whileHover={{ y: -8, boxShadow: '0 20px 40px -5px rgba(0, 0, 0, 0.3)' }}
          >
            <div className="device-header">
              <div className="device-icon">
                {device.type === 'Computer' ? '💻' : device.type === 'Mobile' ? '📱' : '🔌'}
              </div>
              <span className={`status-indicator status-${device.status}`}></span>
            </div>
            <h3 className="device-name">{device.name}</h3>
            <div className="device-details">
              <div className="detail-row">
                <span className="detail-label">IP:</span>
                <span className="detail-value">{device.ip}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">MAC:</span>
                <span className="detail-value">{device.mac}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Type:</span>
                <span className="device-type-badge">{device.type}</span>
              </div>
            </div>
            <div className="device-trust">
              <div className="trust-label">Trust Score</div>
              <div className="trust-bar">
                <div 
                  className={`trust-fill ${
                    device.trust >= 70 ? 'high' : device.trust >= 40 ? 'medium' : 'low'
                  }`}
                  style={{ width: `${device.trust}%` }}
                >
                  <span>{device.trust}</span>
                </div>
              </div>
            </div>
            <button className="btn-primary">View Details</button>
          </motion.div>
        ))}
      </motion.div>

      {filteredDevices.length === 0 && (
        <div className="no-results glass">
          <div className="no-results-icon">🔍</div>
          <h3>No devices found</h3>
          <p>Try adjusting your search criteria</p>
        </div>
      )}
    </motion.div>
  )
}

export default NetworkDiscovery
