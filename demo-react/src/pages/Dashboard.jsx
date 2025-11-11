import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { StatCard, ChartCard } from '../components/Card'
import { MonitorDot, Target, AlertTriangle, Shield } from 'lucide-react'
import './Dashboard.css'

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalDevices: 0,
    avgTrust: 0,
    activeAlerts: 0,
    blockedThreats: 0
  })

  const [trafficData, setTrafficData] = useState([])
  const [trustDistribution, setTrustDistribution] = useState([])

  useEffect(() => {
    // Animate stats
    const targetStats = {
      totalDevices: 24,
      avgTrust: 82,
      activeAlerts: 3,
      blockedThreats: 127
    }

    const duration = 2000
    const steps = 60
    const interval = duration / steps

    let step = 0
    const timer = setInterval(() => {
      step++
      const progress = step / steps
      
      setStats({
        totalDevices: Math.floor(targetStats.totalDevices * progress),
        avgTrust: Math.floor(targetStats.avgTrust * progress),
        activeAlerts: Math.floor(targetStats.activeAlerts * progress),
        blockedThreats: Math.floor(targetStats.blockedThreats * progress)
      })

      if (step >= steps) {
        clearInterval(timer)
        setStats(targetStats)
      }
    }, interval)

    // Generate traffic data
    const traffic = Array.from({ length: 60 }, (_, i) => ({
      time: i,
      value: Math.floor(Math.random() * 1000) + 500
    }))
    setTrafficData(traffic)

    // Generate trust distribution
    const trust = [
      { range: '90-100', count: 8, fill: 'var(--success)' },
      { range: '70-89', count: 10, fill: 'var(--primary)' },
      { range: '40-69', count: 4, fill: 'var(--warning)' },
      { range: '0-39', count: 2, fill: 'var(--danger)' }
    ]
    setTrustDistribution(trust)

    // Simulate live updates
    const updateInterval = setInterval(() => {
      setTrafficData(prev => {
        const newData = [...prev.slice(1), {
          time: prev[prev.length - 1].time + 1,
          value: Math.floor(Math.random() * 1000) + 500
        }]
        return newData
      })
    }, 3000)

    return () => {
      clearInterval(timer)
      clearInterval(updateInterval)
    }
  }, [])

  const devices = [
    { name: 'Desktop-PC-01', ip: '192.168.1.105', status: 'online', trust: 85 },
    { name: 'Laptop-Work', ip: '192.168.1.112', status: 'online', trust: 92 },
    { name: 'iPhone-Personal', ip: '192.168.1.156', status: 'online', trust: 88 },
    { name: 'Smart-TV-Living', ip: '192.168.1.203', status: 'online', trust: 76 },
    { name: 'Security-Camera-01', ip: '192.168.1.221', status: 'online', trust: 45 },
    { name: 'Alexa-Echo', ip: '192.168.1.198', status: 'online', trust: 71 }
  ]

  return (
    <motion.div
      className="dashboard"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Real-time network security monitoring</p>
      </div>

      <div className="alert-banner glass">
        <div className="alert-icon">ℹ️</div>
        <div>
          <strong>Interactive Demo Mode:</strong> This demo uses simulated data to showcase Project Argus features. All data updates in real-time.
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={MonitorDot}
          title="Total Devices"
          value={stats.totalDevices}
          label="Active on network"
          color="primary"
          delay={0.1}
        />
        <StatCard
          icon={Target}
          title="Avg Trust Score"
          value={stats.avgTrust}
          label="Network health"
          color="success"
          delay={0.2}
        />
        <StatCard
          icon={AlertTriangle}
          title="Active Alerts"
          value={stats.activeAlerts}
          label="Requires attention"
          color="warning"
          delay={0.3}
        />
        <StatCard
          icon={Shield}
          title="Blocked Threats"
          value={stats.blockedThreats}
          label="Last 24 hours"
          color="danger"
          delay={0.4}
        />
      </div>

      <div className="charts-grid">
        <ChartCard title="Network Traffic (Last Hour)" delay={0.5}>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={trafficData}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
              <XAxis dataKey="time" stroke="var(--text-muted)" />
              <YAxis stroke="var(--text-muted)" />
              <Tooltip 
                contentStyle={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--glass-border)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)'
                }}
              />
              <Area type="monotone" dataKey="value" stroke="var(--primary)" fillOpacity={1} fill="url(#colorValue)" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Trust Score Distribution" delay={0.6}>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={trustDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
              <XAxis dataKey="range" stroke="var(--text-muted)" />
              <YAxis stroke="var(--text-muted)" />
              <Tooltip 
                contentStyle={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--glass-border)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)'
                }}
              />
              <Bar dataKey="count" fill="var(--primary)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <motion.div 
        className="devices-table glass"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <h3 className="table-title">Recent Devices</h3>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Device</th>
                <th>IP Address</th>
                <th>Status</th>
                <th>Trust Score</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((device, index) => (
                <motion.tr
                  key={device.ip}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8 + index * 0.1 }}
                >
                  <td>{device.name}</td>
                  <td>{device.ip}</td>
                  <td>
                    <span className={`status-badge status-${device.status}`}>
                      <span className="status-dot"></span>
                      {device.status}
                    </span>
                  </td>
                  <td>
                    <div className="trust-score-bar">
                      <div 
                        className={`trust-score-fill ${
                          device.trust >= 70 ? 'high' : device.trust >= 40 ? 'medium' : 'low'
                        }`}
                        style={{ width: `${device.trust}%` }}
                      >
                        {device.trust}
                      </div>
                    </div>
                  </td>
                  <td>Just now</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default Dashboard
