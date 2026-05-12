import { Bar } from 'react-chartjs-2'
import { StatCard, Loading, PALETTE } from '../chartSetup'

export default function GeoView({ data }) {
  if (!data) return <Loading />

  const estLabels = Object.keys(data.top_estados)
  const estData = {
    labels: estLabels,
    datasets: [{ label: 'Registros', data: Object.values(data.top_estados), backgroundColor: PALETTE.slice(0, estLabels.length), borderRadius: 6 }],
  }

  const cityLabels = Object.keys(data.top_ciudades).slice(0, 15)
  const cityData = {
    labels: cityLabels,
    datasets: [{ label: 'Registros', data: cityLabels.map(c => data.top_ciudades[c]), backgroundColor: 'rgba(34,211,238,0.7)', borderRadius: 6 }],
  }

  const barOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }, y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } } }
  const hBarOpts = { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } }, y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } } } }

  // Top 10 ciudades para responder a la pregunta principal
  const topCiudadesList = Object.entries(data.top_ciudades).slice(0, 10).map(([city, count]) => ({ city, count }));
  const ciudadPrincipal = cityLabels[0] || '-';

  return (
    <>
      <div className="stats-grid">
        <StatCard icon="🌎" value={data.total_registros?.toLocaleString()} label="Total Registros" color="blue" delay={1} />
        <StatCard icon="🏙️" value={data.total_ciudades?.toLocaleString()} label="Ciudades Únicas" color="emerald" delay={2} />
        <StatCard icon="🏆" value={ciudadPrincipal.toUpperCase()} label="Ciudad Principal" color="amber" delay={3} />
        <StatCard icon="📈" value={data.top_ciudades[ciudadPrincipal]?.toLocaleString() || '0'} label="Órdenes en Top Ciudad" color="cyan" delay={4} />
      </div>

      <div className="table-section fade-in" style={{ marginBottom: '24px' }}>
        <div className="table-header">
          <div className="table-header__title" style={{ fontSize: '1.2rem', color: '#e2e8f0' }}>
            ❓ ¿En qué ciudades existe mayor cantidad de registros de órdenes?
          </div>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '10%' }}>Ranking</th>
                <th style={{ width: '40%' }}>Ciudad</th>
                <th style={{ width: '20%' }}>Cantidad de Órdenes</th>
                <th style={{ width: '30%' }}>Volumen vs Top 1</th>
              </tr>
            </thead>
            <tbody>
              {topCiudadesList.map((c, i) => {
                const maxCount = topCiudadesList[0]?.count || 1;
                const pct = ((c.count / maxCount) * 100).toFixed(1);
                return (
                  <tr key={i}>
                    <td style={{ fontWeight: 'bold', color: i < 3 ? '#fbbf24' : '#94a3b8' }}>#{i + 1}</td>
                    <td><span className="badge badge--tcp" style={{ textTransform: 'capitalize', fontSize: '0.95rem' }}>{c.city}</span></td>
                    <td style={{ fontWeight: 'bold', color: '#e2e8f0', fontSize: '1.05rem' }}>{c.count.toLocaleString()}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ flex: 1, height: '8px', background: '#334155', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${pct}%`, height: '100%', background: i === 0 ? '#fbbf24' : '#38bdf8', borderRadius: '4px' }}></div>
                        </div>
                        <span style={{ fontSize: '12px', color: '#94a3b8', width: '45px', textAlign: 'right' }}>{pct}%</span>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">🏙️</span>Top 15 Ciudades (Gráfico)</div>
          <div className="chart-wrapper" style={{ height: '380px' }}><Bar data={cityData} options={hBarOpts} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">🗺️</span>Distribución por Estado</div>
          <div className="chart-wrapper" style={{ height: '380px' }}><Bar data={estData} options={barOpts} /></div>
        </div>
      </div>
    </>
  )
}
