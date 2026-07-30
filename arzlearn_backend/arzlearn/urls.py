"""
آدرس‌دهی اصلی پروژه.
"""

import os

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from articles.sitemaps import ArticleSitemap, CategorySitemap, PriceSitemap, StaticViewSitemap

sitemaps = {
    'articles': ArticleSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
    'prices': PriceSitemap,
}

# آدرس پنل ادمین از .env خوانده می‌شود؛ برای پروداکشن به یک مسیر غیرقابل‌حدس تغییر بده.
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

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
