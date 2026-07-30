from django.conf import settings
from django.contrib.sitemaps import Sitemap

from .models import Article, Category


class ArticleSitemap(Sitemap):
    """نقشه‌ی سایت برای صفحات مقالات (اشاره به آدرس فرانت‌اند، نه بک‌اند)."""

    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Article.objects.filter(status='published').order_by('-published_at')

    def lastmod(self, article):
        return article.updated_at

    def location(self, article):
        return f'{settings.FRONTEND_BASE_URL.rstrip("/")}/article/{article.slug}'


class CategorySitemap(Sitemap):
    """نقشه‌ی سایت برای صفحات دسته‌بندی."""

    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, category):
        return f'{settings.FRONTEND_BASE_URL.rstrip("/")}/category/{category.slug}'


class StaticViewSitemap(Sitemap):
    """صفحات ثابت سایت (صفحه اصلی، ورود، ثبت‌نام)."""

    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return ['home', 'login', 'register']

    def location(self, item):
        base = settings.FRONTEND_BASE_URL.rstrip('/')
        paths = {'home': '/', 'login': '/login', 'register': '/register'}
        return f'{base}{paths[item]}'


class PriceSitemap(Sitemap):
    """
    صفحات اختصاصی قیمت لحظه‌ای (قیمت بیت‌کوین، اتریوم، سولانا، دلار، طلا)؛
    این صفحات مخصوص سئو ساخته شده‌اند تا در جستجوی «قیمت بیت‌کوین» و مشابه
    آن دیده شوند و هر روز (به‌خاطر تغییر قیمت) دوباره کراول شوند.
    """

    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return ['bitcoin', 'ethereum', 'solana', 'dollar', 'gold']

    def location(self, slug):
        return f'{settings.FRONTEND_BASE_URL.rstrip("/")}/price/{slug}'
