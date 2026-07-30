import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { parseApiErrors } from '../utils/apiError'
import PasswordInput from '../components/PasswordInput'
import './AuthPages.css'

const USERNAME_REGEX = /^[a-zA-Z0-9_.]+$/

function getPasswordIssues(password: string): string[] {
  const issues: string[] = []
  if (password.length < 8) issues.push('حداقل ۸ کاراکتر')
  if (!/[A-Z]/.test(password)) issues.push('حداقل یک حرف بزرگ انگلیسی')
  if (!/[a-z]/.test(password)) issues.push('حداقل یک حرف کوچک انگلیسی')
  if (!/[0-9]/.test(password)) issues.push('حداقل یک عدد')
  return issues
}

export default function RegisterPage() {
  const [username, setUsername] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [generalError, setGeneralError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const { register } = useAuth()
  const navigate = useNavigate()

  const usernameError =
    username.length > 0 && !USERNAME_REGEX.test(username)
      ? 'نام کاربری باید فقط شامل حروف انگلیسی، اعداد، نقطه و آندرلاین باشد.'
      : fieldErrors.username

  const passwordIssues = useMemo(() => getPasswordIssues(password), [password])
  const passwordsMatch = password.length > 0 && passwordConfirm.length > 0 && password === passwordConfirm

  const confirmClassName = passwordsMatch ? 'valid' : 'invalid'

  function validateBeforeSubmit(): boolean {
    const errors: Record<string, string> = {}

    if (!displayName.trim()) {
      errors.display_name = 'نام نمایشی نمی‌تواند خالی باشد.'
    }
    if (!USERNAME_REGEX.test(username)) {
      errors.username = 'نام کاربری باید فقط شامل حروف انگلیسی، اعداد، نقطه و آندرلاین باشد.'
    }
    if (passwordIssues.length > 0) {
      errors.password = `رمز عبور باید شامل موارد زیر باشد: ${passwordIssues.join('، ')}`
    }
    if (password !== passwordConfirm) {
      errors.password_confirm = 'رمز عبور و تکرار آن یکسان نیستند.'
    }

    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setGeneralError(null)

    if (!validateBeforeSubmit()) return

    setSubmitting(true)
    try {
      await register(username, displayName, email, password, passwordConfirm)
      navigate('/')
    } catch (err) {
      const parsed = parseApiErrors(err)
      setFieldErrors(parsed.fields)
      if (parsed.general) setGeneralError(parsed.general)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1>ثبت‌نام در ارزلرن</h1>

        {generalError && <p className="auth-general-error">{generalError}</p>}

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
            {fieldErrors.email && <p className="auth-field__error">{fieldErrors.email}</p>}
          </div>

          <div className="auth-field">
            <label htmlFor="display_name">نام نمایشی (فارسی یا انگلیسی)</label>
            <input
              id="display_name"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="مثلاً: علی محمدی یا Ali M."
              required
            />
            <p className="auth-field__hint">
              این نام زیر دیدگاه‌هایتان نمایش داده می‌شود (نه نام کاربری ورود).
            </p>
            {fieldErrors.display_name && <p className="auth-field__error">{fieldErrors.display_name}</p>}
          </div>

          <div className="auth-field">
            <label htmlFor="username">نام کاربری (فقط انگلیسی)</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={username.length > 0 ? (usernameError ? 'invalid' : 'valid') : ''}
              required
            />
            {usernameError && <p className="auth-field__error">{usernameError}</p>}
          </div>

          <div className="auth-field">
            <label htmlFor="password">رمز عبور</label>
            <PasswordInput
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <p className="auth-field__hint">
              رمز عبور باید حداقل ۸ کاراکتر و شامل حرف بزرگ، حرف کوچک و عدد انگلیسی باشد.
            </p>
            {fieldErrors.password && <p className="auth-field__error">{fieldErrors.password}</p>}
          </div>

          <div className="auth-field">
            <label htmlFor="password_confirm">تکرار رمز عبور</label>
            <PasswordInput
              id="password_confirm"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              className={confirmClassName}
              required
            />
            {fieldErrors.password_confirm && <p className="auth-field__error">{fieldErrors.password_confirm}</p>}
          </div>

          <button type="submit" className="btn btn-primary auth-submit" disabled={submitting}>
            {submitting ? 'در حال ثبت‌نام...' : 'ثبت‌نام'}
          </button>
        </form>

        <p className="auth-switch">
          قبلاً ثبت‌نام کرده‌اید؟ <Link to="/login">وارد شوید</Link>
        </p>
      </div>
    </div>
  )
}
