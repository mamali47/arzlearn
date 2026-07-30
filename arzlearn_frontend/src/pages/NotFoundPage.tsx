import { Link } from 'react-router-dom'

export default function NotFoundPage() {
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
