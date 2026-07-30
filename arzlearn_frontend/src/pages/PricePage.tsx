import { useParams } from 'react-router-dom'
import { usePrices } from '../hooks/usePrices'
import { useSEO } from '../hooks/useSEO'
import { buildFAQSchema } from '../utils/seo'
import { formatNumber } from '../utils/apiError'
import Breadcrumb from '../components/Breadcrumb'
import './PricePage.css'

interface RouteInfo {
  symbol: string
  nameFa: string
}

const SYMBOL_ROUTES: Record<string, RouteInfo> = {
  bitcoin: { symbol: 'BTC', nameFa: 'بیت‌کوین' },
  ethereum: { symbol: 'ETH', nameFa: 'اتریوم' },
  solana: { symbol: 'SOL', nameFa: 'سولانا' },
  dollar: { symbol: 'USD', nameFa: 'دلار' },
  gold: { symbol: 'GOLD18', nameFa: 'طلای ۱۸ عیار' },
}

export default function PricePage() {
  const { slug } = useParams<{ slug: string }>()
  const routeInfo = slug ? SYMBOL_ROUTES[slug] : undefined
  const { prices, isLoading } = usePrices()

  const price = routeInfo ? prices.find((p) => p.symbol === routeInfo.symbol) : undefined
  const unitLabel = price?.currency === 'USD' ? 'دلار' : 'ریال'
  const priceText = price ? `${formatNumber(price.price_value)} ${unitLabel}` : null

  const title = routeInfo ? `قیمت ${routeInfo.nameFa} امروز` : 'قیمت لحظه‌ای'

  const faqs = routeInfo
    ? [
        {
          id: 1,
          question: `قیمت ${routeInfo.nameFa} امروز چقدر است؟`,
          answer: priceText
            ? `قیمت لحظه‌ای ${routeInfo.nameFa} در حال حاضر ${priceText} است. این قیمت به‌صورت خودکار و لحظه‌ای در ارزلرن بروزرسانی می‌شود.`
            : `قیمت لحظه‌ای ${routeInfo.nameFa} در حال دریافت است؛ چند لحظه صبر کنید.`,
        },
        {
          id: 2,
          question: `قیمت ${routeInfo.nameFa} هر چند وقت یک‌بار بروزرسانی می‌شود؟`,
          answer: `قیمت ${routeInfo.nameFa} در ارزلرن هر دقیقه به‌صورت خودکار بروزرسانی می‌شود تا همیشه جدیدترین نرخ بازار را مشاهده کنید.`,
        },
      ]
    : []

  useSEO({
    title,
    description: routeInfo
      ? `قیمت لحظه‌ای ${routeInfo.nameFa} به ${unitLabel} - بروزرسانی خودکار هر دقیقه در ارزلرن.`
      : undefined,
    structuredData: faqs.length > 0 ? [buildFAQSchema(faqs)!] : undefined,
  })

  if (!routeInfo) {
    return <p className="page-empty">دارایی مورد نظر یافت نشد.</p>
  }

  return (
    <div className="price-page">
      <Breadcrumb items={[{ label: title }]} />

      <div className="container price-page__content">
        <h1>{title}</h1>

        {isLoading && !price ? (
          <p className="text-muted">در حال دریافت قیمت...</p>
        ) : (
          <div className="price-page__value-box card">
            <span className="price-page__value">{priceText ?? '—'}</span>
            {price && (
              <span className={`price-page__change ${price.is_positive_change ? 'up' : 'down'}`}>
                {price.is_positive_change ? '▲' : '▼'} {Math.abs(Number(price.change_percent))}%
              </span>
            )}
          </div>
        )}

        <div className="price-page__faqs">
          {faqs.map((faq) => (
            <div key={faq.id} className="price-page__faq-item">
              <h2>{faq.question}</h2>
              <p>{faq.answer}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
