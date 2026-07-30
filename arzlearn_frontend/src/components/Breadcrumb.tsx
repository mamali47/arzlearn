import { Link } from 'react-router-dom'

export interface BreadcrumbItem {
  label: string
  to?: string
}

export default function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  const allItems: BreadcrumbItem[] = [{ label: 'خانه', to: '/' }, ...items]

  return (
    <nav className="breadcrumb container" aria-label="breadcrumb">
      {allItems.map((item, index) => {
        const isLast = index === allItems.length - 1
        return (
          <span key={index} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {index > 0 && <span className="sep">/</span>}
            {isLast || !item.to ? (
              <span className="current">{item.label}</span>
            ) : (
              <Link to={item.to}>{item.label}</Link>
            )}
          </span>
        )
      })}
    </nav>
  )
}
