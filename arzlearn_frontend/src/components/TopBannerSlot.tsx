import { useEffect, useState } from 'react'
import { fetchActiveTopBanner } from '../api/endpoints'
import type { TopBanner } from '../api/types'
import './TopBannerSlot.css'

/**
 * بنر بالای هدر (بالاترین قسمت سایت). فقط وقتی یک بنر «فعال» از ادمین
 * جنگو (/admin/topbanner/topbanner/) تنظیم شده باشد نمایش داده می‌شود؛
 * در غیر این صورت این کامپوننت هیچ‌چیزی رندر نمی‌کند (بدون فضای خالی اضافه).
 */
export default function TopBannerSlot() {
  const [banner, setBanner] = useState<TopBanner | null>(null)

  useEffect(() => {
    fetchActiveTopBanner()
      .then(setBanner)
      .catch(() => setBanner(null))
  }, [])

  if (!banner || !banner.image) return null

  return (
    <a
      href={banner.link_url}
      target="_blank"
      rel="noopener noreferrer sponsored"
      className="top-banner-slot"
    >
      <img src={banner.image} alt="تبلیغ" />
    </a>
  )
}
