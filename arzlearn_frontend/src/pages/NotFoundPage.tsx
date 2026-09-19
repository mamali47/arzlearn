import { Link } from 'react-router-dom'
import { useSEO } from '../hooks/useSEO'

export default function NotFoundPage() {
  useSEO({
    title: 'صفحه پیدا نشد',
    description: 'صفحه‌ای که دنبالش بودید پیدا نشد.',
    noindex: true,
  })

  return (
    <div className="page-empty">
      <h1 style={{ fontSize: 40, margin: 0 }}>۴۰۴</h1>
      <p>صفحه مورد نظر یافت نشد.</p>
      <Link to="/" className="btn btn-primary">
        بازگشت به صفحه اصلی
      </Link>
    </div>
  )
}
