import { useEffect, useRef } from 'react'
import './AdSlot.css'

interface AdSlotProps {
  /** شناسه‌ی یکتای این جایگاه تبلیغ، مثلاً "home-hero" یا "article-inline-1" */
  slotId: string
  /** کلاس اضافه‌ی اختیاری برای تنظیم فاصله/اندازه در محل استفاده */
  className?: string
}

/**
 * جایگاه تبلیغ (Ad Slot) - آماده برای اتصال به یکتانت یا هر شبکه‌ی
 * تبلیغاتی مشابه، بدون نیاز به تغییر کد صفحاتی که ازش استفاده می‌کنن.
 *
 * وضعیت فعلی: چون هنوز از یکتانت تاییدیه نگرفتیم، این کامپوننت هیچ‌چیزی
 * رندر نمی‌کنه (بدون فضای خالی اضافه تو صفحه). وقتی تبلیغ فعال شد، کافیه:
 *
 *   ۱. توی فایل .env فرانت‌اند این خط رو اضافه/تغییر بده:
 *        VITE_ADS_ENABLED=true
 *
 *   ۲. کد اسکریپت واقعی یکتانت (که بعد از تایید بهت می‌دن) رو دقیقاً توی
 *      همین فایل، داخل useEffect زیر (جایی که نوشته «اینجا» رو پیدا کن)
 *      جایگزین کن. چون این یک کامپوننت مشترکه، همین یک تغییر برای همه‌ی
 *      جایگاه‌های تبلیغ تو کل سایت کافیه.
 *
 * جاهایی که الان این کامپوننت استفاده شده (برای دیدن سریع، سرچ کن AdSlot):
 *   - صفحه اصلی: زیر آخرین اخبار
 *   - صفحه مقاله: بین بدنه‌ی مقاله و مطالب مشابه
 */
const ADS_ENABLED = import.meta.env.VITE_ADS_ENABLED === 'true'

export default function AdSlot({ slotId, className }: AdSlotProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ADS_ENABLED || !containerRef.current) return

    // ⬇️ اینجا کد اسکریپت واقعی یکتانت رو جایگزین کن، مثلاً چیزی شبیه:
    //
    // const script = document.createElement('script')
    // script.src = 'https://cdn.yektanet.com/.../ad.js'
    // script.async = true
    // script.setAttribute('data-yn-slot', slotId)
    // containerRef.current.appendChild(script)
    //
    // return () => {
    //   script.remove()
    // }
  }, [slotId])

  if (!ADS_ENABLED) return null

  return (
    <div
      ref={containerRef}
      id={`ad-slot-${slotId}`}
      className={`ad-slot ${className ?? ''}`}
      data-ad-slot={slotId}
    >
      <span className="ad-slot__label">تبلیغات</span>
    </div>
  )
}
