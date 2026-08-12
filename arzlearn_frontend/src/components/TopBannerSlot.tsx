import { useEffect, useState } from 'react'
import { fetchActiveTopBanner } from '../api/endpoints'
import type { TopBanner } from '../api/types'
import './TopBannerSlot.css'

export default function TopBannerSlot() {
  const [banner, setBanner] = useState<TopBanner | null>(null)

  useEffect(() => {
    fetchActiveTopBanner()
      .then(setBanner)
      .catch(() => setBanner(null))
  }, [])

  if (!banner || !banner.image) return null

  return (
    
      href={banner.link_url}
      target="_blank"
      rel="noopener noreferrer sponsored"
      className="top-banner-slot"
    >
      <picture>
        {banner.image_mobile && (
          <source media="(max-width: 768px)" srcSet={banner.image_mobile} />
        )}
        <img src={banner.image} alt="تبلیغ" />
      </picture>
    </a>
  )
}
