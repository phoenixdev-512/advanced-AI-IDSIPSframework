import React from 'react'
import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LayoutDashboard, Network, MonitorDot, AlertTriangle, Settings } from 'lucide-react'
import './Sidebar.css'

const menuItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/network', icon: Network, label: 'Network Discovery' },
  { path: '/devices', icon: MonitorDot, label: 'Device Details' },
  { path: '/alerts', icon: AlertTriangle, label: 'Alerts & Incidents' },
  { path: '/admin', icon: Settings, label: 'Admin & Training' },
]

const Sidebar = ({ isOpen }) => {
  return (
    <motion.aside 
      className={`sidebar glass ${isOpen ? 'open' : 'closed'}`}
      initial={{ x: -300 }}
      animate={{ x: isOpen ? 0 : -300 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
    >
      <div className="sidebar-content">
        {menuItems.map((item, index) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}
          >
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="sidebar-item-content"
            >
              <item.icon className="sidebar-icon" size={20} />
              <span className="sidebar-label">{item.label}</span>
            </motion.div>
          </NavLink>
        ))}
      </div>
    </motion.aside>
  )
}

export default Sidebar
