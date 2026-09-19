import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { searchArticles } from '../api/endpoints'
import ArticleCard from '../components/ArticleCard'
import { useSEO } from '../hooks/useSEO'
import type { ArticleListItem } from '../api/types'
import './SearchPage.css'

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') ?? ''
  const [results, setResults] = useState<ArticleListItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // صفحات نتایج جستجو نباید ایندکس شوند: محتوای یکتا ندارند و به ازای هر
  // عبارت جستجو یک URL جدید می‌سازند (محتوای تکراری + هدر رفتن crawl budget).
  useSEO({
    title: query ? `نتایج جستجو برای «${query}»` : 'جستجو',
    description: 'جستجو در اخبار، تحلیل‌ها و آموزش‌های ارزلرن.',
    url: '/search',
    noindex: true,
  })

  useEffect(() => {
    if (!query) {
      setResults([])
      setIsLoading(false)
      return
    }
    setIsLoading(true)
    searchArticles(query)
      .then((data) => setResults(data.results))
      .finally(() => setIsLoading(false))
  }, [query])

  return (
    <div className="search-page container">
      <h1>نتایج جستجو برای «{query}»</h1>

      {isLoading ? (
        <p className="page-loading">در حال جستجو...</p>
      ) : results.length === 0 ? (
        <p className="page-empty">نتیجه‌ای برای این عبارت یافت نشد.</p>
      ) : (
        <div className="search-page__grid">
          {results.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}
    </div>
  )
}
