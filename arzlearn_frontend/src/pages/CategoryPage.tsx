import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchCategoryArticles } from '../api/endpoints'
import Breadcrumb from '../components/Breadcrumb'
import { useSEO } from '../hooks/useSEO'
import { buildBreadcrumbSchema } from '../utils/seo'
import type { ArticleListItem, Category, Paginated } from '../api/types'
import { formatDatePersian } from '../utils/apiError'
import './CategoryPage.css'

export default function CategoryPage() {
  const { slug } = useParams<{ slug: string }>()
  const [data, setData] = useState<(Paginated<ArticleListItem> & { category?: Category }) | null>(null)
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!slug) return
    setIsLoading(true)
    setError(false)
    fetchCategoryArticles(slug, page)
      .then(setData)
      .catch(() => setError(true))
      .finally(() => setIsLoading(false))
  }, [slug, page])

  const categoryName = data?.category?.name ?? ''

  useSEO({
    title: categoryName || undefined,
    description: categoryName ? `آخرین مقالات دسته‌بندی ${categoryName} در ارزلرن` : undefined,
    structuredData:
      categoryName && slug
        ? buildBreadcrumbSchema([
            { label: 'خانه', path: '/' },
            { label: categoryName, path: `/category/${slug}` },
          ])
        : undefined,
  })

  if (isLoading && !data) {
    return <p className="page-loading">در حال بارگذاری...</p>
  }

  if (error || !data) {
    return <p className="page-empty">دسته‌بندی مورد نظر یافت نشد.</p>
  }

  return (
    <div className="category-page">
      <Breadcrumb items={[{ label: categoryName }]} />

      <div className="container">
        <h1 className="category-page__title">{categoryName}</h1>

        {data.results.length === 0 ? (
          <p className="page-empty">مقاله‌ای در این دسته‌بندی یافت نشد.</p>
        ) : (
          <div className="category-page__list">
            {data.results.map((article) => (
              <article key={article.id} className="category-item card">
                <Link to={`/article/${article.slug}`} className="category-item__image">
                  {article.image ? (
                    <img src={article.image} alt={article.title} loading="lazy" />
                  ) : (
                    <div className="category-item__placeholder" />
                  )}
                </Link>
                <div className="category-item__body">
                  <Link to={`/article/${article.slug}`}>
                    <h2>{article.title}</h2>
                  </Link>
                  <p className="text-muted">{article.summary}</p>
                  <div className="category-item__footer">
                    <span className="text-muted">{formatDatePersian(article.published_at)}</span>
                    <Link to={`/article/${article.slug}`} className="btn btn-outline">
                      ادامه مطلب
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}

        {(data.next || data.previous) && (
          <div className="category-page__pagination">
            <button className="btn btn-outline" disabled={!data.previous} onClick={() => setPage((p) => p - 1)}>
              قبلی
            </button>
            <span className="text-muted">صفحه {page}</span>
            <button className="btn btn-outline" disabled={!data.next} onClick={() => setPage((p) => p + 1)}>
              بعدی
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
