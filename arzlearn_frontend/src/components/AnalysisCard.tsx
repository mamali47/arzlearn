import { Link } from 'react-router-dom'
import type { ArticleListItem } from '../api/types'
import { formatDatePersian } from '../utils/apiError'
import './AnalysisCard.css'

export default function AnalysisCard({ article }: { article: ArticleListItem }) {
  return (
    <Link to={`/article/${article.slug}`} className="analysis-card">
      <div className="analysis-card__image">
        {article.image ? <img src={article.image} alt={article.title} loading="lazy" /> : <div className="analysis-card__placeholder" />}
        <span className="analysis-card__badge">{article.category.name}</span>
      </div>
      <div className="analysis-card__body">
        <h3>{article.title}</h3>
        <p className="text-muted">{article.summary}</p>
        <span className="analysis-card__date text-muted">{formatDatePersian(article.published_at)}</span>
      </div>
    </Link>
  )
}
