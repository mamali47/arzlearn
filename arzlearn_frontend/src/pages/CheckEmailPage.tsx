import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { resendVerificationEmail } from '../api/endpoints'
import './AuthPages.css'

export default function CheckEmailPage() {
  const location = useLocation()
  const email = (location.state as { email?: string } | null)?.email

  const [sending, setSending] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleResend() {
    setSending(true)
    setMessage(null)
    setError(null)
    try {
      const res = await resendVerificationEmail()
      setMessage(res.detail)
    } catch {
      setError('ارسال دوباره ناموفق بود. اگه قبلاً ایمیلتون تایید شده، نیازی به این کار نیست.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1>ثبت‌نام با موفقیت انجام شد 🎉</h1>
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
          لطفاً صندوق ورودی (و پوشه‌ی Spam) ایمیلتون رو چک کنید و روی لینک تایید کلیک کنید.
        </p>

        {message && <p style={{ color: 'green' }}>{message}</p>}
        {error && <p className="auth-general-error">{error}</p>}

        <button
          type="button"
          className="btn btn-primary auth-submit"
          onClick={handleResend}
          disabled={sending}
        >
          {sending ? 'در حال ارسال...' : 'ارسال دوباره ایمیل تایید'}
        </button>

        <p className="auth-switch">
          <Link to="/">رفتن به صفحه‌ی اصلی</Link>
        </p>
      </div>
    </div>
  )
}
