import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchCategories } from '../api/endpoints'
import { useAuth } from '../context/AuthContext'
import type { Category } from '../api/types'
import './Header.css'

export default function Header() {
  const [categories, setCategories] = useState<Category[]>([])
  const [openDropdown, setOpenDropdown] = useState<number | null>(null)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [expandedMobileCategories, setExpandedMobileCategories] = useState<number[]>([])
  const [searchValue, setSearchValue] = useState('')
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const closeTimer = useRef<number | null>(null)

  useEffect(() => {
    fetchCategories()
      .then(setCategories)
      .catch(() => setCategories([]))
  }, [])

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault()
    const q = searchValue.trim()
    if (q) {
      navigate(`/search?q=${encodeURIComponent(q)}`)
      setMobileOpen(false)
    }
  }

  function openMenu(id: number) {
    if (closeTimer.current) window.clearTimeout(closeTimer.current)
    setOpenDropdown(id)
  }

  function scheduleClose() {
    closeTimer.current = window.setTimeout(() => setOpenDropdown(null), 150)
  }

  function toggleMobileCategory(id: number) {
    setExpandedMobileCategories((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    )
  }

  function closeMobileMenu() {
    setMobileOpen(false)
    setExpandedMobileCategories([])
  }

  async function handleLogout() {
    await logout()
    closeMobileMenu()
    navigate('/')
  }

  return (
    <header className="site-header">
      <div className="container site-header__inner">
        {/* همبرگری - فقط موبایل */}
        <button
          className="hamburger-btn"
          aria-label="منو"
          onClick={() => setMobileOpen((v) => !v)}
        >
          <span />
          <span />
          <span />
        </button>

        {/* لوگو */}
        <Link to="/" className="site-logo" onClick={closeMobileMenu}>
          <img src="/logo.png" alt="ارزلرن" className="site-logo__image" />
          <span>ارزلرن</span>
        </Link>

        {/* دسته‌بندی‌ها - دسکتاپ */}
        <nav className="main-nav">
          <ul>
            {categories.map((cat) => (
              <li
                key={cat.id}
                onMouseEnter={() => openMenu(cat.id)}
                onMouseLeave={scheduleClose}
              >
                <Link to={`/category/${cat.slug}`}>{cat.name}</Link>
                {cat.children.length > 0 && openDropdown === cat.id && (
                  <ul className="dropdown">
                    {cat.children.map((child) => (
                      <li key={child.id}>
                        <Link to={`/category/${child.slug}`}>{child.name}</Link>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </nav>

        {/* سرچ + ورود/ثبت‌نام - دسکتاپ / خوش‌آمدید - موبایل */}
        <div className="header-actions">
          <form className="search-box" onSubmit={handleSearchSubmit}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
              <path d="M20 20L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            <input
              type="text"
              placeholder="جستجو..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
            />
          </form>

          {user ? (
            <div className="auth-box">
              <span className="username">خوش‌آمدید {user.display_name}</span>
              <button className="btn btn-outline desktop-only" onClick={handleLogout}>
                خروج از حساب کاربری
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn btn-primary">
              ورود / ثبت‌نام
            </Link>
          )}
        </div>
      </div>

      {/* منوی موبایل */}
      {mobileOpen && (
        <div className="mobile-menu">
          <form className="search-box mobile" onSubmit={handleSearchSubmit}>
            <input
              type="text"
              placeholder="جستجو..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
            />
            <button type="submit" className="btn btn-primary">
              جستجو
            </button>
          </form>

          <ul className="mobile-categories">
            {categories.map((cat) => {
              const hasChildren = cat.children.length > 0
              const isExpanded = expandedMobileCategories.includes(cat.id)
              return (
                <li key={cat.id}>
                  <div className="mobile-categories__row">
                    <Link to={`/category/${cat.slug}`} onClick={closeMobileMenu}>
                      {cat.name}
                    </Link>
                    {hasChildren && (
                      <button
                        type="button"
                        className={`mobile-categories__toggle ${isExpanded ? 'mobile-categories__toggle--open' : ''}`}
                        aria-label={`نمایش زیردسته‌های ${cat.name}`}
                        onClick={() => toggleMobileCategory(cat.id)}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path
                            d="M6 9l6 6 6-6"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </button>
                    )}
                  </div>
                  {hasChildren && isExpanded && (
                    <ul>
                      {cat.children.map((child) => (
                        <li key={child.id}>
                          <Link to={`/category/${child.slug}`} onClick={closeMobileMenu}>
                            {child.name}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              )
            })}
          </ul>

          <div className="mobile-auth">
            {user ? (
              <button className="btn btn-outline mobile-auth__logout" onClick={handleLogout}>
                خروج از حساب کاربری
              </button>
            ) : (
              <Link to="/login" className="btn btn-primary" onClick={closeMobileMenu}>
                ورود / ثبت‌نام
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
