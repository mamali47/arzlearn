"""
آدرس‌دهی اصلی پروژه.
"""

import os

from django.contrib import admin
from django.contrib.sitemaps.views import index as sitemap_index, sitemap
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import include, path
from django.views.decorators.cache import cache_page

from articles.feeds import ArticleFeed
from articles.sitemaps import (
    ArticleSitemap,
    CategorySitemap,
    PriceSitemap,
    StaticViewSitemap,
)
from arzlearn.seo import site_url

sitemaps = {
    'static': StaticViewSitemap,
    'articles': ArticleSitemap,
    'categories': CategorySitemap,
    'prices': PriceSitemap,
}


def robots_txt(request):
    """
    robots.txt پویا.

    مسیرهایی که محتوای یکتا ندارند (جستجو، صفحات حساب کاربری) بسته می‌شوند
    تا بودجه‌ی خزش (crawl budget) گوگل صرف مقالات شود، نه صفحات بی‌ارزش.
    """
    base = site_url()
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /search',
        'Disallow: /login',
        'Disallow: /register',
        'Disallow: /forgot-password',
        'Disallow: /reset-password',
        'Disallow: /verify-email',
        'Disallow: /check-email',
        'Disallow: /api/',
        'Disallow: /*?q=',
        '',
        '# ربات‌های هوش مصنوعیِ اسکرپر که ترافیک سنگین می‌سازند',
        'User-agent: GPTBot',
        'Crawl-delay: 10',
        '',
        f'Sitemap: {base}/sitemap.xml',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


# آدرس پنل ادمین از .env خوانده می‌شود؛ برای پروداکشن به یک مسیر غیرقابل‌حدس تغییر بده.
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # سایت‌مپ به‌صورت index + بخش‌های جداگانه. مزیت: وقتی تعداد مقالات زیاد
    # شود گوگل مجبور نیست یک فایل غول‌پیکر بخواند و در Search Console هم
    # می‌فهمی دقیقاً کدام بخش مشکل دارد.
    path('sitemap.xml', cache_page(60 * 60)(sitemap_index),
         {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemap-section'}, name='sitemap-index'),
    path('sitemap-<section>.xml', cache_page(60 * 60)(sitemap),
         {'sitemaps': sitemaps}, name='sitemap-section'),

    path('robots.txt', robots_txt, name='robots'),
    path('rss.xml', cache_page(60 * 15)(ArticleFeed()), name='rss'),

    path('api/accounts/', include('accounts.urls')),
    path('api/articles/', include('articles.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/prices/', include('prices.urls')),
    path('api/socials/', include('socials.urls')),
    path('api/exchanges/', include('exchanges.urls')),
    path('api/economic-calendar/', include('economic_calendar.urls')),
    path('api/topbanner/', include('topbanner.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
