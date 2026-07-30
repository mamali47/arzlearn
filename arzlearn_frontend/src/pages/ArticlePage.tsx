import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchArticleBySlug } from '../api/endpoints'
import Breadcrumb, { type BreadcrumbItem } from '../components/Breadcrumb'
import ArticleCard from '../components/ArticleCard'
import PriceWidget from '../components/PriceWidget'
import CommentSection from '../components/CommentSection'
import ArticleFAQSection from '../components/ArticleFAQSection'
import AdSlot from '../components/AdSlot'
import { useSEO } from '../hooks/useSEO'
import { buildArticleSchema, buildBreadcrumbSchema, buildFAQSchema } from '../utils/seo'
import type { ArticleDetail } from '../api/types'
import { formatDatePersian } from '../utils/apiError'
import './ArticlePage.css'

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>()
  const [article, setArticle] = useState<ArticleDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!slug) return
    window.scrollTo(0, 0)
    setIsLoading(true)
    setError(false)
    fetchArticleBySlug(slug)
      .then(setArticle)
      .catch(() => setError(true))
      .finally(() => setIsLoading(false))
  }, [slug])

  const breadcrumbItems: BreadcrumbItem[] = []
  if (article?.category.parent) {
    breadcrumbItems.push({ label: article.category.parent.name, to: `/category/${article.category.parent.slug}` })
  }
  if (article) {
    breadcrumbItems.push({ label: article.category.name, to: `/category/${article.category.slug}` })
    breadcrumbItems.push({ label: article.title })
  }

  useSEO({
    title: article?.title,
    description: article?.summary,
    image: article?.image ?? undefined,
    structuredData: article
      ? [
          buildArticleSchema(article),
          buildBreadcrumbSchema([
            { label: 'خانه', path: '/' },
            ...breadcrumbItems.map((item) => ({
              label: item.label,
              path: item.to ?? `/article/${article.slug}`,
            })),
          ]),
          ...(buildFAQSchema(article.faqs) ? [buildFAQSchema(article.faqs)!] : []),
        ]
      : undefined,
  })

  if (isLoading) {
    return <p className="page-loading">در حال بارگذاری مقاله...</p>
  }

  if (error || !article) {
    return <p className="page-empty">مقاله مورد نظر یافت نشد.</p>
  }

  return (
    <div className="article-page">
      <Breadcrumb items={breadcrumbItems} />

      <article className="container article-page__content">
        <header className="article-page__header">
          <h1>{article.title}</h1>
          <div className="article-page__meta">
            <span className="article-page__reading-time">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6" />
                <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
              مدت زمان مطالعه: {article.reading_time_minutes} دقیقه
            </span>
            <span className="text-muted">{formatDatePersian(article.published_at)}</span>
          </div>
        </header>

        {article.image && (
          <div className="article-page__image">
            <img src={article.image} alt={article.title} loading="lazy" />
          </div>
        )}

        <div className="article-page__body" dangerouslySetInnerHTML={{ __html: article.body }} />

        {article.secondary_tags.length > 0 && (
          <div className="article-page__tags">
            {article.secondary_tags.map((tag) => (
              <span key={tag.id} className="article-page__tag">
                {tag.name}
              </span>
            ))}
          </div>
        )}
      </article>

      <div className="container">
        <AdSlot slotId="article-inline-1" />
      </div>

      <div className="container">
        <ArticleFAQSection faqs={article.faqs} />
      </div>

      {article.related_articles.length > 0 && (
        <section className="container article-page__related">
          <h2 className="section-title">مطالب مشابه</h2>
          <div className="article-page__related-grid">
            {article.related_articles.map((related) => (
              <ArticleCard key={related.id} article={related} />
            ))}
          </div>
        </section>
      )}

      <section className="container article-page__prices">
        <PriceWidget layout="horizontal" />
      </section>

      <div className="container">
        <CommentSection articleId={article.id} articleSlug={article.slug} />
      </div>
    </div>
  )
}
