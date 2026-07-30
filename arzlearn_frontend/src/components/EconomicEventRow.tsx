import type { EconomicEvent } from '../api/types'
import './EconomicEventRow.css'

const IMPORTANCE_LABELS: Record<string, string> = {
  high: 'بسیار مهم',
  medium: 'مهم',
  low: 'کم‌اهمیت',
}

export default function EconomicEventRow({ event }: { event: EconomicEvent }) {
  return (
    <div className="economic-event-row">
      <span className={`economic-event-row__dot economic-event-row__dot--${event.importance}`} />

      <div className="economic-event-row__main">
        <div className="economic-event-row__title-line">
          <span className="economic-event-row__country">{event.country}</span>
          <span className="economic-event-row__title">{event.title}</span>
        </div>
        <span className={`economic-event-row__badge economic-event-row__badge--${event.importance}`}>
          {IMPORTANCE_LABELS[event.importance] ?? event.importance}
        </span>
      </div>

      <div className="economic-event-row__values">
        {event.event_time && <span className="economic-event-row__time">{event.event_time.slice(0, 5)}</span>}
        <div className="economic-event-row__numbers">
          {event.actual && (
            <span>
              <b>واقعی:</b> {event.actual}
            </span>
          )}
          {event.forecast && (
            <span>
              <b>پیش‌بینی:</b> {event.forecast}
            </span>
          )}
          {event.previous && (
            <span>
              <b>قبلی:</b> {event.previous}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
