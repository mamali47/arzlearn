import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { parseApiErrors } from '../utils/apiError'
import PasswordInput from '../components/PasswordInput'
import './AuthPages.css'

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [generalError, setGeneralError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setGeneralError(null)
    setSubmitting(true)
    try {
      await login(identifier, password)
      navigate('/')
    } catch (err) {
      const parsed = parseApiErrors(err)
      setGeneralError(parsed.general ?? Object.values(parsed.fields)[0] ?? 'ورود ناموفق بود.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1>ورود به حساب کاربری</h1>

        {generalError && <p className="auth-general-error">{generalError}</p>}

        <form onSubmit={handleSubmit}>
          <div className="auth-field">
            <label htmlFor="identifier">نام کاربری یا ایمیل</label>
            <input
              id="identifier"
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="password">رمز عبور</label>
            <PasswordInput
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary auth-submit" disabled={submitting}>
            {submitting ? 'در حال ورود...' : 'ورود'}
          </button>
        </form>

        <p className="auth-switch">
          اکانت نساخته‌اید؟ <Link to="/register">ثبت‌نام کنید</Link>
        </p>
      </div>
    </div>
  )
}
