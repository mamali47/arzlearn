"""
سایت‌مپ‌های ارزلرن.

دو نکته‌ی مهمی که در نسخه‌ی قبلی مشکل‌ساز بود:

۱) اسلاگ‌ها فارسی‌اند. آدرس فارسیِ خام داخل <loc> طبق استاندارد sitemap
   نامعتبر است (باید percent-encoded باشد). بعضی ابزارها آن URLها را رد
   می‌کنند و در Search Console خطای «Invalid URL» می‌دهند.

۲) دامنه از روی هدر درخواست ساخته می‌شد. اگر سایت‌مپ از طریق پروکسی یا با
   دامنه‌ی بک‌اند خوانده شود، آدرس‌های داخلش اشتباه درمی‌آید. حالا دامنه
   همیشه از settings.SITE_URL می‌آید.
"""

from urllib.parse import urlsplit

from django.contrib.sitemaps import Sitemap
from django.utils import timezone

from arzlearn.seo import encode_path, site_url

from .models import Article, Category, Tag


class BaseSitemap(Sitemap):
    """دامنه و پروتکل ثابت + مسیر percent-encoded."""

    protocol = 'https'

    def get_domain(self, site=None):
        return urlsplit(site_url()).netloc

    def _encoded(self, path):
        return encode_path(path)


class ArticleSitemap(BaseSitemap):
    changefreq = 'daily'
    limit = 2000

    def items(self):
        return (
            Article.objects.filter(status='published')
            .select_related('category')
            .order_by('-published_at')
        )

    def lastmod(self, article):
        return article.updated_at

    def priority(self, article):
        # مقالات یک ماه اخیر اولویت بالاتر می‌گیرند تا گوگل سراغشان زودتر برود.
        age = (timezone.now() - article.published_at).days
        return 0.9 if age <= 30 else 0.6

    def location(self, article):
        return self._encoded(f'/article/{article.slug}')


class CategorySitemap(BaseSitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, category):
        latest = (
            Article.objects.filter(
                category_id__in=category.get_self_and_descendant_ids(), status='published'
            )
            .order_by('-updated_at')
            .first()
        )
        return latest.updated_at if latest else None

    def location(self, category):
        return self._encoded(f'/category/{category.slug}')


class TagSitemap(BaseSitemap):
    """
    تگ‌ها فعلاً صفحه‌ی اختصاصی ندارند؛ اگر بعداً مسیر /tag/<slug> اضافه شد،
    کافی است این کلاس را به دیکشنری sitemaps در urls.py اضافه کنی.
    """

    changefreq = 'weekly'
    priority = 0.4

    def items(self):
        return Tag.objects.filter(main_articles__status='published').distinct()

    def location(self, tag):
        return self._encoded(f'/tag/{tag.slug}')


class StaticViewSitemap(BaseSitemap):
    """
    فقط صفحاتی که واقعاً ارزش ایندکس شدن دارند.

    صفحه‌ی ورود و ثبت‌نام عمداً حذف شدند: این صفحات محتوای یکتا ندارند،
    در نتایج جستجو به درد کسی نمی‌خورند و بودنشان در ایندکس فقط نسبت
    «صفحات بی‌کیفیت به کل صفحات» دامنه را بدتر می‌کند.
    """

    def items(self):
        return [
            ('/', 1.0, 'hourly'),
            ('/about', 0.5, 'monthly'),
            ('/economic-calendar', 0.7, 'daily'),
        ]

    def location(self, item):
        return self._encoded(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]


class PriceSitemap(BaseSitemap):
    changefreq = 'hourly'
    priority = 0.8

    def items(self):
        return ['bitcoin', 'ethereum', 'solana', 'bnb', 'hype', 'xaut', 'dollar', 'gold']

    def location(self, slug):
        return self._encoded(f'/price/{slug}')
