import './StarRating.css'

const STAR_COUNT = 5
const STAR_SIZE = 18
const STAR_GAP = 3
const ROW_WIDTH = STAR_COUNT * STAR_SIZE + (STAR_COUNT - 1) * STAR_GAP

const STAR_PATH =
  'M12 2.5l2.9 6.06 6.6.87-4.86 4.6 1.27 6.6L12 17.9l-5.91 2.73 1.27-6.6-4.86-4.6 6.6-.87L12 2.5z'

function StarRow({ color }: { color: string }) {
  return (
    <span className="star-rating__row">
      {Array.from({ length: STAR_COUNT }).map((_, i) => (
        <svg key={i} width={STAR_SIZE} height={STAR_SIZE} viewBox="0 0 24 24" fill={color}>
          <path d={STAR_PATH} />
        </svg>
      ))}
    </span>
  )
}

/**
 * نمایش امتیاز از ۵ با ستاره؛ اعداد اعشاری (مثل 4.5) هم پشتیبانی می‌شود.
 * لایه‌ی طلایی با clip-path برش می‌خورد (نه overflow:hidden ساده)، چون
 * clip-path مستقل از جهت صفحه (RTL/LTR) و چیدمان flex داخلی است و همیشه
 * دقیقاً بر اساس عرض فیزیکی خودِ باکس برش می‌زند.
 */
export default function StarRating({ rating }: { rating: number }) {
  const clamped = Math.max(0, Math.min(5, rating))
  const fillWidth = (clamped / STAR_COUNT) * ROW_WIDTH

  return (
    <span className="star-rating" role="img" aria-label={`امتیاز ${clamped} از ۵`}>
      <span className="star-rating__stars" style={{ width: ROW_WIDTH, height: STAR_SIZE }}>
        <span className="star-rating__base">
          <StarRow color="var(--color-border)" />
        </span>
        <span
          className="star-rating__fill"
          style={{ clipPath: `inset(0 ${ROW_WIDTH - fillWidth}px 0 0)` }}
        >
          <StarRow color="#f5a623" />
        </span>
      </span>
      <span className="star-rating__value">{clamped.toFixed(1)}</span>
    </span>
  )
}
