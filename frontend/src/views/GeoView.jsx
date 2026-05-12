import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { StatCard, Loading, PALETTE } from '../chartSetup'

export default function GeoView({ data }) {
  if (!data) return <Loading />

  // Top 10 ciudades para responder a la pregunta principal
  const topCiudadesList = (data.top_ciudades || []).slice(0, 10);
  const ciudadPrincipal = topCiudadesList[0]?.city || '-';
  
  // Datos del mapa
  const ciudadesMapa = data.ciudades_mapa || [];
  const maxCount = ciudadesMapa.length > 0 ? Math.max(...ciudadesMapa.map(c => c.count)) : 1;

  return (
    <>
      <div className="stats-grid">
        <StatCard icon="🌎" value={data.total_registros?.toLocaleString()} label="Total Órdenes" color="blue" delay={1} />
        <StatCard icon="🏙️" value={data.total_ciudades?.toLocaleString()} label="Ciudades Únicas" color="emerald" delay={2} />
        <StatCard icon="🏆" value={ciudadPrincipal.toUpperCase()} label="Ciudad Principal" color="amber" delay={3} />
        <StatCard icon="📈" value={topCiudadesList[0]?.count?.toLocaleString() || '0'} label="Órdenes en Top Ciudad" color="cyan" delay={4} />
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
                const pct = ((c.count / (topCiudadesList[0]?.count || 1)) * 100).toFixed(1);
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

      <div className="chart-section" style={{ gridTemplateColumns: '1fr' }}>
        <div className="chart-card fade-in">
          <div className="chart-card__title" style={{ marginBottom: '16px' }}>
            <span className="chart-card__title-icon">🗺️</span>Mapa de Calor de Órdenes
          </div>
          <div style={{ height: '500px', width: '100%', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            <MapContainer center={[-14.235, -51.925]} zoom={4} style={{ height: '100%', width: '100%', background: '#0f172a' }}>
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              />
              {ciudadesMapa.map((c, i) => {
                const intensidad = c.count / maxCount;
                const radius = Math.max(5, intensidad * 35);
                const color = intensidad > 0.5 ? '#fbbf24' : intensidad > 0.1 ? '#38bdf8' : '#818cf8';
                return (
                  <CircleMarker
                    key={i}
                    center={[c.lat, c.lng]}
                    radius={radius}
                    fillOpacity={Math.max(0.4, intensidad)}
                    color={color}
                    fillColor={color}
                    weight={1}
                  >
                    <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                      <div style={{ padding: '4px' }}>
                        <div style={{ fontWeight: 'bold', textTransform: 'capitalize', color: '#0f172a' }}>{c.city}</div>
                        <div style={{ color: '#334155' }}>{c.count.toLocaleString()} órdenes</div>
                      </div>
                    </Tooltip>
                  </CircleMarker>
                )
              })}
            </MapContainer>
          </div>
        </div>
      </div>
    </>
  )
}
