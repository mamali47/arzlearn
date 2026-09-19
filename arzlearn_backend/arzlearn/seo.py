"""
توابع کمکی مشترک سئو (URL، متا دیسکریپشن، JSON-LD امن).

چرا این فایل لازم بود؟
----------------------
۱) اسلاگ‌های سایت فارسی هستند (allow_unicode=True). اگر آدرس فارسی را خام
   داخل <link rel="canonical"> یا sitemap.xml بگذاریم، خروجی طبق استاندارد
   RFC 3986 معتبر نیست. گوگل معمولاً خودش نرمال‌سازی می‌کند ولی در این حالت
   ممکن است canonical با آدرسی که کرال کرده «یکی» حساب نشود و ارزش صفحه
   تقسیم شود. راه‌حل درست: percent-encode کردن مسیر (نه دامنه).

۲) JSON-LD را نباید با |safe و بدون escape داخل <script> ریخت؛ اگر تایتل یا
   خلاصه‌ی یک مقاله رشته‌ی </script> داشته باشد، هم صفحه می‌شکند و هم یک
   حفره‌ی XSS باز می‌شود.
"""

import json
import re
from urllib.parse import quote, urlsplit, urlunsplit

from django.conf import settings
from django.utils.html import strip_tags


def site_url() -> str:
    """آدرس عمومی سایت، بدون اسلش انتهایی."""
    return (getattr(settings, 'SITE_URL', 'https://arzlearn.ir') or '').rstrip('/')


def encode_path(path: str) -> str:
    """
    مسیر فارسی را به شکل percent-encoded برمی‌گرداند.

    مثال: '/article/تحلیل-بیت-کوین' -> '/article/%D8%AA%D8%AD%D9%84%DB%8C%D9%84-...'
    کاراکترهای ساختاری URL (/ ? = & #) دست‌نخورده می‌مانند.
    """
    if not path:
        return '/'
    if not path.startswith('/'):
        path = '/' + path
    return quote(path, safe='/-_.~!$&\'()*+,;=:@?#%')


def absolute_url(path: str) -> str:
    """آدرس کامل و encode‌شده‌ی یک مسیر داخلی."""
    return f'{site_url()}{encode_path(path)}'


def canonical_of(url: str) -> str:
    """
    نسخه‌ی canonical یک آدرس کامل: بدون query string، بدون fragment و بدون
    اسلش اضافه‌ی انتهایی (به‌جز خود صفحه‌ی اصلی).
    """
    parts = urlsplit(url)
    path = parts.path or '/'
    if len(path) > 1 and path.endswith('/'):
        path = path.rstrip('/')
    return urlunsplit((parts.scheme, parts.netloc, encode_path(path), '', ''))


def meta_description(text: str, limit: int = 160) -> str:
    """
    متن را برای متا دیسکریپشن تمیز می‌کند: حذف تگ‌های HTML، یکی کردن
    فاصله‌ها و کوتاه کردن روی مرز کلمه (نه وسط کلمه).
    """
    if not text:
        return ''
    clean = re.sub(r'\s+', ' ', strip_tags(text)).strip()
    if len(clean) <= limit:
        return clean
    cut = clean[:limit].rsplit(' ', 1)[0]
    return f'{cut.rstrip("،, ")}…'


def json_ld(data) -> str:
    """
    JSON-LD امن برای قرار گرفتن داخل <script type="application/ld+json">.

    کاراکترهای < > & به معادل یونیکدشان تبدیل می‌شوند تا هیچ محتوایی نتواند
    از تگ اسکریپت فرار کند. این دقیقاً همان کاری است که خود جنگو در
    json_script انجام می‌دهد.
    """
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return (
        raw.replace('<', '\\u003C')
        .replace('>', '\\u003E')
        .replace('&', '\\u0026')
    )


def organization_schema() -> dict:
    base = site_url()
    return {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        '@id': f'{base}/#organization',
        'name': 'ارزلرن',
        'alternateName': 'Arzlearn',
        'url': f'{base}/',
        'logo': {'@type': 'ImageObject', 'url': f'{base}/logo.png'},
        'description': 'مجله تخصصی بازارهای مالی: اخبار، تحلیل و قیمت لحظه‌ای ارز دیجیتال، دلار و طلا.',
    }


def website_schema() -> dict:
    base = site_url()
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': f'{base}/#website',
        'name': 'ارزلرن',
        'url': f'{base}/',
        'inLanguage': 'fa-IR',
        'publisher': {'@id': f'{base}/#organization'},
        'potentialAction': {
            '@type': 'SearchAction',
            'target': {
                '@type': 'EntryPoint',
                'urlTemplate': f'{base}/search?q={{search_term_string}}',
            },
            'query-input': 'required name=search_term_string',
        },
    }


def breadcrumb_schema(items) -> dict:
    """items: لیستی از (نام، مسیر داخلی)."""
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': index + 1,
                'name': name,
                'item': absolute_url(path),
            }
            for index, (name, path) in enumerate(items)
        ],
    }


def item_list_schema(articles, name: str) -> dict:
    """
    فهرست مقالات یک صفحه (صفحه اصلی / دسته‌بندی) به‌صورت ItemList.
    به گوگل کمک می‌کند بفهمد این صفحه یک صفحه‌ی فهرست است نه یک مقاله.
    """
    return {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': name,
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': index + 1,
                'url': absolute_url(f'/article/{article.slug}'),
                'name': article.title,
            }
            for index, article in enumerate(articles)
        ],
    }
