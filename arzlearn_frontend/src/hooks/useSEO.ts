import { useEffect } from 'react'

interface SEOOptions {
  title?: string
  description?: string
  image?: string
  url?: string
  structuredData?: object | object[]
}

const SITE_NAME = 'ارزلرن'
const DEFAULT_TITLE = 'ارزلرن | اخبار، تحلیل و قیمت لحظه‌ای ارزهای دیجیتال'
const DEFAULT_DESCRIPTION = 'مرجع اخبار، تحلیل و قیمت لحظه‌ای ارزهای دیجیتال و طلا'

function setMetaTag(attr: 'name' | 'property', key: string, content: string) {
  let el = document.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function setCanonical(url: string) {
  let link = document.querySelector('link[rel="canonical"]')
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  link.setAttribute('href', url)
}

/**
 * مدیریت تایتل، متا تگ‌ها (description/OG)، canonical، و داده‌های ساختاریافته
 * (JSON-LD) هر صفحه. چون این یک SPA بدون رندر سمت سرور است، این روش بهترین
 * تلاش ممکن برای سئوی سمت کلاینت است؛ برای سئوی کامل‌تر در آینده می‌توان
 * به سمت SSR/Prerendering (مثل Next.js) مهاجرت کرد.
 */
export function useSEO({ title, description, image, url, structuredData }: SEOOptions) {
  useEffect(() => {
    const finalTitle = title ? `${title} | ${SITE_NAME}` : DEFAULT_TITLE
    const finalDescription = description || DEFAULT_DESCRIPTION
    const finalUrl = url || window.location.href

    document.title = finalTitle
    setMetaTag('name', 'description', finalDescription)
    setMetaTag('property', 'og:title', finalTitle)
    setMetaTag('property', 'og:description', finalDescription)
    setMetaTag('property', 'og:type', 'website')
    setMetaTag('property', 'og:url', finalUrl)
    setMetaTag('property', 'og:site_name', SITE_NAME)
    if (image) setMetaTag('property', 'og:image', image)
    setCanonical(finalUrl)

    const injectedScripts: HTMLScriptElement[] = []
    if (structuredData) {
      const items = Array.isArray(structuredData) ? structuredData : [structuredData]
      items.forEach((item) => {
        const script = document.createElement('script')
        script.type = 'application/ld+json'
        script.textContent = JSON.stringify(item)
        document.head.appendChild(script)
        injectedScripts.push(script)
      })
    }

    return () => {
      injectedScripts.forEach((script) => script.remove())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [title, description, image, url, JSON.stringify(structuredData)])
}
