import { Bar, Line } from 'react-chartjs-2'
import { Loading, defaultScales, defaultLegend } from '../chartSetup'

export default function SensoresView({ data }) {
  if (!data) return <Loading />
  const sensores = data.sensores || []
  if (sensores.length === 0) return <div className="empty-state">No hay lecturas de sensores</div>

  const porTipo = {}
  sensores.forEach(s => { if (!porTipo[s.type]) porTipo[s.type] = []; porTipo[s.type].push(s) })
  const tipos = Object.keys(porTipo)
  const colors = { temperatura: '#fb7185', humedad: '#3b82f6', velocidad: '#34d399', presion: '#fbbf24' }

  const promedios = tipos.map(t => { const v = porTipo[t].map(s => s.value); return Math.round(v.reduce((a, b) => a + b, 0) / v.length * 100) / 100 })
  const avgData = { labels: tipos.map(t => t.charAt(0).toUpperCase() + t.slice(1)), datasets: [{ label: 'Promedio', data: promedios, backgroundColor: tipos.map(t => colors[t] || '#94a3b8'), borderRadius: 6 }] }

  const timeDs = tipos.map(t => ({ label: t.charAt(0).toUpperCase() + t.slice(1), data: porTipo[t].map(s => s.value), borderColor: colors[t] || '#94a3b8', backgroundColor: 'transparent', tension: 0.3, pointRadius: 2 }))
  const timeData = { labels: sensores.map((_, i) => i + 1), datasets: timeDs }

  const ultimas = sensores.slice(-12).reverse()

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0, fontSize: '1.6rem', color: '#FFFFFF', fontWeight: 600, letterSpacing: '-0.5px' }}>Telemetría de Sensores</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(56, 189, 248, 0.1)', padding: '6px 14px', borderRadius: '30px', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#38bdf8' }}>
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v8l9-11h-7z" /></svg>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, letterSpacing: '0.5px', textTransform: 'uppercase' }}>Live Updates</span>
        </div>
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title">Promedio por Tipo</div>
          <div className="chart-wrapper"><Bar data={avgData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8' }, grid: { display: false } }, y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } } }} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title">Lecturas en el Tiempo</div>
          <div className="chart-wrapper"><Line data={timeData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: defaultLegend }, scales: defaultScales }} /></div>
        </div>
      </div>
      <div className="sensors-grid">
        {ultimas.map((s, i) => (
          <div className="sensor-card" key={i}>
            <div className="sensor-card__header"><span className="sensor-card__id">{s.sensor_id}</span><span className="sensor-card__type">{s.type}</span></div>
            <div className="sensor-card__value">{s.value}<span className="sensor-card__unit">{s.unit}</span></div>
            <div className="sensor-card__time">{s.timestamp ? new Date(s.timestamp).toLocaleString() : '-'}</div>
          </div>
        ))}
      </div>
    </>
  )
}
