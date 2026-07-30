import StarRating from './StarRating'
import type { Exchange } from '../api/types'
import './ExchangeCard.css'

export default function ExchangeCard({ exchange }: { exchange: Exchange }) {
  return (
    <div className="exchange-card card">
      <div className="exchange-card__logo">
        {exchange.logo ? (
          <img src={exchange.logo} alt={exchange.name} loading="lazy" />
        ) : (
          <div className="exchange-card__logo-placeholder">{exchange.name.charAt(0)}</div>
        )}
      </div>

      <h3 className="exchange-card__name">{exchange.name}</h3>

      <StarRating rating={Number(exchange.rating)} />

      <div className="exchange-card__fees">
        <span className="exchange-card__fee-item">
          <span className="text-muted">کارمزد میکر:</span>
          <span className="exchange-card__fee-value">{exchange.maker_fee}</span>
        </span>
        <span className="exchange-card__fee-item">
          <span className="text-muted">کارمزد تیکر:</span>
          <span className="exchange-card__fee-value">{exchange.taker_fee}</span>
        </span>
      </div>

      <p className="exchange-card__description">{exchange.short_description}</p>

      <a
        href={exchange.registration_url}
        target="_blank"
        rel="noopener noreferrer"
        className="btn btn-primary exchange-card__cta"
      >
        اکنون ثبت‌نام کنید
      </a>
    </div>
  )
}
