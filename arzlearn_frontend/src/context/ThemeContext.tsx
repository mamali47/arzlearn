import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

type Theme = 'light' | 'dark'

interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)
const STORAGE_KEY = 'arzlearn-theme'

const THEME_COLORS: Record<Theme, string> = { light: '#f4f6fb', dark: '#0f1117' }

function getInitialTheme(): Theme {
  // اسکریپت کوچکی که در index.html قبل از ری‌اکت اجرا می‌شود، همین مقدار را
  // روی <html> گذاشته است؛ از همان می‌خوانیم تا تم دو بار عوض نشود.
  const fromDom = document.documentElement.getAttribute('data-theme')
  if (fromDom === 'light' || fromDom === 'dark') return fromDom
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch {
    /* حالت مرور ناشناس بعضی مرورگرها localStorage را بلاک می‌کند */
  }
  // اگر کاربر قبلاً انتخاب نکرده، پیش‌فرض همیشه روشن (لایت) است
  return 'light'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.style.colorScheme = theme
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', THEME_COLORS[theme])
    try {
      localStorage.setItem(STORAGE_KEY, theme)
    } catch {
      /* نادیده بگیر */
    }
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'))
  }

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme باید داخل ThemeProvider استفاده شود')
  return ctx
}
