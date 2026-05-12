import { Loading } from '../chartSetup'

export default function DatosView({ data }) {
  if (!data) return <Loading />

  return (
    <div className="table-section">
      <div className="table-header">
        <div className="table-header__title">Datos Crudos del Warehouse <span style={{marginLeft: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)'}}>{data.total} registros</span></div>
      </div>
      <div className="table-container">
        <table className="data-table">
          <thead><tr><th>ID</th><th>Origen</th><th>Contenido</th><th>Fecha</th></tr></thead>
          <tbody>
            {(data.datos || []).map(row => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td><span className={`badge badge--${row.origen.toLowerCase()}`}>{row.origen}</span></td>
                <td><span className="cell-content">{row.contenido}</span></td>
                <td style={{ whiteSpace: 'nowrap' }}>{row.fecha ? new Date(row.fecha).toLocaleString() : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
