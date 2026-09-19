import { Outlet } from 'react-router-dom'
import TopBannerSlot from './TopBannerSlot'
import Header from './Header'
import Footer from './Footer'

export default function Layout() {
  return (
    <>
      {/*
        لینک «پرش به محتوا»: فقط وقتی با Tab روی آن بروی دیده می‌شود.
        هم برای کاربران کیبورد/اسکرین‌ریدر لازم است، هم Lighthouse در بخش
        Accessibility امتیازش را حساب می‌کند.
      */}
      <a href="#main-content" className="skip-link">
        رفتن به محتوای اصلی
      </a>
      <TopBannerSlot />
      <Header />
      <main id="main-content">
        <Outlet />
      </main>
      <Footer />
    </>
  )
}
