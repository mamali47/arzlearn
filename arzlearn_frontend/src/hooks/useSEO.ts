import { useEffect } from 'react'
import { SITE_NAME, SITE_URL, absoluteUrl, canonicalOf, clampDescription } from '../utils/seo'

interface SEOOptions {
  title?: string
  description?: string
  image?: string
  /** مسیر داخلی صفحه، مثل '/about'. اگر ندهی از آدرس فعلی استفاده می‌شود. */
  url?: string
  /** 'website' برای صفحات معمولی، 'article' برای صفحه مقاله */
  type?: 'website' | 'article'
  /** صفحاتی مثل ورود/جستجو نباید ایندکس شوند */
  noindex?: boolean
  publishedTime?: string
  modifiedTime?: string
  structuredData?: object | object[]
}

const DEFAULT_TITLE = 'ارزلرن | اخبار، تحلیل و قیمت لحظه‌ای ارزهای دیجیتال، دلار و طلا'
const DEFAULT_DESCRIPTION =
  'مرجع اخبار، تحلیل و قیمت لحظه‌ای بیت‌کوین، اتریوم، سولانا، دلار و طلا؛ همراه با معرفی صرافی‌ها، تقویم اقتصادی و آموزش‌های کاربردی بازار.'
const DEFAULT_IMAGE = `${SITE_URL}/logo.png`

// تگ‌هایی که این هوک مدیریت می‌کند با این صفت علامت می‌خورند تا موقع رفتن به
// صفحه‌ی بعد پاک شوند. بدون این کار، متاتگ‌های صفحه‌ی قبلی روی صفحه‌ی جدید
// می‌مانند و ربات‌های سوشیال اطلاعات اشتباه می‌گیرند.
const MANAGED = 'data-seo-managed'

function setMeta(attr: 'name' | 'property', key: string, content: string | undefined) {
  const selector = `meta[${attr}="${key}"]`
  const existing = document.head.querySelector<HTMLMetaElement>(selector)

  if (!content) {
    if (existing?.hasAttribute(MANAGED)) existing.remove()
    return
  }

  const el = existing ?? document.createElement('meta')
  if (!existing) {
    el.setAttribute(attr, key)
    el.setAttribute(MANAGED, '')
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function setLink(rel: string, href: string) {
  let el = document.head.querySelector<HTMLLinkElement>(`link[rel="${rel}"]`)
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', rel)
    el.setAttribute(MANAGED, '')
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

/**
 * مدیریت تایتل، متاتگ‌ها، canonical و JSON-LD هر صفحه.
 *
 * نکته: این کار «سئوی سمت کلاینت» است و فقط برای خزنده‌هایی کار می‌کند که
 * جاوااسکریپت اجرا می‌کنند. نسخه‌ی اصلی و قابل‌اتکا، همان HTML ایستایی است
 * که دستور `python manage.py generate_static_pages` در سمت بک‌اند می‌سازد.
 * این هوک آن را تکمیل می‌کند (مثلاً برای جستجوی زنده یا تغییر مسیر بدون رفرش).
 */
export function useSEO({
  title,
  description,
  image,
  url,
  type = 'website',
  noindex = false,
  publishedTime,
  modifiedTime,
  structuredData,
}: SEOOptions) {
  useEffect(() => {
    const finalTitle = title ? `${title} | ${SITE_NAME}` : DEFAULT_TITLE
    const finalDescription = clampDescription(description || DEFAULT_DESCRIPTION)
    // canonical همیشه بدون query string و بدون hash؛ وگرنه /search?q=x و
    // /search?q=y دو صفحه‌ی جدا حساب می‌شوند و محتوای تکراری می‌سازند.
    const canonical = url ? absoluteUrl(url) : canonicalOf(window.location.href)
    const finalImage = image ? absoluteUrl(image) : DEFAULT_IMAGE

    document.title = finalTitle
    document.documentElement.lang = 'fa'

    setMeta('name', 'description', finalDescription)
    setMeta(
      'name',
      'robots',
      noindex
        ? 'noindex, follow'
        : 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1'
    )

    setMeta('property', 'og:title', finalTitle)
    setMeta('property', 'og:description', finalDescription)
    setMeta('property', 'og:type', type)
    setMeta('property', 'og:url', canonical)
    setMeta('property', 'og:site_name', SITE_NAME)
    setMeta('property', 'og:locale', 'fa_IR')
    setMeta('property', 'og:image', finalImage)
    setMeta('property', 'article:published_time', type === 'article' ? publishedTime : undefined)
    setMeta('property', 'article:modified_time', type === 'article' ? modifiedTime : undefined)

    setMeta('name', 'twitter:card', 'summary_large_image')
    setMeta('name', 'twitter:title', finalTitle)
    setMeta('name', 'twitter:description', finalDescription)
    setMeta('name', 'twitter:image', finalImage)

    setLink('canonical', canonical)

    const injected: HTMLScriptElement[] = []
    if (structuredData) {
      const items = (Array.isArray(structuredData) ? structuredData : [structuredData]).filter(
        Boolean
      )
      items.forEach((item) => {
        const script = document.createElement('script')
        script.type = 'application/ld+json'
        // جلوگیری از فرار از تگ اسکریپت اگر عنوان مقاله کاراکتر < داشته باشد
        script.textContent = JSON.stringify(item).replace(/</g, '\\u003C')
        document.head.appendChild(script)
        injected.push(script)
      })
    }

    return () => {
      injected.forEach((script) => script.remove())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    title,
    description,
    image,
    url,
    type,
    noindex,
    publishedTime,
    modifiedTime,
    JSON.stringify(structuredData),
  ])
}
