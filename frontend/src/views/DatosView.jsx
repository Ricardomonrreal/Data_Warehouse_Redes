import { Loading } from '../chartSetup'

export default function DatosView({ data }) {
  if (!data) return <Loading />

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0, fontSize: '1.6rem', color: '#FFFFFF', fontWeight: 600, letterSpacing: '-0.5px' }}>Registros Transaccionales</h2>
        <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', background: 'var(--bg-panel)', padding: '6px 12px', borderRadius: '20px', border: '1px solid var(--border-color)' }}>
          Últimos <b>{data.total}</b> registros procesados
        </span>
      </div>
      <div className="table-section">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '10%' }}>ID</th>
                <th style={{ width: '15%' }}>Origen</th>
                <th style={{ width: '55%' }}>Contenido</th>
                <th style={{ width: '20%' }}>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {(data.datos || []).map(row => (
                <tr key={row.id}>
                  <td style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>#{row.id}</td>
                  <td><span className={`badge badge--${row.origen.toLowerCase()}`}>{row.origen}</span></td>
                  <td><span className="cell-content">{row.contenido}</span></td>
                  <td style={{ whiteSpace: 'nowrap', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{row.fecha ? new Date(row.fecha).toLocaleString() : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
