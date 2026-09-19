import { useEffect, useState } from 'react'
import { fetchActiveTopBanner } from '../api/endpoints'
import type { TopBanner } from '../api/types'
import './TopBannerSlot.css'

/**
 * بنر بالای سایت.
 *
 * ارتفاع نوار از همان لحظه‌ی اول (قبل از لود شدن تصویر) با CSS رزرو می‌شود
 * و تصویر با width/height واقعی رندر می‌شود؛ یعنی هیچ «پرش» چیدمانی
 * (Cumulative Layout Shift) اتفاق نمی‌افتد. CLS یکی از سه فاکتور
 * Core Web Vitals گوگل است و مستقیم روی رتبه اثر دارد.
 *
 * نسخه‌ی موبایل تصویرِ جداگانه‌ای است که سرور با نسبتِ بلندترِ مخصوص گوشی
 * ساخته، نه همان تصویر دسکتاپِ کوچک‌شده. به همین دلیل متن بنر روی موبایل
 * چند برابر بزرگ‌تر و خواناتر دیده می‌شود.
 */
export default function TopBannerSlot() {
  const [banner, setBanner] = useState<TopBanner | null>(null)

  useEffect(() => {
    let cancelled = false
    fetchActiveTopBanner()
      .then((data) => !cancelled && setBanner(data))
      .catch(() => !cancelled && setBanner(null))
    return () => {
      cancelled = true
    }
  }, [])

  if (!banner) return null

  const desktopSrc = banner.desktop?.jpeg ?? banner.image ?? null
  const mobileSrc = banner.mobile?.jpeg ?? banner.image_mobile ?? desktopSrc
  if (!desktopSrc) return null

  const style = {
    '--top-banner-h-desktop': `${banner.display_height_desktop ?? 92}px`,
    '--top-banner-h-mobile': `${banner.display_height_mobile ?? 104}px`,
    '--top-banner-bg': banner.background_color || 'transparent',
    '--top-banner-fit': banner.fit_mode === 'contain' ? 'contain' : 'cover',
  } as React.CSSProperties

  return (
    <aside className="top-banner-slot" style={style} aria-label="تبلیغ">
      <a
        className="top-banner-slot__link"
        href={banner.link_url}
        target="_blank"
        rel="noopener noreferrer sponsored"
      >
        <picture>
          {banner.mobile?.webp && (
            <source media="(max-width: 768px)" type="image/webp" srcSet={banner.mobile.webp} />
          )}
          {mobileSrc && <source media="(max-width: 768px)" srcSet={mobileSrc} />}
          {banner.desktop?.webp && <source type="image/webp" srcSet={banner.desktop.webp} />}
          <img
            className="top-banner-slot__img"
            src={desktopSrc}
            width={banner.desktop?.width || undefined}
            height={banner.desktop?.height || undefined}
            alt={banner.alt_text || 'بنر تبلیغاتی ارزلرن'}
            decoding="async"
            fetchPriority="high"
          />
        </picture>
      </a>
    </aside>
  )
}
