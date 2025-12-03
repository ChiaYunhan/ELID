import { useState } from 'react'
import './App.css'
import { DeviceForm } from './components/DeviceForm'
import { DeviceList } from './components/DeviceList'
import { TransactionList } from './components/TransactionList'

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [activeTab, setActiveTab] = useState<'devices' | 'transactions'>('devices')

  const handleDeviceCreated = () => {
    setRefreshTrigger((prev) => prev + 1)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ELID - Device Management System</h1>
        <p>Manage devices and monitor transactions in real-time</p>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'devices' ? 'active' : ''}`}
          onClick={() => setActiveTab('devices')}
        >
          Devices
        </button>
        <button
          className={`tab ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => setActiveTab('transactions')}
        >
          Transactions
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'devices' ? (
          <div className="devices-view">
            <DeviceForm onDeviceCreated={handleDeviceCreated} />
            <DeviceList refreshTrigger={refreshTrigger} />
          </div>
        ) : (
          <TransactionList />
        )}
      </main>
    </div>
  )
}

export default App
