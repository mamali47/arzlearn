import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'

// Code splitting: صفحات کم‌تکرارتر lazy لود می‌شوند تا حجم بسته‌ی اولیه
// (initial bundle) کوچک‌تر بماند و سرعت بارگذاری اول سایت بهتر شود (فاکتور سئو).
const CategoryPage = lazy(() => import('./pages/CategoryPage'))
const ArticlePage = lazy(() => import('./pages/ArticlePage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const SearchPage = lazy(() => import('./pages/SearchPage'))
const EconomicCalendarPage = lazy(() => import('./pages/EconomicCalendarPage'))
const PricePage = lazy(() => import('./pages/PricePage'))
const AboutPage = lazy(() => import('./pages/AboutPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))

function PageFallback() {
  return <p className="page-loading">در حال بارگذاری...</p>
}

export default function App() {
  return (
    <Suspense fallback={<PageFallback />}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/category/:slug" element={<CategoryPage />} />
          <Route path="/article/:slug" element={<ArticlePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/economic-calendar" element={<EconomicCalendarPage />} />
          <Route path="/price/:slug" element={<PricePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </Suspense>
  )
}
