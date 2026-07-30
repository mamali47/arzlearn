import { Outlet } from 'react-router-dom'
import TopBannerSlot from './TopBannerSlot'
import Header from './Header'
import Footer from './Footer'

export default function Layout() {
  return (
    <>
      <TopBannerSlot />
      <Header />
      <main>
        <Outlet />
      </main>
      <Footer />
    </>
  )
}
