import { useState } from 'react';
import { Chart } from 'react-chartjs-2';
import { StatCard, Loading, PALETTE } from '../chartSetup';

export default function CategoriasView({ data }) {
  const [metric, setMetric] = useState('revenue');

  if (!data) return <Loading />;

  const topCategorias = data.top_categorias || [];
  const topProductos = data.top_productos || [];

  const mainCategory = topCategorias[0] || {};
  const totalRevenue = topCategorias.reduce((a, b) => a + b.revenue, 0);

  const colorMap = {};
  topCategorias.forEach((cat, idx) => {
    colorMap[cat.category] = PALETTE[idx % PALETTE.length];
  });

  const treemapData = {
    datasets: [{
      label: 'Top Productos por Categoría',
      tree: topProductos,
      key: metric,
      groups: ['category', 'id'],
      spacing: 1,
      borderWidth: 1,
      borderColor: 'var(--bg-panel)',
      backgroundColor: (ctx) => {
        if (ctx.type !== 'data') return 'transparent';
        const raw = ctx.raw;
        if (!raw || !raw._data) return 'transparent';
        
        const catName = raw._data.category || (raw._data.children ? raw._data.children[0].category : null);
        return colorMap[catName] || 'rgba(59, 130, 246, 0.5)';
      },
      labels: {
        display: true,
        formatter: (ctx) => {
          if (ctx.type !== 'data') return '';
          return [ctx.raw._data.id.substring(0, 8), `${metric === 'revenue' ? '$' : ''}${ctx.raw.v.toLocaleString()}`];
        },
        color: '#FFFFFF',
        font: { family: 'Inter', size: 10 }
      },
      captions: {
        display: true,
        align: 'center',
        color: '#FFFFFF',
        font: { family: 'Inter', size: 14, weight: '600' },
        formatter: (ctx) => {
          return ctx.raw ? ctx.raw._data.category : '';
        }
      }
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: (items) => {
            if (!items.length) return '';
            const raw = items[0].raw;
            return raw._data ? raw._data.category : '';
          },
          label: (item) => {
            const raw = item.raw;
            if (!raw || !raw._data) return '';
            return `ID: ${raw._data.id} | ${metric === 'revenue' ? 'Ingreso: $' : 'Ventas: '}${raw.v.toLocaleString()}`;
          }
        }
      }
    }
  };

  return (
    <>
      <div className="stats-grid">
        <StatCard value={`$${totalRevenue.toLocaleString()}`} label="Top 10 Ingresos Netos" color="blue" />
        <StatCard value={topCategorias.length} label="Categorías Principales" color="emerald" />
        <StatCard value={mainCategory.category || '-'} label="Categoría Top" color="amber" />
        <StatCard value={`$${(mainCategory.revenue || 0).toLocaleString()}`} label="Ingreso Categoría Top" color="cyan" />
      </div>

      <div className="chart-section" style={{ gridTemplateColumns: '1fr' }}>
        <div className="chart-card">
          <div className="chart-card__title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Mapa de Árbol: Productos Top por Categoría</span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button 
                className="badge"
                style={{ cursor: 'pointer', border: '1px solid var(--border-color)', background: metric === 'revenue' ? 'var(--accent-blue)' : 'transparent', color: metric === 'revenue' ? 'white' : 'var(--text-secondary)' }}
                onClick={() => setMetric('revenue')}
              >
                Por Ingresos
              </button>
              <button 
                className="badge"
                style={{ cursor: 'pointer', border: '1px solid var(--border-color)', background: metric === 'sales' ? 'var(--accent-blue)' : 'transparent', color: metric === 'sales' ? 'white' : 'var(--text-secondary)' }}
                onClick={() => setMetric('sales')}
              >
                Por Unidades
              </button>
            </div>
          </div>
          <div className="chart-wrapper" style={{ height: '500px' }}>
            <Chart type="treemap" data={treemapData} options={options} />
          </div>
        </div>
      </div>
      
      <div className="table-section">
        <div className="table-header">
          <div className="table-header__title">Desempeño de Categorías Top</div>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Ranking</th>
                <th>Categoría (Inglés)</th>
                <th>Ingresos Netos ($)</th>
                <th>Ventas Totales</th>
              </tr>
            </thead>
            <tbody>
              {topCategorias.map((cat, i) => (
                <tr key={i}>
                  <td style={{ color: i < 3 ? 'var(--accent-yellow)' : 'var(--text-secondary)', fontWeight: 600 }}>#{i + 1}</td>
                  <td style={{ textTransform: 'capitalize' }}>{cat.category}</td>
                  <td>${cat.revenue.toLocaleString()}</td>
                  <td>{cat.sales.toLocaleString()} uds.</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
