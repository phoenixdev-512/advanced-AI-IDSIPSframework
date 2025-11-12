import React from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { StatCard, ChartCard } from '../components/Card'
import { Activity, Wifi, Lock, AlertCircle } from 'lucide-react'
import './DeviceDetails.css'

const DeviceDetails = () => {
  const trafficData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    traffic: Math.floor(Math.random() * 50) + 10
  }))

  return (
    <motion.div
      className="device-details"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="page-header">
        <h1 className="page-title">Device Details</h1>
        <p className="page-subtitle">Comprehensive device information and analytics</p>
      </div>

      <div className="device-info-card glass">
        <div className="device-info-header">
          <div>
            <div className="device-icon-large">💻</div>
            <h2>Desktop-PC-01</h2>
            <p className="device-type">Windows 11 Workstation</p>
          </div>
          <span className="status-badge online">Online</span>
        </div>
        
        <div className="device-meta">
          <div className="meta-item">
            <span className="meta-label">IP Address</span>
            <span className="meta-value">192.168.1.105</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">MAC Address</span>
            <span className="meta-value">AA:BB:CC:DD:EE:FF</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">First Seen</span>
            <span className="meta-value">2024-01-15</span>
          </div>
        </div>

        <div className="trust-score-section">
          <h4>Trust Score</h4>
          <div className="trust-meter">
            <div className="trust-fill high" style={{ width: '85%' }}>
              <span>85</span>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={Activity}
          title="Packets Sent"
          value="1.2M"
          label="Network activity"
          color="primary"
          delay={0.2}
        />
        <StatCard
          icon={Wifi}
          title="Data Transfer"
          value="45.2 GB"
          label="Total bandwidth"
          color="info"
          delay={0.3}
        />
        <StatCard
          icon={Lock}
          title="Vulnerabilities"
          value="0"
          label="All secure"
          color="success"
          delay={0.4}
        />
        <StatCard
          icon={AlertCircle}
          title="Anomalies"
          value="0"
          label="Behavior normal"
          color="success"
          delay={0.5}
        />
      </div>

      <ChartCard title="Traffic Pattern (Last 24 Hours)" delay={0.6}>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={trafficData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
            <XAxis dataKey="hour" stroke="var(--text-muted)" />
            <YAxis stroke="var(--text-muted)" />
            <Tooltip 
              contentStyle={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--glass-border)',
                borderRadius: '8px',
                color: 'var(--text-primary)'
              }}
            />
            <Line type="monotone" dataKey="traffic" stroke="var(--primary)" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="device-ports glass">
        <h3>Open Ports</h3>
        <div className="ports-list">
          <span className="port-badge safe">80 (HTTP)</span>
          <span className="port-badge safe">443 (HTTPS)</span>
          <span className="port-badge safe">3389 (RDP)</span>
          <span className="port-badge verified">✓ All Safe</span>
        </div>
      </div>

      <div className="actions">
        <button className="btn-primary">🔄 Refresh</button>
        <button className="btn-secondary">📊 Export Data</button>
        <button className="btn-secondary">🔍 Deep Scan</button>
      </div>
    </motion.div>
  )
}

export default DeviceDetails
