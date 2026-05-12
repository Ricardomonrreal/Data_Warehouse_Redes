import { useState, useEffect, useCallback } from 'react'
import './index.css'
import ResumenView from './views/ResumenView'
import GeoView from './views/GeoView'
import SensoresView from './views/SensoresView'
import DatosView from './views/DatosView'

const API_BASE = '';

const TABS = [
  { 
    id: 'resumen', label: 'Dashboard', 
    icon: <svg className="sidebar__icon" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
  },
  { 
    id: 'geo', label: 'Geo Analytics', 
    icon: <svg className="sidebar__icon" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
  },
  { 
    id: 'sensores', label: 'Sensors Data', 
    icon: <svg className="sidebar__icon" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" /></svg>
  },
  { 
    id: 'datos', label: 'Data Tables', 
    icon: <svg className="sidebar__icon" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>
  },
]

const ENDPOINTS = {
  resumen: '/api/datos/resumen',
  sensores: '/api/datos/sensores',
  datos: '/api/datos?limite=200',
  geo: '/api/analytics/geo',
}

function App() {
  const [tab, setTab] = useState('resumen')
  const [data, setData] = useState({})
  const [error, setError] = useState(null)
  const [loadingTab, setLoadingTab] = useState(null)

  const loadTab = useCallback(async (tabId) => {
    if (data[tabId]) return
    setLoadingTab(tabId)
    try {
      const url = ENDPOINTS[tabId]
      if (!url) return
      const res = await fetch(`${API_BASE}${url}`)
      
      const contentType = res.headers.get("content-type");
      if (!res.ok) {
        if (contentType && contentType.includes("application/json")) {
          const errJson = await res.json();
          throw new Error(`Server Error ${res.status}: ${errJson.error || 'Unknown error'}`);
        }
        throw new Error(`Server Error HTTP ${res.status}`);
      }
      
      const json = await res.json()
      setData(prev => ({ ...prev, [tabId]: json }))
    } catch (err) {
      setError('Connection error: ' + err.message)
      console.error(err)
    } finally {
      setLoadingTab(null)
    }
  }, [data])

  useEffect(() => { loadTab(tab) }, [tab])

  const isLoading = loadingTab === tab && !data[tab]

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar__logo">
          <svg className="sidebar__logo-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
          HelpDesk
        </div>
        <nav className="sidebar__nav">
          {TABS.map(t => (
            <button 
              key={t.id} 
              className={`sidebar__item ${tab === t.id ? 'sidebar__item--active' : ''}`} 
              onClick={() => setTab(t.id)}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="top-header">
          <div className="top-header__search">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="var(--text-secondary)" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input type="text" placeholder="Search..." />
          </div>
          <div className="top-header__actions">
            <div className="top-header__profile">
              <div className="top-header__avatar">R</div>
              Ricardo M.
            </div>
          </div>
        </header>

        <div className="page-content">
          {error ? (
            <div style={{ color: 'var(--accent-red)', padding: '20px' }}>{error}</div>
          ) : isLoading ? (
            <div className="loading">Loading data...</div>
          ) : (
            <>
              {tab === 'resumen' && <ResumenView data={data.resumen} />}
              {tab === 'geo' && <GeoView data={data.geo} />}
              {tab === 'sensores' && <SensoresView data={data.sensores} />}
              {tab === 'datos' && <DatosView data={data.datos} />}
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
