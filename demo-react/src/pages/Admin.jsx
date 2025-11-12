import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { ChartCard } from '../components/Card'
import { Upload, Rocket, Download, Settings as SettingsIcon } from 'lucide-react'
import './Admin.css'

const Admin = () => {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [isTraining, setIsTraining] = useState(false)
  const [trainingProgress, setTrainingProgress] = useState(0)
  const [currentEpoch, setCurrentEpoch] = useState(0)
  const [currentLoss, setCurrentLoss] = useState('-')
  const [trainingData, setTrainingData] = useState([])

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setUploadedFile(file.name)
    }
  }

  const startTraining = () => {
    setIsTraining(true)
    setTrainingProgress(0)
    setCurrentEpoch(0)
    const data = []

    const totalEpochs = 50
    let epoch = 0

    const interval = setInterval(() => {
      epoch++
      const progress = (epoch / totalEpochs) * 100
      const loss = (0.5 - (epoch / totalEpochs) * 0.4 + Math.random() * 0.05).toFixed(4)

      setTrainingProgress(progress)
      setCurrentEpoch(epoch)
      setCurrentLoss(loss)
      
      data.push({ epoch, loss: parseFloat(loss) })
      setTrainingData([...data])

      if (epoch >= totalEpochs) {
        clearInterval(interval)
        setIsTraining(false)
      }
    }, 200)
  }

  return (
    <motion.div
      className="admin"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="page-header">
        <h1 className="page-title">Admin & Model Training</h1>
        <p className="page-subtitle">Train custom ML models and manage system settings</p>
      </div>

      <div className="training-section glass">
        <div className="section-header">
          <Rocket size={24} />
          <h2>Train New Anomaly Detection Model</h2>
        </div>

        <motion.div 
          className="upload-zone"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => document.getElementById('file-input').click()}
        >
          <Upload className="upload-icon" size={48} />
          <h3>Drag & Drop Your Dataset Here</h3>
          <p>or click to select files</p>
          <span className="upload-hint">Supported formats: .csv, .parquet, .pkl</span>
          <input
            id="file-input"
            type="file"
            style={{ display: 'none' }}
            accept=".csv,.parquet,.pkl"
            onChange={handleFileUpload}
          />
        </motion.div>

        {uploadedFile && (
          <motion.div 
            className="upload-success"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="success-icon">✅</div>
            <div>
              <strong>Dataset uploaded successfully:</strong>
              <span className="filename">{uploadedFile}</span>
            </div>
          </motion.div>
        )}
      </div>

      <div className="config-grid">
        <div className="config-card glass">
          <h3>Model Configuration</h3>
          <div className="form-group">
            <label>Model Type</label>
            <select className="form-control">
              <option>Autoencoder (Deep Learning)</option>
              <option>Isolation Forest (Ensemble)</option>
              <option>One-Class SVM</option>
            </select>
          </div>
          <div className="form-group">
            <label>Epochs</label>
            <input type="number" className="form-control" defaultValue="50" />
          </div>
          <div className="form-group">
            <label>Batch Size</label>
            <input type="number" className="form-control" defaultValue="32" />
          </div>
        </div>

        <div className="progress-card glass">
          <h3>Training Progress</h3>
          <div className="progress-info">
            <div className="progress-row">
              <span>Status</span>
              <span className={`status-badge ${isTraining ? 'training' : 'ready'}`}>
                {isTraining ? 'Training' : 'Ready'}
              </span>
            </div>
            <div className="progress-bar-container">
              <div 
                className="progress-bar-fill"
                style={{ width: `${trainingProgress}%` }}
              />
            </div>
            <div className="progress-row">
              <span>Epoch</span>
              <strong>{currentEpoch}/50</strong>
            </div>
            <div className="progress-row">
              <span>Loss</span>
              <strong>{currentLoss}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button 
          className="btn-primary large"
          onClick={startTraining}
          disabled={isTraining}
        >
          <Rocket size={20} />
          {isTraining ? 'Training...' : 'Start Training'}
        </button>
        <button className="btn-secondary large">
          <SettingsIcon size={20} />
          View Model History
        </button>
        <button className="btn-secondary large">
          <Download size={20} />
          Download Model
        </button>
      </div>

      {trainingData.length > 0 && (
        <ChartCard title="Training Metrics" delay={0.3}>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trainingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
              <XAxis dataKey="epoch" stroke="var(--text-muted)" />
              <YAxis stroke="var(--text-muted)" />
              <Tooltip 
                contentStyle={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--glass-border)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="loss" 
                stroke="var(--primary)" 
                strokeWidth={2}
                dot={{ fill: 'var(--primary)', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      )}

      <div className="settings-card glass">
        <h3>System Settings</h3>
        <div className="settings-grid">
          <div className="setting-item">
            <label>Trust Score Threshold</label>
            <div className="slider-container">
              <input type="range" min="0" max="100" defaultValue="20" className="slider" />
              <span className="slider-value">20</span>
            </div>
          </div>
          <div className="setting-item">
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Auto-Block Enabled</span>
            </label>
            <p className="setting-description">Automatically block low-trust devices</p>
          </div>
          <div className="setting-item">
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Real-time Monitoring</span>
            </label>
            <p className="setting-description">Enable continuous network monitoring</p>
          </div>
          <div className="setting-item">
            <label className="checkbox-label">
              <input type="checkbox" />
              <span>Email Notifications</span>
            </label>
            <p className="setting-description">Receive alerts via email</p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default Admin
