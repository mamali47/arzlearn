import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { verifyEmail } from '../api/endpoints'
import './AuthPages.css'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('لینک نامعتبر است.')
      return
    }
    verifyEmail(token)
      .then((res) => {
        setStatus('success')
        setMessage(res.detail)
      })
      .catch(() => {
        setStatus('error')
        setMessage('این لینک نامعتبر یا منقضی شده است.')
      })
  }, [token])

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1>تایید ایمیل</h1>
        {status === 'loading' && <p>در حال بررسی لینک...</p>}
        {status === 'success' && <p style={{ color: 'green' }}>{message}</p>}
        {status === 'error' && <p className="auth-general-error">{message}</p>}
        <p className="auth-switch">
          <Link to="/">بازگشت به صفحه‌ی اصلی</Link>
        </p>
      </div>
    </div>
  )
}
