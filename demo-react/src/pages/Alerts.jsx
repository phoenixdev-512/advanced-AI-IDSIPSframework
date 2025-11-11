import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { StatCard } from '../components/Card'
import { AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react'
import './Alerts.css'

const Alerts = () => {
  const [filter, setFilter] = useState('all')

  const alerts = [
    { 
      id: 1,
      time: '2 min ago', 
      severity: 'high', 
      type: 'Port Scan', 
      device: 'Security-Camera-01', 
      description: 'Unusual port scanning detected', 
      status: 'Active' 
    },
    { 
      id: 2,
      time: '15 min ago', 
      severity: 'medium', 
      type: 'Anomaly', 
      device: 'Smart-TV-Living', 
      description: 'Traffic pattern deviation detected', 
      status: 'Investigating' 
    },
    { 
      id: 3,
      time: '1 hour ago', 
      severity: 'low', 
      type: 'Info', 
      device: 'Desktop-PC-01', 
      description: 'New device connected to network', 
      status: 'Resolved' 
    },
    { 
      id: 4,
      time: '3 hours ago', 
      severity: 'high', 
      type: 'Vulnerability', 
      device: 'Security-Camera-01', 
      description: 'Open Telnet port detected (CVE-2024-1234)', 
      status: 'Blocked' 
    },
    { 
      id: 5,
      time: '5 hours ago', 
      severity: 'medium', 
      type: 'Suspicious Activity', 
      device: 'Alexa-Echo', 
      description: 'Unexpected outbound connections', 
      status: 'Monitoring' 
    },
  ]

  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter(a => a.severity === filter)

  const stats = {
    critical: alerts.filter(a => a.severity === 'critical').length,
    high: alerts.filter(a => a.severity === 'high').length,
    medium: alerts.filter(a => a.severity === 'medium').length,
    low: alerts.filter(a => a.severity === 'low').length
  }

  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'high': return <AlertCircle size={20} />
      case 'medium': return <AlertTriangle size={20} />
      case 'low': return <Info size={20} />
      default: return <XCircle size={20} />
    }
  }

  return (
    <motion.div
      className="alerts"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="page-header">
        <h1 className="page-title">Alerts & Security Incidents</h1>
        <p className="page-subtitle">Monitor and respond to security events</p>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={XCircle}
          title="Critical"
          value={stats.critical}
          label="Immediate action required"
          color="danger"
          delay={0.1}
        />
        <StatCard
          icon={AlertCircle}
          title="High Priority"
          value={stats.high}
          label="Review recommended"
          color="danger"
          delay={0.2}
        />
        <StatCard
          icon={AlertTriangle}
          title="Medium"
          value={stats.medium}
          label="Monitor closely"
          color="warning"
          delay={0.3}
        />
        <StatCard
          icon={Info}
          title="Low Priority"
          value={stats.low}
          label="For your information"
          color="info"
          delay={0.4}
        />
      </div>

      <div className="filter-tabs glass">
        {['all', 'high', 'medium', 'low'].map((tab) => (
          <button
            key={tab}
            className={`filter-tab ${filter === tab ? 'active' : ''}`}
            onClick={() => setFilter(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="alerts-list">
        {filteredAlerts.map((alert, index) => (
          <motion.div
            key={alert.id}
            className={`alert-card glass severity-${alert.severity}`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 + index * 0.1 }}
            whileHover={{ x: 4, boxShadow: '0 8px 24px rgba(0, 0, 0, 0.2)' }}
          >
            <div className="alert-icon">
              {getSeverityIcon(alert.severity)}
            </div>
            <div className="alert-content">
              <div className="alert-header">
                <div>
                  <h3 className="alert-type">{alert.type}</h3>
                  <p className="alert-device">{alert.device}</p>
                </div>
                <div className="alert-meta">
                  <span className="alert-time">{alert.time}</span>
                  <span className={`alert-status status-${alert.status.toLowerCase()}`}>
                    {alert.status}
                  </span>
                </div>
              </div>
              <p className="alert-description">{alert.description}</p>
              <div className="alert-actions">
                <button className="btn-small primary">View Details</button>
                <button className="btn-small secondary">Dismiss</button>
                <button className="btn-small secondary">Block Device</button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredAlerts.length === 0 && (
        <div className="no-alerts glass">
          <div className="no-alerts-icon">✅</div>
          <h3>No alerts found</h3>
          <p>Your network is secure</p>
        </div>
      )}
    </motion.div>
  )
}

export default Alerts
