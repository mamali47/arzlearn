import { useState, forwardRef } from 'react'
import './PasswordInput.css'

type Props = React.InputHTMLAttributes<HTMLInputElement>

/**
 * فیلد رمز عبور با آیکون چشم برای نمایش/مخفی‌کردن متن وارد شده.
 */
const PasswordInput = forwardRef<HTMLInputElement, Props>(function PasswordInput(props, ref) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="password-input">
      <input {...props} ref={ref} type={visible ? 'text' : 'password'} />
      <button
        type="button"
        className="password-input__toggle"
        onClick={() => setVisible((v) => !v)}
        aria-label={visible ? 'مخفی کردن رمز عبور' : 'نمایش رمز عبور'}
        tabIndex={-1}
      >
        {visible ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              d="M3 3l18 18M10.58 10.58a2 2 0 002.83 2.83M9.88 5.09A9.77 9.77 0 0112 5c5 0 9 4 10 7-.37 1.15-1.1 2.4-2.13 3.5M6.5 6.64C4.3 8.02 2.7 10 2 12c1 3 5 7 10 7 1.35 0 2.63-.28 3.79-.77"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.7" />
          </svg>
        )}
      </button>
    </div>
  )
})

export default PasswordInput
