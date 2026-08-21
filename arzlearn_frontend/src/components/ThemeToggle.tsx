import { useTheme } from '../context/ThemeContext'
import './ThemeToggle.css'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={toggleTheme}
      aria-label={isDark ? 'رفتن به حالت روشن' : 'رفتن به حالت تاریک'}
      title={isDark ? 'حالت روشن' : 'حالت تاریک'}
    >
      <span className={`theme-toggle__icon ${isDark ? 'theme-toggle__icon--dark' : ''}`}>
        {isDark ? '☀️' : '🌙'}
      </span>
    </button>
  )
}
