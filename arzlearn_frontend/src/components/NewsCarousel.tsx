import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import ArticleCard from './ArticleCard'
import type { ArticleListItem } from '../api/types'
import './NewsCarousel.css'

interface Props {
  items: ArticleListItem[]
  viewAllHref?: string
}

export default function NewsCarousel({ items, viewAllHref }: Props) {
  const [activeIndex, setActiveIndex] = useState(0)
  const cardRefs = useRef<(HTMLDivElement | null)[]>([])

  function goTo(index: number) {
    if (items.length === 0) return
    const clamped = (index + items.length) % items.length
    setActiveIndex(clamped)
    cardRefs.current[clamped]?.scrollIntoView({
      behavior: 'smooth',
      inline: 'start',
      block: 'nearest',
    })
  }

  return (
    <section className="news-carousel">
      <div className="news-carousel__header">
        <div className="news-carousel__title-group">
          <h2 className="section-title">آخرین اخبار</h2>
          <div className="news-carousel__arrows">
            <button aria-label="خبر بعدی" onClick={() => goTo(activeIndex + 1)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M9 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <button aria-label="خبر قبلی" onClick={() => goTo(activeIndex - 1)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M15 6l-6 6 6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>

        {viewAllHref && (
          <Link to={viewAllHref} className="news-carousel__viewall">
            مشاهده همه اخبار
          </Link>
        )}
      </div>

      {items.length === 0 ? (
        <p className="text-muted">مقاله‌ای در دسته‌بندی اخبار یافت نشد.</p>
      ) : (
        <>
          <div className="news-carousel__track">
            {items.map((article, index) => (
              <div
                key={article.id}
                className="news-carousel__slide"
                ref={(el) => (cardRefs.current[index] = el)}
              >
                <ArticleCard article={article} variant="hero" />
              </div>
            ))}
          </div>

          {items.length > 1 && (
            <div className="news-carousel__dots">
              {items.map((_, index) => (
                <button
                  key={index}
                  className={`news-carousel__dot ${index === activeIndex ? 'active' : ''}`}
                  onClick={() => goTo(index)}
                  aria-label={`اسلاید ${index + 1}`}
                />
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
