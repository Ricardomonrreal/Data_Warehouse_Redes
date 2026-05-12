import { Loading, StatCard } from '../chartSetup'

export default function SensoresView({ data }) {
  if (!data) return <Loading />
  const sensores = data.sensores || []
  if (sensores.length === 0) return <div className="empty-state">No hay lecturas de sensores</div>

  // Obtener la última lectura por cada tipo de sensor
  const latest = {};
  sensores.forEach(s => {
    latest[s.type] = s;
  });

  const ultimas = sensores.slice(-32).reverse();

  // Colores temáticos por tipo de sensor
  const typeColors = {
    temperatura: { color: '#f43f5e', bg: 'rgba(244, 63, 94, 0.1)' },
    humedad:     { color: '#38bdf8', bg: 'rgba(56, 189, 248, 0.1)' },
    velocidad:   { color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },
    presion:     { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' }
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0, fontSize: '1.6rem', color: '#FFFFFF', fontWeight: 600, letterSpacing: '-0.5px' }}>Telemetría de Sensores</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'rgba(56, 189, 248, 0.05)', padding: '6px 14px', borderRadius: '30px', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#38bdf8' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#38bdf8', boxShadow: '0 0 8px #38bdf8' }}></div>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, letterSpacing: '0.5px', textTransform: 'uppercase' }}>Live Updates</span>
        </div>
      </div>

      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <StatCard value={latest.temperatura ? `${latest.temperatura.value} ${latest.temperatura.unit}` : '-'} label="Última Temperatura" color="red" />
        <StatCard value={latest.humedad ? `${latest.humedad.value} ${latest.humedad.unit}` : '-'} label="Última Humedad" color="cyan" />
        <StatCard value={latest.velocidad ? `${latest.velocidad.value} ${latest.velocidad.unit}` : '-'} label="Última Velocidad" color="emerald" />
        <StatCard value={latest.presion ? `${latest.presion.value} ${latest.presion.unit}` : '-'} label="Última Presión" color="amber" />
      </div>

      <div className="table-section">
        <div className="table-header">
           <div className="table-header__title">Datos Duros Recientes <span style={{ fontSize: '0.8rem', marginLeft: '10px', color: 'var(--text-secondary)' }}>Mostrando últimas {ultimas.length} capturas</span></div>
        </div>
        <div className="table-container" style={{ padding: '20px', overflowY: 'visible' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
            gap: '16px'
          }}>
            {ultimas.map((s, i) => {
              const theme = typeColors[s.type] || { color: '#94a3b8', bg: '#1e293b' };
              return (
                <div key={i} style={{
                  background: 'var(--bg-card)',
                  border: `1px solid var(--border-color)`,
                  borderRadius: '12px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  borderTop: `4px solid ${theme.color}`
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{s.sensor_id}</span>
                    <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '12px', background: theme.bg, color: theme.color, textTransform: 'capitalize', fontWeight: 600 }}>
                      {s.type}
                    </span>
                  </div>
                  <div style={{ fontSize: '1.9rem', fontWeight: 700, color: '#FFFFFF', margin: '4px 0' }}>
                    {s.value} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>{s.unit}</span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textAlign: 'right' }}>
                    {s.timestamp ? new Date(s.timestamp).toLocaleTimeString() : '-'}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </>
  )
}
