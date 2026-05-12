import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler,
  ScatterController,
} from 'chart.js'

ChartJS.register(
  CategoryScale, LinearScale, BarElement, PointElement,
  LineElement, ArcElement, Title, Tooltip, Legend, Filler,
  ScatterController
)

export const CHART_COLORS = {
  blue: 'rgba(59, 130, 246, 0.8)',
  purple: 'rgba(168, 85, 247, 0.8)',
  cyan: 'rgba(34, 211, 238, 0.8)',
  emerald: 'rgba(52, 211, 153, 0.8)',
  amber: 'rgba(251, 191, 36, 0.8)',
  rose: 'rgba(251, 113, 133, 0.8)',
  slate: 'rgba(148, 163, 184, 0.5)',
}

export const PALETTE = [
  CHART_COLORS.blue, CHART_COLORS.purple, CHART_COLORS.cyan,
  CHART_COLORS.emerald, CHART_COLORS.amber, CHART_COLORS.rose,
  'rgba(96,165,250,0.8)', 'rgba(192,132,252,0.8)', 'rgba(45,212,191,0.8)',
  'rgba(74,222,128,0.8)', 'rgba(253,186,116,0.8)', 'rgba(244,114,182,0.8)',
  'rgba(129,140,248,0.8)', 'rgba(34,197,94,0.8)', 'rgba(249,115,22,0.8)',
]

export const defaultScales = {
  x: { ticks: { color: '#A1A1AA', font: { family: 'Inter', size: 11 } }, grid: { display: false, color: '#27272A' } },
  y: { ticks: { color: '#A1A1AA', font: { family: 'Inter', size: 11 } }, grid: { display: true, color: '#27272A' }, border: { display: false } },
}

export const defaultLegend = { labels: { color: '#A1A1AA', font: { family: 'Inter', size: 12 } } }

export function StatCard({ icon, value, label, color }) {
  // Mapping color to css class
  const colorClass = color === 'blue' || color === 'cyan' ? 'icon-blue' : 
                     color === 'emerald' ? 'icon-green' : 
                     color === 'amber' ? 'icon-yellow' : 'icon-red';
  
  return (
    <div className="stat-card">
      <div className="stat-card__info">
        <span className="stat-card__label">{label}</span>
        <span className="stat-card__value">{typeof value === 'number' ? value.toLocaleString() : value}</span>
      </div>
      <div className={`stat-card__icon-wrap ${colorClass}`}>
        {icon || (
          <svg fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        )}
      </div>
    </div>
  )
}

export function Loading() {
  return <div className="loading">Loading data...</div>
}

export function EmptyState({ text = 'No data available' }) {
  return <div className="empty-state">{text}</div>
}
