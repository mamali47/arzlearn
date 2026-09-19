import { Link } from 'react-router-dom'
import type { ArticleListItem } from '../api/types'
import { formatDatePersian } from '../utils/apiError'
import './ArticleCard.css'

interface Props {
  article: ArticleListItem
  variant?: 'hero' | 'default'
  /**
   * اولین کارت قابل‌مشاهده‌ی صفحه (معمولاً اسلاید اول کاروسل اخبار).
   *
   * تصویر آن تقریباً همیشه همان عنصر LCP صفحه است؛ پس نباید lazy باشد و
   * باید با اولویت بالا دانلود شود. lazy بودنِ تصویر LCP یکی از رایج‌ترین
   * دلایل «قرمز» شدن معیار LCP در PageSpeed است.
   */
  priority?: boolean
}

export default function ArticleCard({ article, variant = 'default', priority = false }: Props) {
  const badgeTag = article.main_tags[0]
  const isHero = variant === 'hero'

  return (
    <Link to={`/article/${article.slug}`} className={`article-card article-card--${variant}`}>
      <div className="article-card__image">
        {article.image ? (
          <img
            src={article.image}
            alt={article.title}
            /* width/height واقعی تصویر: فضای تصویر از اول رزرو می‌شود و
               صفحه هنگام لود شدن عکس نمی‌پرد (CLS = 0) */
            width={isHero ? 800 : 480}
            height={isHero ? 450 : 270}
            loading={priority ? 'eager' : 'lazy'}
            fetchPriority={priority ? 'high' : 'auto'}
            decoding={priority ? 'sync' : 'async'}
          />
        ) : (
          <div className="article-card__placeholder" />
        )}
        {badgeTag && <span className="article-card__badge">{badgeTag.name}</span>}
      </div>
      <div className="article-card__body">
        <h3>{article.title}</h3>
        <span className="text-muted">{formatDatePersian(article.published_at)}</span>
      </div>
    </Link>
  )
}
