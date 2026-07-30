import { useRef } from 'react'
import ExchangeCard from './ExchangeCard'
import type { Exchange } from '../api/types'
import './ExchangeCarousel.css'

export default function ExchangeCarousel({ items }: { items: Exchange[] }) {
  const trackRef = useRef<HTMLDivElement>(null)

  function scrollByPage(direction: 1 | -1) {
    const track = trackRef.current
    if (!track) return
    track.scrollBy({ left: direction * track.clientWidth, behavior: 'smooth' })
  }

  if (items.length === 0) return null

  return (
    <section className="exchange-carousel">
      <div className="exchange-carousel__header">
        <h2 className="section-title">بهترین صرافی‌ها</h2>
        <div className="exchange-carousel__arrows">
          <button aria-label="صرافی‌های بعدی" onClick={() => scrollByPage(1)}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M9 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <button aria-label="صرافی‌های قبلی" onClick={() => scrollByPage(-1)}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M15 6l-6 6 6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>

      <div className="exchange-carousel__track" ref={trackRef}>
        {items.map((exchange) => (
          <div key={exchange.id} className="exchange-carousel__slide">
            <ExchangeCard exchange={exchange} />
          </div>
        ))}
      </div>
    </section>
  )
}
