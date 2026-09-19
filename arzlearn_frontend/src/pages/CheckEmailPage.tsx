import { Link, useLocation } from 'react-router-dom'
import './AuthPages.css'
import { useSEO } from '../hooks/useSEO'

export default function CheckEmailPage() {
  useSEO({
    title: 'ایمیلتان را بررسی کنید',
    description: 'لینک تایید به ایمیل شما ارسال شد.',
    url: '/check-email',
    noindex: true,
  })

  const location = useLocation()
  const email = (location.state as { email?: string } | null)?.email

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1>یک قدم تا تکمیل ثبت‌نام 📬</h1>
        <p>
          {email ? (
            <>
              یک ایمیل تایید به آدرس <strong>{email}</strong> ارسال شد.
            </>
          ) : (
            <>یک ایمیل تایید برای شما ارسال شد.</>
          )}
        </p>
        <p className="auth-field__hint">
          لطفاً صندوق ورودی (و پوشه‌ی Spam) ایمیلتان را چک کنید و روی لینک
          تایید کلیک کنید. تا وقتی این کار را نکنید، اکانتتان ساخته نمی‌شود.
        </p>
        <p className="auth-field__hint">
          این لینک تا ۲۴ ساعت معتبر است. اگر منقضی شد یا ایمیل را پیدا
          نکردید، کافی است دوباره فرم ثبت‌نام را پر کنید.
        </p>

        <p className="auth-switch">
          <Link to="/">رفتن به صفحه‌ی اصلی</Link>
        </p>
      </div>
    </div>
  )
}
