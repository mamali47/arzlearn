import type { ArticleDetail, ArticleFAQ, ArticleListItem } from '../api/types'

export const SITE_NAME = 'ارزلرن'

/**
 * آدرس عمومی سایت.
 *
 * چرا ثابت و نه window.location.origin؟ چون اگر سایت از طریق دامنه‌ی دوم،
 * زیر‌دامنه‌ی تست یا www باز شود، canonical و JSON-LD باید همچنان به دامنه‌ی
 * اصلی اشاره کنند؛ وگرنه گوگل دو نسخه‌ی موازی از سایت می‌بیند و اعتبار
 * صفحات بین آنها تقسیم می‌شود.
 */
export const SITE_URL = (
  import.meta.env.VITE_SITE_URL || 'https://arzlearn.ir'
).replace(/\/$/, '')

/** مسیر فارسی را percent-encode می‌کند تا URL معتبر باشد. */
export function encodePath(path: string): string {
  if (!path) return '/'
  const withSlash = path.startsWith('/') ? path : `/${path}`
  return withSlash
    .split('/')
    .map((segment) => encodeURIComponent(decodeURIComponent(segment)))
    .join('/')
}

export function absoluteUrl(pathOrUrl: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl
  return `${SITE_URL}${encodePath(pathOrUrl)}`
}

/** آدرس canonical: بدون query، بدون hash، بدون اسلش اضافه‌ی انتهایی. */
export function canonicalOf(href: string): string {
  try {
    const parsed = new URL(href)
    let path = parsed.pathname || '/'
    if (path.length > 1 && path.endsWith('/')) path = path.replace(/\/+$/, '')
    return `${SITE_URL}${encodePath(path)}`
  } catch {
    return SITE_URL
  }
}

/** کوتاه کردن متن روی مرز کلمه برای متا دیسکریپشن (حد استاندارد ~۱۶۰ کاراکتر). */
export function clampDescription(text: string, limit = 160): string {
  const clean = text.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
  if (clean.length <= limit) return clean
  return `${clean.slice(0, limit).replace(/[\s،,]+\S*$/, '')}…`
}

export function buildOrganizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${SITE_URL}/#organization`,
    name: SITE_NAME,
    alternateName: 'Arzlearn',
    url: `${SITE_URL}/`,
    logo: { '@type': 'ImageObject', url: `${SITE_URL}/logo.png` },
  }
}

export function buildWebsiteSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${SITE_URL}/#website`,
    name: SITE_NAME,
    url: `${SITE_URL}/`,
    inLanguage: 'fa-IR',
    publisher: { '@id': `${SITE_URL}/#organization` },
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${SITE_URL}/search?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  }
}

export function buildBreadcrumbSchema(items: { label: string; path: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.label,
      item: absoluteUrl(item.path),
    })),
  }
}

/** فهرست مقالات یک صفحه؛ به گوگل می‌فهماند این صفحه یک صفحه‌ی لیست است. */
export function buildItemListSchema(articles: ArticleListItem[], name: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name,
    itemListElement: articles.map((article, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      url: absoluteUrl(`/article/${article.slug}`),
      name: article.title,
    })),
  }
}

export function buildArticleSchema(article: ArticleDetail) {
  return {
    '@context': 'https://schema.org',
    '@type': 'NewsArticle',
    headline: article.title.slice(0, 110),
    description: clampDescription(article.summary),
    image: article.image ? [absoluteUrl(article.image)] : undefined,
    datePublished: article.published_at,
    dateModified: article.published_at,
    inLanguage: 'fa-IR',
    articleSection: article.category?.name,
    author: {
      '@type': 'Organization',
      name: article.author_username || SITE_NAME,
      url: `${SITE_URL}/about`,
    },
    publisher: { '@id': `${SITE_URL}/#organization` },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': absoluteUrl(`/article/${article.slug}`),
    },
  }
}

export function buildFAQSchema(faqs: ArticleFAQ[]) {
  if (faqs.length === 0) return null

  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim(),
      },
    })),
  }
}
