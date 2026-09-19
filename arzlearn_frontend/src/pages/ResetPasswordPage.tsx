import { useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { confirmPasswordReset } from '../api/endpoints'
import { parseApiErrors } from '../utils/apiError'
import PasswordInput from '../components/PasswordInput'
import './AuthPages.css'
import { useSEO } from '../hooks/useSEO'

function getPasswordIssues(password: string): string[] {
  const issues: string[] = []
  if (password.length < 8) issues.push('حداقل ۸ کاراکتر')
  if (!/[A-Z]/.test(password)) issues.push('حداقل یک حرف بزرگ انگلیسی')
  if (!/[a-z]/.test(password)) issues.push('حداقل یک حرف کوچک انگلیسی')
  if (!/[0-9]/.test(password)) issues.push('حداقل یک عدد')
  return issues
}

export default function ResetPasswordPage() {
  useSEO({
    title: 'تعیین رمز عبور جدید',
    description: 'تعیین رمز عبور جدید برای حساب کاربری ارزلرن.',
    url: '/reset-password',
    noindex: true,
  })

  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') || ''
  const token = searchParams.get('token') || ''

  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [generalError, setGeneralError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  const passwordIssues = useMemo(() => getPasswordIssues(password), [password])

  if (!uid || !token) {
    return (
      <div className="auth-page">
        <div className="auth-card card">
          <h1>لینک نامعتبر است</h1>
          <p>این لینک بازیابی رمز عبور معتبر نیست. لطفاً دوباره درخواست بدهید.</p>
          <p className="auth-switch">
            <Link to="/forgot-password">درخواست لینک جدید</Link>
          </p>
        </div>
      </div>
    )
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setGeneralError(null)

    const errors: Record<string, string> = {}
    if (passwordIssues.length > 0) {
      errors.new_password = `رمز عبور باید شامل موارد زیر باشد: ${passwordIssues.join('، ')}`
    }
    if (password !== passwordConfirm) {
      errors.new_password_confirm = 'رمز عبور و تکرار آن یکسان نیستند.'
    }
    setFieldErrors(errors)
    if (Object.keys(errors).length > 0) return

    setSubmitting(true)
    try {
      await confirmPasswordReset({
        uid,
        token,
        new_password: password,
        new_password_confirm: passwordConfirm,
      })
      setSuccess(true)
      setTimeout(() => navigate('/login'), 2500)
    } catch (err) {
      const parsed = parseApiErrors(err)
      setFieldErrors(parsed.fields)
      setGeneralError(parsed.general || 'این لینک نامعتبر یا منقضی شده است.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1>تعیین رمز عبور جدید</h1>

        {success ? (
          <p style={{ color: 'green' }}>
            رمز عبور با موفقیت تغییر کرد. در حال انتقال به صفحه‌ی ورود...
          </p>
        ) : (
          <>
            {generalError && <p className="auth-general-error">{generalError}</p>}
            <form onSubmit={handleSubmit} noValidate>
              <div className="auth-field">
                <label htmlFor="password">رمز عبور جدید</label>
                <PasswordInput
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                {fieldErrors.new_password && <p className="auth-field__error">{fieldErrors.new_password}</p>}
              </div>

              <div className="auth-field">
                <label htmlFor="password_confirm">تکرار رمز عبور جدید</label>
                <PasswordInput
                  id="password_confirm"
                  value={passwordConfirm}
                  onChange={(e) => setPasswordConfirm(e.target.value)}
                  required
                />
                {fieldErrors.new_password_confirm && (
                  <p className="auth-field__error">{fieldErrors.new_password_confirm}</p>
                )}
              </div>

              <button type="submit" className="btn btn-primary auth-submit" disabled={submitting}>
                {submitting ? 'در حال ثبت...' : 'تغییر رمز عبور'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
