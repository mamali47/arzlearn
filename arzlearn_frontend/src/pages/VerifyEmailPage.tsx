import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './AuthPages.css'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const { completeEmailVerification } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('لینک نامعتبر است.')
      return
    }
    completeEmailVerification(token)
      .then(() => {
        setStatus('success')
        setMessage('ایمیل شما با موفقیت تایید شد و اکانتتان ساخته شد. در حال انتقال...')
        setTimeout(() => navigate('/'), 2000)
      })
      .catch(() => {
        setStatus('error')
        setMessage('این لینک نامعتبر یا منقضی شده است. لطفاً دوباره ثبت‌نام کنید.')
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1>تایید ایمیل</h1>
        {status === 'loading' && <p>در حال بررسی لینک و ساخت اکانت...</p>}
        {status === 'success' && <p style={{ color: 'green' }}>{message}</p>}
        {status === 'error' && (
          <>
            <p className="auth-general-error">{message}</p>
            <p className="auth-switch">
              <Link to="/register">ثبت‌نام دوباره</Link>
            </p>
          </>
        )}
        <p className="auth-switch">
          <Link to="/">بازگشت به صفحه‌ی اصلی</Link>
        </p>
      </div>
    </div>
  )
}
