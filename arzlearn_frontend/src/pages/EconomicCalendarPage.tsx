import { useEffect, useState } from 'react'
import { fetchWeekEconomicEvents } from '../api/endpoints'
import EconomicEventRow from '../components/EconomicEventRow'
import { useSEO } from '../hooks/useSEO'
import type { EconomicEvent } from '../api/types'
import './EconomicCalendarPage.css'

function formatGregorian(dateStr: string) {
  try {
    return new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }).format(new Date(dateStr))
  } catch {
    return dateStr
  }
}

export default function EconomicCalendarPage() {
  const [events, setEvents] = useState<EconomicEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useSEO({
    title: 'تقویم اقتصادی هفتگی',
    description: 'مهم‌ترین رویدادهای اقتصادی هفته جاری به همراه پیش‌بینی و مقادیر قبلی.',
  })

  useEffect(() => {
    fetchWeekEconomicEvents()
      .then(setEvents)
      .catch(() => setEvents([]))
      .finally(() => setIsLoading(false))
  }, [])

  const groupedByDate = events.reduce<Record<string, EconomicEvent[]>>((acc, event) => {
    if (!acc[event.event_date]) acc[event.event_date] = []
    acc[event.event_date].push(event)
    return acc
  }, {})

  const sortedDates = Object.keys(groupedByDate).sort()

  return (
    <div className="economic-calendar-page">
      <div className="economic-calendar-page__hero">
        <div className="container">
          <h1>تقویم اقتصادی هفتگی</h1>
          <p>مهم‌ترین رویدادهای اقتصادی هفته جاری، به‌همراه پیش‌بینی و مقادیر قبلی</p>
        </div>
      </div>

      <div className="container economic-calendar-page__body">
        {isLoading ? (
          <p className="page-loading">در حال بارگذاری...</p>
        ) : sortedDates.length === 0 ? (
          <p className="page-empty">داده‌ای برای این هفته یافت نشد.</p>
        ) : (
          sortedDates.map((date) => {
            const dayEvents = groupedByDate[date]
            const first = dayEvents[0]
            return (
              <div key={date} className="economic-calendar-page__day">
                <div className="economic-calendar-page__day-bar">
                  <span className="economic-calendar-page__day-name">{first.day_name_fa}</span>
                  <span className="economic-calendar-page__day-dates">
                    <span>{first.shamsi_date}</span>
                    <span className="economic-calendar-page__sep">•</span>
                    <span dir="ltr">{formatGregorian(date)}</span>
                  </span>
                </div>
                <div className="economic-calendar-page__day-events card">
                  {dayEvents.map((event) => (
                    <EconomicEventRow key={event.id} event={event} />
                  ))}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
