import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Menu, Shield, Github } from 'lucide-react'
import './Navbar.css'

const Navbar = ({ toggleSidebar }) => {
  return (
    <motion.nav 
      className="navbar glass"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="navbar-content">
        <div className="navbar-left">
          <button className="menu-btn" onClick={toggleSidebar}>
            <Menu size={24} />
          </button>
          <Link to="/dashboard" className="navbar-brand">
            <Shield className="brand-icon" size={28} />
            <span className="brand-text">Project Argus</span>
            <span className="brand-badge">Interactive Demo</span>
          </Link>
        </div>
        <div className="navbar-right">
          <a 
            href="https://github.com/phoenixdev-512/advanced-AI-IDSIPSframework" 
            target="_blank" 
            rel="noopener noreferrer"
            className="nav-link"
          >
            <Github size={20} />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </motion.nav>
  )
}

export default Navbar
