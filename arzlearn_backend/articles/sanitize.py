"""
پاک‌سازی HTML خروجی CKEditor قبل از ذخیره در دیتابیس.

چرا لازم است؟ محدودیت‌های CKEditor (مثل toolbar محدود) فقط سمت کلاینت
هستند و به‌راحتی قابل دور زدن‌اند (مثلاً با ارسال مستقیم درخواست به API
یا دستکاری request در DevTools). اگر یک حساب ادمین/نویسنده به هر دلیلی
(رمز ضعیف، فیشینگ و...) به خطر بیفتد، بدون این پاک‌سازی، مهاجم می‌تواند
کد جاوااسکریپت مخرب (Stored XSS) را داخل بدنه‌ی مقاله تزریق کند که برای
تمام بازدیدکنندگان سایت اجرا می‌شود (چون فرانت‌اند بدنه‌ی مقاله را با
dangerouslySetInnerHTML رندر می‌کند). این تابع یک لایه‌ی دفاعی سمت سرور
است که مستقل از فرانت‌اند، فقط تگ‌ها/attributeهای امن را نگه می‌دارد.
"""

import bleach
from bs4 import BeautifulSoup
from django.conf import settings

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'a',
    'ul', 'ol', 'li', 'blockquote',
    'h2', 'h3', 'h4', 'h5', 'h6',
    'img', 'figure', 'figcaption',
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'span', 'div', 'code', 'pre', 'hr',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
    'span': ['class', 'style'],
    'div': ['class'],
    'table': ['class'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
    '*': ['class'],
}

# فقط این پروتکل‌ها در href/src مجاز هستند (جلوگیری از javascript:‌ و data: مخرب)
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def absolutize_media_urls(html: str) -> str:
    """
    آدرس‌های نسبی عکس‌هایی که از طریق آپلودر CKEditor داخل متن مقاله قرار
    می‌گیرند (مثل «/media/uploads/x.jpg») را به آدرس کامل (شامل دامنه‌ی
    بک‌اند) تبدیل می‌کند.

    چرا لازم است؟ فرانت‌اند (React) روی یک دامنه/پورت جدا از بک‌اند
    (Django) اجرا می‌شود. اگر آدرس عکس نسبی باشد، مرورگر آن را نسبت به
    دامنه‌ی فرانت‌اند حل می‌کند (نه بک‌اند)، که چنین مسیری روی فرانت‌اند
    اصلاً وجود ندارد و عکس لود نمی‌شود. تصویر اصلی مقاله همین مشکل را
    نداشت چون سریالایزرش صراحتاً از request.build_absolute_uri() استفاده
    می‌کند؛ عکس‌های داخل متن (که مستقیماً توسط CKEditor درج می‌شوند) این
    مرحله را نداشتند.
    """
    if not html or 'src="/' not in html:
        return html

    soup = BeautifulSoup(html, 'html.parser')
    backend_url = settings.BACKEND_BASE_URL.rstrip('/')

    for img in soup.find_all('img', src=True):
        if img['src'].startswith('/'):
            img['src'] = f'{backend_url}{img["src"]}'

    return str(soup)


def open_links_in_new_tab(html: str) -> str:
    """
    تمام لینک‌های داخل متن مقاله را طوری تنظیم می‌کند که در تب جدید باز
    شوند (target="_blank")، صرف‌نظر از اینکه CKEditor موقع ساخت لینک این
    مقدار را تنظیم کرده باشد یا نه. rel="noopener noreferrer" هم برای
    امنیت (جلوگیری از دسترسی صفحه‌ی مقصد به window.opener) اضافه می‌شود.
    """
    if not html or '<a ' not in html:
        return html

    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a', href=True):
        link['target'] = '_blank'
        link['rel'] = 'noopener noreferrer'

    return str(soup)


def sanitize_article_html(html: str) -> str:
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    cleaned = absolutize_media_urls(cleaned)
    cleaned = open_links_in_new_tab(cleaned)
    return cleaned
