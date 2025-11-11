import React from 'react'
import { motion } from 'framer-motion'
import './Card.css'

const Card = ({ children, className = '', delay = 0, hover = true }) => {
  return (
    <motion.div
      className={`card glass ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={hover ? { y: -4, boxShadow: '0 20px 40px -5px rgba(0, 0, 0, 0.3)' } : {}}
    >
      {children}
    </motion.div>
  )
}

export const StatCard = ({ icon: Icon, title, value, label, color = 'primary', delay = 0 }) => {
  return (
    <Card delay={delay}>
      <div className="stat-card">
        <div className="stat-header">
          <span className="stat-title">{title}</span>
          <div className={`stat-icon stat-icon-${color}`}>
            <Icon size={24} />
          </div>
        </div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </Card>
  )
}

export const ChartCard = ({ title, children, delay = 0 }) => {
  return (
    <Card delay={delay} hover={false}>
      <div className="chart-card">
        <h3 className="chart-title">{title}</h3>
        <div className="chart-content">
          {children}
        </div>
      </div>
    </Card>
  )
}

export default Card
