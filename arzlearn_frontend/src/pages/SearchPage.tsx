import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { searchArticles } from '../api/endpoints'
import ArticleCard from '../components/ArticleCard'
import type { ArticleListItem } from '../api/types'
import './SearchPage.css'

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') ?? ''
  const [results, setResults] = useState<ArticleListItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

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
