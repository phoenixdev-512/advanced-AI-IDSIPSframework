import React, { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import NetworkDiscovery from './pages/NetworkDiscovery'
import DeviceDetails from './pages/DeviceDetails'
import Alerts from './pages/Alerts'
import Admin from './pages/Admin'
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <BrowserRouter>
      <div className="app">
        <Navbar toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        <div className="app-container">
          <Sidebar isOpen={sidebarOpen} />
          <main className={`main-content ${sidebarOpen ? '' : 'expanded'}`}>
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/network" element={<NetworkDiscovery />} />
                <Route path="/devices/:id?" element={<DeviceDetails />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/admin" element={<Admin />} />
              </Routes>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
