import { Link } from 'react-router-dom'
import type { ArticleListItem } from '../api/types'
import { formatDatePersian } from '../utils/apiError'
import './ArticleCard.css'

interface Props {
  article: ArticleListItem
  variant?: 'hero' | 'default'
}

export default function ArticleCard({ article, variant = 'default' }: Props) {
  const badgeTag = article.main_tags[0]

  return (
    <Link to={`/article/${article.slug}`} className={`article-card article-card--${variant}`}>
      <div className="article-card__image">
        {article.image ? <img src={article.image} alt={article.title} loading="lazy" /> : <div className="article-card__placeholder" />}
        {badgeTag && <span className="article-card__badge">{badgeTag.name}</span>}
      </div>
      <div className="article-card__body">
        <h3>{article.title}</h3>
        <span className="text-muted">{formatDatePersian(article.published_at)}</span>
      </div>
    </Link>
  )
}
