import { useState } from 'react'
import { Link } from 'react-router-dom'
import { requestPasswordReset } from '../api/endpoints'
import { parseApiErrors } from '../utils/apiError'
import './AuthPages.css'
import { useSEO } from '../hooks/useSEO'

export default function ForgotPasswordPage() {
  useSEO({
    title: 'فراموشی رمز عبور',
    description: 'بازیابی رمز عبور حساب کاربری ارزلرن.',
    url: '/forgot-password',
    noindex: true,
  })

  const [email, setEmail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    setSubmitting(true)
    try {
      const res = await requestPasswordReset(email)
      setMessage(res.detail)
    } catch (err) {
      const parsed = parseApiErrors(err)
      setError(parsed.general || 'خطایی رخ داد، دوباره تلاش کنید.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1>فراموشی رمز عبور</h1>
        <p className="auth-field__hint">
          ایمیلی که با آن ثبت‌نام کرده‌اید را وارد کنید تا لینک بازیابی رمز عبور برایتان ارسال شود.
        </p>

        {message && <p style={{ color: 'green' }}>{message}</p>}
        {error && <p className="auth-general-error">{error}</p>}

        {!message && (
          <form onSubmit={handleSubmit} noValidate>
            <div className="auth-field">
              <label htmlFor="email">ایمیل</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary auth-submit" disabled={submitting}>
              {submitting ? 'در حال ارسال...' : 'ارسال لینک بازیابی'}
            </button>
          </form>
        )}

        <p className="auth-switch">
          <Link to="/login">بازگشت به صفحه‌ی ورود</Link>
        </p>
      </div>
    </div>
  )
}
