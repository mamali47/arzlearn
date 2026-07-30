import { Link } from 'react-router-dom'
import { usePrices } from '../hooks/usePrices'
import { formatNumber } from '../utils/apiError'
import type { Price, PriceSymbol } from '../api/types'
import './PriceWidget.css'

// فایل‌های لوگو باید توی frontend/public/coins/ با همین اسم‌ها باشند
// (مثلاً public/coins/btc.png). هرکدوم نبود، بجاش دایره‌ی رنگی+حرف نشون داده می‌شه.
const SYMBOL_META: Record<PriceSymbol, { color: string; short: string; logo: string; pageSlug: string }> = {
  BTC: { color: '#f7931a', short: '₿', logo: '/coins/btc.png', pageSlug: 'bitcoin' },
  ETH: { color: '#627eea', short: 'Ξ', logo: '/coins/eth.png', pageSlug: 'ethereum' },
  SOL: { color: '#14f195', short: 'S', logo: '/coins/sol.png', pageSlug: 'solana' },
  USD: { color: '#16a34a', short: '$', logo: '/coins/usd.png', pageSlug: 'dollar' },
  GOLD18: { color: '#d4af37', short: 'Au', logo: '/coins/gold.png', pageSlug: 'gold' },
}

function PriceRow({ price }: { price: Price }) {
  const meta = SYMBOL_META[price.symbol] ?? { color: '#999', short: '?', logo: '', pageSlug: '' }
  const unit = price.currency === 'USD' ? 'دلار' : 'ریال'
  const prefix = price.currency === 'USD' ? '$ ' : ''

  return (
    <li className="price-row">
      <Link to={`/price/${meta.pageSlug}`} className="price-row__link">
        <span className="price-row__icon" style={{ background: meta.color }}>
          {meta.logo ? (
            <img
              src={meta.logo}
              alt={price.name_fa}
              onError={(e) => {
                // اگر فایل لوگو پیدا نشد، همون آیکون حرفی جایگزینش می‌شه
                e.currentTarget.style.display = 'none'
                e.currentTarget.nextElementSibling?.classList.remove('price-row__icon-fallback--hidden')
              }}
            />
          ) : null}
          <span className={`price-row__icon-fallback ${meta.logo ? 'price-row__icon-fallback--hidden' : ''}`}>
            {meta.short}
          </span>
        </span>
        <div className="price-row__info">
          <span className="price-row__name">{price.name_fa}</span>
          <span className="price-row__unit text-muted">{unit}</span>
        </div>
        <div className="price-row__values">
          <span className="price-row__value">
            {prefix}
            {formatNumber(price.price_value)}
          </span>
          <span className={`price-row__change ${price.is_positive_change ? 'up' : 'down'}`}>
            {price.is_positive_change ? '▲' : '▼'} {Math.abs(Number(price.change_percent))}%
          </span>
        </div>
      </Link>
    </li>
  )
}

interface PriceWidgetProps {
  layout?: 'vertical' | 'horizontal'
}

export default function PriceWidget({ layout = 'vertical' }: PriceWidgetProps) {
  const { prices, isLoading, isConnected } = usePrices()

  return (
    <div className={`price-widget card price-widget--${layout}`}>
      <div className="price-widget__header">
        <h3 className="section-title">قیمت لحظه‌ای</h3>
        <span className={`price-widget__live ${isConnected ? 'on' : 'off'}`}>
          <span className="dot" />
          {isConnected ? 'زنده' : 'در حال اتصال...'}
        </span>
      </div>

      {isLoading && prices.length === 0 ? (
        <p className="text-muted" style={{ padding: '12px 4px' }}>
          در حال دریافت قیمت‌ها...
        </p>
      ) : (
        <ul className="price-widget__list">
          {prices.map((price) => (
            <PriceRow key={price.symbol} price={price} />
          ))}
        </ul>
      )}
    </div>
  )
}
