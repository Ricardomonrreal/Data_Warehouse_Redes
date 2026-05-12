import { Bar, Doughnut, Line } from 'react-chartjs-2'
import { StatCard, Loading, defaultScales, defaultLegend } from '../chartSetup'

export default function ResumenView({ data }) {
  if (!data) return <Loading />

  const origenData = {
    labels: Object.keys(data.por_origen),
    datasets: [{ data: Object.values(data.por_origen), backgroundColor: ['rgba(59,130,246,0.8)', 'rgba(168,85,247,0.8)'], borderColor: ['#3b82f6', '#a855f7'], borderWidth: 2, hoverOffset: 8 }],
  }

  const tg = {}
  ;(data.timeline || []).forEach(t => {
    const k = t.timestamp?.slice(11, 16) || 'N/A'
    if (!tg[k]) tg[k] = { TCP: 0, UDP: 0 }
    tg[k][t.origen] = t.cantidad
  })
  const tLabels = Object.keys(tg)

  const timeData = {
    labels: tLabels,
    datasets: [
      { label: 'TCP', data: tLabels.map(k => tg[k].TCP), backgroundColor: '#3b82f6', borderRadius: 4 },
      { label: 'UDP', data: tLabels.map(k => tg[k].UDP), backgroundColor: '#a855f7', borderRadius: 4 },
    ],
  }

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0, fontSize: '1.6rem', color: '#FFFFFF', fontWeight: 600, letterSpacing: '-0.5px' }}>Panel Principal</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--bg-panel)', padding: '8px 16px', borderRadius: '30px', border: '1px solid var(--border-color)' }}>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--accent-green)', boxShadow: '0 0 10px var(--accent-green)' }}></div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '0.5px', textTransform: 'uppercase' }}>Supabase Online</span>
        </div>
      </div>
      <div className="stats-grid">
        <StatCard value={data.total} label="Total registros" color="blue" />
        <StatCard value={data.por_origen?.TCP || 0} label="Registros TCP" color="cyan" />
        <StatCard value={data.por_origen?.UDP || 0} label="Registros UDP" color="emerald" />
        <StatCard value={data.fecha_inicio ? new Date(data.fecha_inicio).toLocaleTimeString() : '-'} label="Primera inserción" color="amber" />
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title">Distribución por Origen</div>
          <div className="chart-wrapper"><Doughnut data={origenData} options={{ responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 20 } } } }} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title">Ingesta por Minuto (Barras)</div>
          <div className="chart-wrapper">
            <Bar 
              data={timeData} 
              options={{ 
                responsive: true, 
                maintainAspectRatio: false, 
                plugins: { legend: defaultLegend }, 
                scales: { 
                  x: { stacked: true, ticks: { color: '#94a3b8' }, grid: { display: false } }, 
                  y: { stacked: true, ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } 
                } 
              }} 
            />
          </div>
        </div>
      </div>
    </>
  )
}
