import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchTodayEconomicEvents } from '../api/endpoints'
import EconomicEventRow from './EconomicEventRow'
import type { EconomicEvent } from '../api/types'
import './EconomicCalendarSection.css'

export default function EconomicCalendarSection() {
  const [events, setEvents] = useState<EconomicEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchTodayEconomicEvents()
      .then(setEvents)
      .catch(() => setEvents([]))
      .finally(() => setIsLoading(false))
  }, [])

  if (!isLoading && events.length === 0) return null

  return (
    <section className="economic-calendar-section">
      <div className="economic-calendar-section__header">
        <h2 className="section-title">مهم‌ترین داده‌های اقتصادی امروز</h2>
        <Link to="/economic-calendar" className="economic-calendar-section__viewall">
          مشاهده همه داده‌های اقتصادی
        </Link>
      </div>

      <div className="economic-calendar-section__card card">
        {isLoading ? (
          <p className="text-muted" style={{ padding: '12px 4px' }}>
            در حال بارگذاری...
          </p>
        ) : (
          events.map((event) => <EconomicEventRow key={event.id} event={event} />)
        )}
      </div>
    </section>
  )
}
