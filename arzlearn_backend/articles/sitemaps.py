from django.contrib.sitemaps import Sitemap
from .models import Article, Category


class ArticleSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Article.objects.filter(status='published').order_by('-published_at')

    def lastmod(self, article):
        return article.updated_at

    def location(self, article):
        return f'/article/{article.slug}'


class CategorySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, category):
        return f'/category/{category.slug}'


class StaticViewSitemap(Sitemap):
    """صفحات ثابت سایت (صفحه اصلی، ورود، ثبت‌نام، درباره ما)."""

    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return ['home', 'login', 'register', 'about']

    def location(self, item):
        base = settings.FRONTEND_BASE_URL.rstrip('/')
        paths = {'home': '/', 'login': '/login', 'register': '/register', 'about': '/about'}
        return f'{base}{paths[item]}'


class PriceSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return ['bitcoin', 'ethereum', 'solana', 'dollar', 'gold']

    def location(self, slug):
        return f'/price/{slug}'
