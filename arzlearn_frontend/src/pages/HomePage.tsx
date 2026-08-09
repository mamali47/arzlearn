import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchExchanges, fetchLatestAnalysis, fetchLatestNews } from '../api/endpoints'
import NewsCarousel from '../components/NewsCarousel'
import AnalysisCard from '../components/AnalysisCard'
import PriceWidget from '../components/PriceWidget'
import ExchangeCarousel from '../components/ExchangeCarousel'
import EconomicCalendarSection from '../components/EconomicCalendarSection'
import AdSlot from '../components/AdSlot'
import { useSEO } from '../hooks/useSEO'
import { buildOrganizationSchema, buildWebsiteSchema } from '../utils/seo'
import type { ArticleListItem, Exchange } from '../api/types'
import './HomePage.css'

export default function HomePage() {
  const [news, setNews] = useState<ArticleListItem[]>([])
  const [analysis, setAnalysis] = useState<ArticleListItem[]>([])
  const [exchanges, setExchanges] = useState<Exchange[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useSEO({
    description: 'اخبار، تحلیل و قیمت لحظه‌ای بیت‌کوین، اتریوم، سولانا، دلار و طلا در ارزلرن.',
    structuredData: [buildOrganizationSchema(), buildWebsiteSchema()],
  })

  useEffect(() => {
    Promise.all([fetchLatestNews(), fetchLatestAnalysis(), fetchExchanges()])
      .then(([newsData, analysisData, exchangesData]) => {
        setNews(newsData)
        setAnalysis(analysisData)
        setExchanges(exchangesData)
      })
      .finally(() => setIsLoading(false))
  }, [])

  // مقاله ممکن است متعلق به یک زیردسته باشد (مثلاً «اخبار بیت‌کوین»)؛
  // در این صورت باید لینک «مشاهده همه» به دسته‌بندی مادر («اخبار») برود، نه به زیردسته.
  function getTopCategorySlug(article?: ArticleListItem): string | undefined {
    if (!article) return undefined
    return article.category.parent?.slug ?? article.category.slug
  }

  const newsCategorySlug = getTopCategorySlug(news[0])
  const analysisCategorySlug = getTopCategorySlug(analysis[0])

  return (
    <div className="home-page container">
      <NewsCarousel items={news} viewAllHref={newsCategorySlug ? `/category/${newsCategorySlug}` : undefined} />

      <AdSlot slotId="home-hero" />

      <div className="home-page__grid">
        <section className="home-page__analysis">
          <div className="home-page__section-header">
            <h2 className="section-title">آخرین تحلیل‌ها</h2>
          </div>

          {isLoading ? (
            <p className="text-muted">در حال بارگذاری...</p>
          ) : analysis.length === 0 ? (
            <p className="text-muted">مقاله‌ای در دسته‌بندی تحلیل یافت نشد.</p>
          ) : (
            <div className="home-page__analysis-list">
              {analysis.map((article) => (
                <AnalysisCard key={article.id} article={article} />
              ))}
            </div>
          )}

          {analysisCategorySlug && (
            <Link to={`/category/${analysisCategorySlug}`} className="btn btn-outline home-page__viewall">
              مشاهده همه تحلیل‌ها
            </Link>
          )}
        </section>

        <aside className="home-page__sidebar">
          <div className="home-page__section-header home-page__section-header--ghost" aria-hidden="true">
            <h2 className="section-title">قیمت لحظه‌ای</h2>
          </div>
          <PriceWidget />
        </aside>
      </div>

      <ExchangeCarousel items={exchanges} />

      <EconomicCalendarSection />
    </div>
  )
}
